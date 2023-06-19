// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <cstring>
#include <usb/core.hxx>
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

// The linker script pins this to 0x20001000
[[gnu::section(".bootMagic")]] static uint16_t bootMagic;

constexpr static uint16_t bootMagicDFU{0xBADB};

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
		// Switch off the HSI and PLL (just in case)
		rcc.clockCtrl &= ~(vals::rcc::clockCtrlHSIEnable | vals::rcc::clockCtrlPLLEnable);
		// Now configure the prescalers
		rcc.clockConfig &= ~(vals::rcc::clockConfigAHBPrescaleMask | vals::rcc::clockConfigAPB1PrescaleMask |
			vals::rcc::clockConfigAPB2PrescaleMask | vals::rcc::clockConfigADCPrescaleMask |
			vals::rcc::clockConfigPLLSourceMask | vals::rcc::clockConfigPLLPrescaleMask |
			vals::rcc::clockConfigPLLMultiplierMask | vals::rcc::clockConfigOutputMask);
		rcc.clockConfig |= vals::rcc::clockConfigAHBPrescale(0) | vals::rcc::clockConfigAPB1Prescale(2) |
			vals::rcc::clockConfigAPB2Prescale(0) | vals::rcc::clockConfigADCPrescale(8) |
			vals::rcc::clockConfigPLLPrescale(0);
		// Now the prescalers are configured, set the Flash wait states appropriately and ready for the PLL'd clock
		flashCtrl.accessCtrl &= ~vals::flash::accessCtrlLatencyMask;
		flashCtrl.accessCtrl |= vals::flash::acccesCtrlLatency(2);
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
}

bool mustEnterBootloader() noexcept
{
	if (!(rcc.ctrlStatus & vals::rcc::ctrlStatusResetCausePOR) && bootMagic == bootMagicDFU)
		return true;
	bootMagic = 0;
	rcc.ctrlStatus |= vals::rcc::ctrlStatusClearResetCause;
	uint32_t stackPointer{};
	static_assert(sizeof(uint32_t) == 4);
	// NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
	std::memcpy(&stackPointer, reinterpret_cast<const void *>(applicationBaseAddr), sizeof(uint32_t));
	return stackPointer == 0xFFFFFFFFU;
}

void rebootToFirmware() noexcept
{
	// Set the vector table to the application's
	scb.vtable = applicationBaseAddr;
	__asm__(R"(
		ldr		r0, =%[baseAddr]
		ldr		r1, [r0]    // Read out the stack pointer
		msr		msp, r1     // Stuff it into the main stack pointer special register
		ldr		pc, [r0, 4] // Hop into the firmware (fake reboot)
		)" : : [baseAddr] "i" (applicationBaseAddr) :
			"r0", "r1"
	);
	while (true)
		continue;
}

namespace usb::dfu
{
	void reboot() noexcept
	{
		// Reset the boot magic, and ask the system controller to reboot the device.
		bootMagic = 0;
		scb.apint = vals::scb::apintKey | vals::scb::apintSystemResetRequest;
		while (true)
			continue;
	}

	bool flashBusy() noexcept
	{
		// Read back the Flash controller status
		const auto status{flashCtrl.status};
		// If we don't see EOP set, or the busy bit is still set, Flash is still busy.
		return !(status & vals::flash::statusEndOfOperation) && (status & vals::flash::statusBusy);
	}

	// XXX: Neither this nor the write routine work for bank2, because there are technically
	// 2 Flash controllers and dragonSTM32 currently doesn't deal with that properly.
	void erase(const std::uintptr_t address) noexcept
	{
		// Unlock the Flash controller if necessary
		if (flashCtrl.control & vals::flash::controlLock)
		{
			flashCtrl.flashKey = vals::flash::unlockKey1;
			flashCtrl.flashKey = vals::flash::unlockKey2;
			// Assume that the controller is now unlocked.. not much we can do otherwise!
		}
		// Set up the page erase
		flashCtrl.control |= vals::flash::controlPageErase;
		flashCtrl.address = address;
		// And then trigger the operation
		flashCtrl.control |= vals::flash::controlStartErase;
	}

	void write(const std::uintptr_t address, const std::size_t count, const uint8_t *const buffer) noexcept
	{
		if (!count || count > flashBufferSize)
			return;

		// Clear the EOP bit (Write 1 to clear)
		flashCtrl.status |= vals::flash::statusEndOfOperation;
		// The controller should already be unlocked because of the erase that occured, so..
		// Set up the programming operation.
		flashCtrl.control |= vals::flash::controlProgram;
		std::memcpy(reinterpret_cast<void *>(address), buffer, count);
	}
} // namespace usb::dfu

void irqCANRx0USBLowPriority() noexcept { usb::core::handleIRQ(); }
