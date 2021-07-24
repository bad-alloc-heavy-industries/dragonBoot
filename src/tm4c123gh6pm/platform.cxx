// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <cstring>
#include <substrate/index_sequence>
#include <tm4c123gh6pm/platform.hxx>
#include <tm4c123gh6pm/constants.hxx>
#include <usb/core.hxx>
#include "platform.hxx"
#include "tm4c123gh6pm.hxx"

constexpr uint32_t applicationBaseAddr{0x00002000U};
constexpr uint32_t flashEndAddr{0x00040000U};

const std::array<usb::dfu::zone_t, 1> firmwareZone
{{
	{
		applicationBaseAddr,
		flashEndAddr
	}
}};

// The linker script pins this to 0x20001000
[[gnu::section(".bootMagic")]] static uint16_t bootMagic;

constexpr static uint16_t bootMagicDFU{0xBADB};

namespace osc
{
	void init() noexcept
	{
		// Clock bring-up on this chip has to be divided into three distinct phases, thanks to shenanigans.
		// In the first phase, MOsc has to be enabled
		// In the second, the CPU clock source has to be switched to MOsc and the PLL powered up
		// In the third, once the PLL reads as stable, the bypass removed and SysClockDiv configured
		// to provide a suitable operating clock.
		// Once all this is done, we finally end up running on the PLL generated clock and can
		// do bring-up on the USB PLL.
		// Additionally, the third phase has to switch clock config registers from the primary
		// to the secondary so we can select 80MHz as our operating frequency

		sysCtrl.mainOscCtrl = vals::sysCtrl::mainOscCtrlOscFailInterrupt | vals::sysCtrl::mainOscCtrlClockMonitorEnable;
		sysCtrl.runClockConfig1 &= vals::sysCtrl::runClockCfg1MainOscEnableMask;

		// TI have provided no way to check that the main oscillator came up.. instead
		// even their own platform library busy loops for 524288 iterations, then hopes
		// and prays when they enable the source that things don't go sideways in a hurry.
		for (volatile uint32_t loops = 524288U; loops; --loops)
			loops;

		sysCtrl.runClockConfig1 = (sysCtrl.runClockConfig1 & vals::sysCtrl::runClockCfg1Mask) |
			vals::sysCtrl::runClockCfg1MainOscEnable | vals::sysCtrl::runClockCfg1MainOscXtal25MHz |
			vals::sysCtrl::runClockCfg1PLLPowerUp | vals::sysCtrl::runClockCfg1PLLBypass |
			vals::sysCtrl::runClockCfg1NoPWMClkDiv | vals::sysCtrl::runClockCfg1NoSysClkDiv |
			vals::sysCtrl::runClockCfg1OscSourceMainOsc | vals::sysCtrl::runClockCfg1SysClockDiv(0);
		while (!(sysCtrl.pllStatus & vals::sysCtrl::pllStatusLocked))
			continue;

		sysCtrl.runClockConfig2 = (sysCtrl.runClockConfig2 & vals::sysCtrl::runClockCfg2Mask) |
			vals::sysCtrl::runClockCfg2UseRCC2 | vals::sysCtrl::runClockCfg2PLLPreDivDisable |
			vals::sysCtrl::runClockCfg2PLLUSBPowerUp | vals::sysCtrl::runClockCfg2PLLPowerUp |
			vals::sysCtrl::runClockCfg2PLLNoBypass | vals::sysCtrl::runClockCfg2OscSourceMainOsc |
			vals::sysCtrl::runClockCfg2SysClockDiv(2) | vals::sysCtrl::runClockCfgSysClockDivLSBClr;
	}
} // namespace osc

void enableInterrupts() noexcept { }
void idle() noexcept { __asm__("wfi"); }

bool mustEnterBootloader() noexcept
{
	if (!(sysCtrl.resetCause & vals::sysCtrl::resetCausePOR) && bootMagic == bootMagicDFU)
		return true;
	bootMagic = 0;
	sysCtrl.resetCause = 0;
	uint32_t stackPointer{};
	static_assert(sizeof(uint32_t) == 4);
	// NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
	std::memcpy(&stackPointer, reinterpret_cast<const void *>(applicationBaseAddr), sizeof(uint32_t));
	return stackPointer == 0xFFFFFFFFU;
}

void rebootToFirmware() noexcept
{
	scb.vtable = applicationBaseAddr;
	__asm__(R"(
		mov		r0, %[baseAddr]
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
		bootMagic = 0;
		scb.apint = vals::scb::apintKey | vals::scb::apintSystemResetRequest;
		while (true)
			continue;
	}

	bool flashBusy() noexcept
	{
		return (flashCtrl.flashMemCtrl & vals::flashCtrl::flashMemCtrlErase) ||
			(flashCtrl.flashMemCtrl2 & vals::flashCtrl::flashMemCtrlWrite);
	}

	void erase(const std::uintptr_t address) noexcept
	{
		flashCtrl.flashMemAddr = address;
		flashCtrl.flashMemCtrl = vals::flashCtrl::flashMemCtrlKey | vals::flashCtrl::flashMemCtrlErase;
	}

	void write(const std::uintptr_t address, const std::size_t count, const uint8_t *const buffer) noexcept
	{
		if (!count || count > flashBufferSize)
			return;

		// for (const auto &offset : substrate::indexSequence_t{0, count, 4})
		for (size_t offset{0U}; offset < count; offset += 4U)
		{
			const auto bufferOffset{(offset >> 2) & 31U};
			const auto amount{std::min<size_t>(count - offset, 4U)};
			uint32_t data{0xFFFFFFFFU};
			std::memcpy(&data, buffer + offset, amount);
			flashCtrl.flashMemBuffer[bufferOffset] = data;
		}
		flashCtrl.flashMemAddr = address;
		flashCtrl.flashMemCtrl2 = vals::flashCtrl::flashMemCtrlKey |
			vals::flashCtrl::flashMemCtrlWrite;
	}
} // namespace usb::dfu

void irqUSB() noexcept { usb::core::handleIRQ(); }
