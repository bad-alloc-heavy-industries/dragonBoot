// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <cstring>
#include <usb/core.hxx>
#include <substrate/indexed_iterator>
#include <substrate/index_sequence>
#include "platform.hxx"
#include "stm32f1.hxx"

constexpr uint32_t applicationBaseAddr{0x08002000U};
constexpr uint32_t flashEndAddr{0x08020000U};

const std::array<usb::dfu::zone_t, 1> firmwareZone
{{
	{
		applicationBaseAddr,
		flashEndAddr
	}
}};

std::array<char16_t, serialLength> serialNumber{{}};

#if BOOTLOADER_TARGET != BMP
// The linker script pins this to 0x20001000
[[gnu::section(".bootMagic")]] static uint16_t bootMagic;

constexpr static uint16_t bootMagicDFU{0xBADB};
#endif

namespace osc
{
	void init() noexcept
	{
		// Start by bringing up the HSE (High-speed external) oscillator and wait for it to become ready.
		rcc.clockCtrl |= vals::rcc::clockCtrlHSEEnable;
		while (!(rcc.clockCtrl & vals::rcc::clockCtrlHSEReady))
			continue;
		// Switch to the HSE for the moment
		rcc.clockConfig = (rcc.clockConfig & ~vals::rcc::clockConfigSourceMask) | vals::rcc::clockConfigSourceHSE;
		// Switch off the PLL (just in case), but not the HSI as that's required for FPEC operations
		rcc.clockCtrl &= ~vals::rcc::clockCtrlPLLEnable;
		// Now configure the prescalers
		rcc.clockConfig &= ~(vals::rcc::clockConfigAHBPrescaleMask | vals::rcc::clockConfigAPB1PrescaleMask |
			vals::rcc::clockConfigAPB2PrescaleMask | vals::rcc::clockConfigADCPrescaleMask |
			vals::rcc::clockConfigPLLSourceMask | vals::rcc::clockConfigPLLPrescaleMask |
			vals::rcc::clockConfigPLLMultiplierMask | vals::rcc::clockConfigOutputMask);
		rcc.clockConfig |= vals::rcc::clockConfigAHBPrescale(0) | vals::rcc::clockConfigAPB1Prescale(2) |
			vals::rcc::clockConfigAPB2Prescale(0) | vals::rcc::clockConfigADCPrescale(8) |
			vals::rcc::clockConfigPLLPrescale(0);
		// Now the prescalers are configured, set the Flash wait states appropriately and ready for the PLL'd clock
		flashCtrl.bank[0].accessCtrl &= ~vals::flash::accessCtrlLatencyMask;
		flashCtrl.bank[0].accessCtrl |= vals::flash::acccesCtrlLatency(2);
		// Set up the PLL and wait for it to come up, stabilise, then switch to it.
		rcc.clockConfig |= vals::rcc::clockConfigPLLMultiplier(9) | vals::rcc::clockConfigPLLSourceHSE;
		rcc.clockCtrl |= vals::rcc::clockCtrlPLLEnable;
		while (!(rcc.clockCtrl & vals::rcc::clockCtrlPLLReady))
			continue;
		rcc.clockConfig = (rcc.clockConfig & ~vals::rcc::clockConfigSourceMask) | vals::rcc::clockConfigSourcePLL;
	}
} // namespace osc

void enableInterrupts() noexcept { }
void idle() noexcept { __asm__("wfi"); }

void readSerialNumber() noexcept
{
#if SERIAL_LENGTH == 8
	// Grab the device's unique ID and compute the raw serial number
	const uint32_t uniqueID = deviceInfo.uniqueID[0] + deviceInfo.uniqueID[1] + deviceInfo.uniqueID[2];
	// Convert that into a series of hex encoded characters
	for (auto [i, digit] : substrate::indexedIterator_t{serialNumber})
	{
		digit = [&](const size_t shift)
		{
			auto hexDigit{static_cast<uint16_t>((uniqueID >> shift) & 0x0fU)};
			hexDigit += 0x30U;
			if (hexDigit > 0x39U)
				hexDigit += 7U; // 'A' - '9' == 8, less 1 gives 7.
			return hexDigit;
		}((7U - i) * 4U);
	}
#else
#warning "Unhandled SERIAL_LENGTH"
#endif
}

bool mustEnterBootloader() noexcept
{
#if BOOTLOADER_TARGET == BMP
	rcc.apb2PeriphClockEn |= vals::rcc::apb2PeriphClockEnGPIOPortB;
	// Delay a little after powering up the GPIO controller to allow the pin value to stabilise
	for ([[maybe_unused]] volatile size_t i : substrate::indexSequence_t{10})
		continue;
	// If PB12 is low, then either the button is pressed, or the firmware set it low
	if (!vals::gpio::value(gpioB, vals::gpio_t::pin12))
		return true;
#else
	if (!(rcc.ctrlStatus & vals::rcc::ctrlStatusResetCausePOR) && bootMagic == bootMagicDFU)
		return true;
	bootMagic = 0;
#endif
	rcc.ctrlStatus |= vals::rcc::ctrlStatusClearResetCause;
	uint32_t stackPointer{};
	static_assert(sizeof(uint32_t) == 4);
	// NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
	std::memcpy(&stackPointer, reinterpret_cast<const void *>(applicationBaseAddr), sizeof(uint32_t));
	return stackPointer == 0xFFFFFFFFU;
}

void rebootToFirmware() noexcept
{
	// Disable the currently enabled interrupts
	nvic.disableInterrupt(vals::irqs::usbLowPriority);
	// Set the vector table to the application's
	scb.vtable = applicationBaseAddr;
	__asm__(R"(
		ldr		r1, [%[baseAddr]]    // Read out the stack pointer
		msr		msp, r1              // Stuff it into the main stack pointer special register
		ldr		pc, [%[baseAddr], 4] // Hop into the firmware (fake reboot)
		)" : : [baseAddr] "l" (applicationBaseAddr) : "r1"
	);
	while (true)
		continue;
}

namespace usb::dfu
{
	static size_t flashBank{};

	void reboot() noexcept
	{
		flashCtrl.bank[0].control |= vals::flash::controlLock;
		flashCtrl.bank[1].control |= vals::flash::controlLock;
		// Reset the boot magic, and ask the system controller to reboot the device.
#if BOOTLOADER_TARGET == BMP
		vals::gpio::config<vals::gpio_t::pin12>(gpioB, vals::gpio::mode_t::input, vals::gpio::config_t::inputFloating);
		vals::gpio::set(gpioB, vals::gpio_t::pin12);
#else
		bootMagic = 0;
#endif
		scb.apint = vals::scb::apintKey | vals::scb::apintSystemResetRequest;
		while (true)
			continue;
	}

	bool flashBusy() noexcept
	{
		// Read back the Flash controller status
		const auto status{flashCtrl.bank[flashBank].status};
		// If we don't see EOP set, or the busy bit is still set, Flash is still busy.
		return !(status & vals::flash::statusEndOfOperation) && (status & vals::flash::statusBusy);
	}

	// XXX: Neither this nor the write routine work for bank2, because there are technically
	// 2 Flash controllers and dragonSTM32 currently doesn't deal with that properly.
	void erase(const std::uintptr_t address) noexcept
	{
		flashBank = address < vals::flash::bankSplit ? 0U : 1U;
		// Unlock the Flash controller if necessary
		if (flashCtrl.bank[flashBank].control & vals::flash::controlLock)
		{
			flashCtrl.bank[flashBank].flashKey = vals::flash::unlockKey1;
			flashCtrl.bank[flashBank].flashKey = vals::flash::unlockKey2;
			// Assume that the controller is now unlocked.. not much we can do otherwise!
		}
		// Set up the page erase
		flashCtrl.bank[flashBank].control = vals::flash::controlPageErase;
		flashCtrl.bank[flashBank].address = address;
		// And then trigger the operation
		flashCtrl.bank[flashBank].control |= vals::flash::controlStartErase;
	}

	void write(const std::uintptr_t address, const std::size_t count, const uint8_t *const buffer) noexcept
	{
		if (!count || count > flashBufferSize)
			return;
		flashBank = address < vals::flash::bankSplit ? 0U : 1U;

		// Clear the EOP bit (Write 1 to clear)
		flashCtrl.bank[flashBank].status |= vals::flash::statusEndOfOperation;
		// The controller should already be unlocked because of the erase that occured, so..
		// Set up the programming operation.
		flashCtrl.bank[flashBank].control = vals::flash::controlProgram;
		// The STM32F1 Flash is only able to be written 16 bits at a time, so turn the address too write into
		// a uint16_t pointer, and copy the data in 2 bytes at a time w/ a fixup for the final one.
		for (const auto offset : substrate::indexSequence_t{count}.step(2))
		{
			const auto amount{std::min(count - offset, 2U)};
			uint16_t data = 0xffffU;
			std::memcpy(&data, buffer + offset, amount);
			*reinterpret_cast<volatile uint16_t *>(address + offset) = data;
		}
	}
} // namespace usb::dfu

void irqCANRx0USBLowPriority() noexcept { usb::core::handleIRQ(); }
