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

// The linker script pins this to 0x20001000
[[gnu::section(".bootMagic")]] static uint16_t bootMagic;

constexpr static uint16_t bootMagicDFU{0xBADB};

void enableInterrupts() noexcept { }
void idle() noexcept { __asm__("wfi"); }

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
		bootMagic = 0;
		scb.apint = vals::scb::apintKey | vals::scb::apintSystemResetRequest;
		while (true)
			continue;
	}
} // namespace usb::dfu

void irqCANRx0USBLowPriority() noexcept { usb::core::handleIRQ(); }
