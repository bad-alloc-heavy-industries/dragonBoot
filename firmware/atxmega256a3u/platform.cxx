// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <cstring>
#include <substrate/index_sequence>
#include <avr/io.h>
#include <avr/builtins.h>
#include <flash.hxx>
#include <usb/core.hxx>
#include "platform.hxx"
#include "atxmega256a3u.hxx"

FUSES =
{
	FUSE0_DEFAULT,
	FUSE1_DEFAULT,
	FUSE2_DEFAULT & FUSE_BOOTRST,
	0xFF,
	FUSE4_DEFAULT & FUSE_JTAGEN,
	FUSE5_DEFAULT & FUSE_EESAVE,
};

constexpr uint32_t applicationBaseAddr{0x00000000U};
constexpr uint32_t flashEndAddr{0x00040000U};

const std::array<usb::dfu::zone_t, 1> firmwareZone
{{
	{
		applicationBaseAddr,
		flashEndAddr
	}
}};

std::array<char16_t, serialLength> serialNumber{{}};

extern "C" void *_memcpy(void *dest, const void *src, size_t len);

// NOLINTNEXTLINE(cert-dcl58-cpp)
namespace std
{
	void *memcpy(void *dest, const void *src, size_t len) __attribute__((weak, alias("_memcpy")));
}

namespace osc
{
	void init() noexcept
	{
		// Set PE4 and 5 to output and get blanking happening ASAP
		PORTE.OUTCLR = 0x20;
		PORTE.OUTSET = 0x10;
		PORTE.DIRSET = 0x30;
		// Set up the crystal's pins
		PORTR.DIRCLR = 0x01;
		OSC.XOSCCTRL = OSC_FRQRANGE_12TO16_gc | OSC_XOSCSEL_EXTCLK_gc;
		// Enable the external osc
		OSC.CTRL |= 0x09;
		while (!(OSC.STATUS & 0x08))
			continue;
		CCP = CCP_IOREG_gc;
		OSC.XOSCFAIL = 1;

		CCP = CCP_IOREG_gc;
		CLK.PSCTRL = CLK_PSADIV_1_gc | CLK_PSBCDIV_1_1_gc;
		CCP = CCP_IOREG_gc;
		CLK.CTRL = CLK_SCLKSEL_XOSC_gc;

		// Disable the internal 2MHz RC osc, but also enable the 32MHz one.
		OSC.CTRL = 0x0A;

		// Configure the PLL to take our 16MHz clock and spin it up to 48MHz
		OSC.PLLCTRL = OSC_PLLSRC_XOSC_gc | 3;
		OSC.CTRL |= 0x10;
		// Wait for it to become ready
		while (!(OSC.STATUS & 0x10))
			continue;
		// And enable the USB peripheral's use of it.
		CLK.USBCTRL = CLK_USBPSDIV_1_gc | CLK_USBSRC_PLL_gc | 1;
	}
} // namespace osc

void enableInterrupts() noexcept
{
	CCP = CCP_IOREG_gc;
	PMIC.CTRL = 0xC7U;
	__builtin_avr_sei();
}

void idle() noexcept { /*__builtin_avr_sleep();*/ }

void readSerialNumber() noexcept
{
}

bool mustEnterBootloader() noexcept
{
	// If we did not get here through any form of reset source, we must bootload.
	if (!RST.STATUS)
		return true;
	RST.STATUS = 0;
	flash_t<uint32_t *> resetVector{nullptr};
	static_assert(sizeof(uint32_t) == 4);
	return *resetVector == 0xFFFFFFFFU;
}

void rebootToFirmware() noexcept
{
	__builtin_avr_cli();
	CCP = CCP_IOREG_gc;
	PMIC.CTRL = 0U;
	__asm__("jmp 0"); // Jump to the firmware reset vector
	while (true)
		continue;
}

namespace usb::dfu
{
	void reboot() noexcept
	{
		CCP = CCP_IOREG_gc;
		RST.CTRL = 0x01U; // Issue a software reset
		while (true)
			continue;
	}

	bool flashBusy() noexcept
	{
		const auto result{bool(NVM.STATUS & NVM_NVMBUSY_bm)};
		if (!result)
			NVM.CMD = NVM_CMD_NO_OPERATION_gc;
		return result;
	}

	void erase(const std::uintptr_t) noexcept
	{
		NVM.CMD = NVM_CMD_ERASE_FLASH_BUFFER_gc;
		CCP = CCP_IOREG_gc;
		NVM.CTRLA = NVM_CMDEX_bm;
	}

	void write(const std::uintptr_t address, const std::size_t count, const uint8_t *const buffer) noexcept
	{
		const auto memoryAddr{reinterpret_cast<uint32_t>(buffer)};
		NVM.CMD = NVM_CMD_LOAD_FLASH_BUFFER_gc;
		__asm__(R"(
				movw r26, %[memory]
				out 0x39, %C[memory]
				movw r30, %[flash]
				out 0x3B, %C[flash]
				movw r24, %[count]
				clz
loop%=:
				breq loopDone%=
				ld r0, X+
				ld r1, X+
				spm Z+
				sbiw r24, 2
				rjmp loop%=
loopDone%=:
			)" : : [memory] "r" (memoryAddr), [flash] "r" (address), [count] "r" (count) :
				"r0", "r1", "r24", "r25", "r26", "r27", "r30", "r31"
		);

		NVM.CMD = NVM_CMD_ERASE_WRITE_FLASH_PAGE_gc;
		__asm__(R"(
				movw r30, %[page] ; Load Z with the page to erase + write
				out 0x3B, %C[page]
				ldi r16, 0x9D
				out 0x34, r16 ; Unlock SPM
				spm
			)" : : [page] "r" (address) : "r16", "r30", "r31"
		);
	}
} // namespace usb::dfu

void *_memcpy(void *dest, const void *src, size_t len)
{
	auto *_dest{static_cast<char *>(dest)};
	const auto *const _src{static_cast<const char *>(src)};
	for (size_t i{0}; i < len; ++i)
		_dest[i] = _src[i];
	return dest;
}

void irqOSCFailure() noexcept
{
	OSC.CTRL = 0x0A;
	CCP = CCP_IOREG_gc;
	CLK.CTRL = CLK_SCLKSEL_RC32M_gc;
	CCP = CCP_IOREG_gc;
	CLK.PSCTRL = CLK_PSADIV_2_gc | CLK_PSBCDIV_2_2_gc;
	OSC.XOSCFAIL = 2;
}

void irqUSB() noexcept { usb::core::handleIRQ(); }
