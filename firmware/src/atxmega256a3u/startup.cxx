// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <avr/io.h>
#include <avr/builtins.h>
#include "platform.hxx"
#include "atxmega256a3u.hxx"

extern const char stackTop;
extern char vectorAddr;
extern const uint8_t beginData;
extern const uint8_t endData;
extern const uint8_t addrData;
extern uint8_t beginBSS;
extern const uint8_t endBSS;

using ctorFuncs_t = void (*)();
extern const ctorFuncs_t beginCtors, endCtors;

extern "C"
{
	[[gnu::used, gnu::section(".vectors"), gnu::naked, gnu::optimize(0)]] void vectorTable();
	[[gnu::used, gnu::section(".startup"), gnu::visibility("default")]] void init();
	[[gnu::used, gnu::signal]] void irqEmptyDef();
}

inline void copyData() noexcept
{
	const uint8_t x{RAMPX};
	const uint8_t z{RAMPZ};

	__asm__(R"(
		; Set up X with addrData
		ldi r26, lo8(beginData)
		ldi r27, hi8(beginData)
		ldi r16, hh8(beginData)
		out 0x39, r16
		; Set up Z with beginData
		ldi r30, lo8(addrData)
		ldi r31, hi8(addrData)
		ldi r16, hh8(addrData)
		out 0x3B, r16
		ldi r17, hi8(endData)
dataCopyLoop:
		; Check the current value of Z against endData
		cpi r26, lo8(endData)
		cpc r27, r17
		breq dataCopyDone
		; Load the next byte from Flash and store it at the location pointed to by X
		elpm r16, Z+
		st X+, r16
		rjmp dataCopyLoop
dataCopyDone:
		)" : : : "r16", "r17", "r26", "r27", "r30", "r31"
	);

	RAMPZ = z;
	RAMPX = x;
}

inline void callCtors() noexcept
{
	__asm__(R"(
		; Set up X with beginCtors
		ldi r26, lo8(beginCtors)
		ldi r27, hi8(beginCtors)
ctorLoop:
		; Check the current value of X against endCtors
		ldi r16, hi8(endCtors)
		cpi r26, hi8(endCtors)
		cpc r27, r16
		breq ctorDone
		; Load Z with the next constructor address from Flash
		movw r30, r26
		elpm r16, Z+
		elpm r17, Z+
		movw r26, r30
		movw r30, r16
		; Call the constructor
		eicall
		rjmp ctorLoop
ctorDone:
		)" : : :
	);
}

void init()
{
	__asm__("clr r1");
	SREG = 0;

	static_assert(__AVR_XMEGA__);
	// NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
	const auto stack{reinterpret_cast<uintptr_t>(&stackTop)};
	SPL = uint8_t(stack);
	SPH = uint8_t(stack >> 8U);

	static_assert(__AVR_3_BYTE_PC__);
	__asm__(R"(
		ldi r16, hh8(vectorTable)
		out 0x3C, r16
		)" : : : "r16"
	);

	RAMPD = 0;
	RAMPX = 0;
	RAMPY = 0;
	RAMPZ = 0;

	static_assert(FLASHEND > 0x10000);
	static_assert(__AVR_ENHANCED__);

	while (true)
	{
		__builtin_avr_cli();
		copyData();
		for (auto *dst{&beginBSS}; dst < &endBSS; ++dst)
			*dst = 0;
		//callCtors();
		run();
	}
}

void irqEmptyDef()
{
	while (true)
		continue;
}

void vectorTable()
{
	__asm__(R"(
		jmp init
		jmp irqOSCFailure ; OSC fail vector
		jmp irqEmptyDef ; Port C Int0 vector
		jmp irqEmptyDef ; Port C Int1 vector
		jmp irqEmptyDef ; Port R Int0 vector
		jmp irqEmptyDef ; Port R Int1 vector
		jmp irqEmptyDef ; DMA Channel 0 vector
		jmp irqEmptyDef ; DMA Channel 1 vector
		jmp irqEmptyDef ; DMA Channel 2 vector
		jmp irqEmptyDef ; DMA Channel 3 vector
		jmp irqEmptyDef ; RTC Overflow vector
		jmp irqEmptyDef ; RTC Compare vector
		jmp irqEmptyDef ; Two-Wire C Peripheral vector
		jmp irqEmptyDef ; Two-Wire C Controller vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Overflow vector | Type 2 Low-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Error vector | Type 2 High-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Capture-Comp A vector | Type 2 Low-Byte Compare A vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Capture-Comp B vector | Type 2 Low-Byte Compare B vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Capture-Comp C vector | Type 2 Low-Byte Compare C vector
		jmp irqEmptyDef ; Timer/Counter C Type 0 Capture-Comp D vector | Type 2 Low-Byte Compare D vector
		jmp irqEmptyDef ; Timer/Counter C Type 1 Overflow vector
		jmp irqEmptyDef ; Timer/Counter C Type 1 Error vector
		jmp irqEmptyDef ; Timer/Counter C Type 1 Capture-Comp A vector
		jmp irqEmptyDef ; Timer/Counter C Type 1 Capture-Comp B vector
		jmp irqEmptyDef ; SPI C vector
		jmp irqEmptyDef ; USART C0 Receive Complete vector
		jmp irqEmptyDef ; USART C0 Data Register Empty vector
		jmp irqEmptyDef ; USART C0 Transmit Complete vector
		jmp irqEmptyDef ; USART C1 Receive Complete vector
		jmp irqEmptyDef ; USART C1 Data Register Empty vector
		jmp irqEmptyDef ; USART C1 Transmit Complete vector
		jmp irqEmptyDef ; AES vector
		jmp irqEmptyDef ; NVM EEPROM Ready vector
		jmp irqEmptyDef ; NVM SPM Ready vector
		jmp irqEmptyDef ; Port B Int0 vector
		jmp irqEmptyDef ; Port B Int1 vector
		jmp irqEmptyDef ; Analog Comparator B Int0 vector
		jmp irqEmptyDef ; Analog Comparator B Int1 vector
		jmp irqEmptyDef ; Analog Compatator B Window vector
		jmp irqEmptyDef ; ADC B Channel 0 vector
		jmp irqEmptyDef ; ADC B Channel 1 vector
		jmp irqEmptyDef ; ADC B Channel 2 vector
		jmp irqEmptyDef ; ADC B Channel 3 vector
		jmp irqEmptyDef ; Port E Int0 vector
		jmp irqEmptyDef ; Port E Int1 vector
		jmp irqEmptyDef ; Two-Wire E Peripheral vector
		jmp irqEmptyDef ; Two-Wire E Controller vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Overflow vector | Type 2 Low-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Error vector | Type 2 High-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Capture-Comp A vector | Type 2 Low-Byte Compare A vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Capture-Comp B vector | Type 2 Low-Byte Compare B vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Capture-Comp C vector | Type 2 Low-Byte Compare C vector
		jmp irqEmptyDef ; Timer/Counter E Type 0 Capture-Comp D vector | Type 2 Low-Byte Compare D vector
		jmp irqEmptyDef ; Timer/Counter E Type 1 Overflow vector
		jmp irqEmptyDef ; Timer/Counter E Type 1 Error vector
		jmp irqEmptyDef ; Timer/Counter E Type 1 Capture-Comp A vector
		jmp irqEmptyDef ; Timer/Counter E Type 1 Capture-Comp B vector
		jmp irqEmptyDef ; SPI E vector
		jmp irqEmptyDef ; USART E0 Data Complete vector
		jmp irqEmptyDef ; USART E0 Data Register Empty vector
		jmp irqEmptyDef ; USART E0 Transmit Complete vector
		jmp irqEmptyDef ; USART E1 Data Complete vector
		jmp irqEmptyDef ; USART E1 Data Register Empty vector
		jmp irqEmptyDef ; USART E1 Transmit Complete vector
		jmp irqEmptyDef ; Port D Int0 vector
		jmp irqEmptyDef ; Port D Int1 vector
		jmp irqEmptyDef ; Port A Int0 vector
		jmp irqEmptyDef ; Port A Int1 vector
		jmp irqEmptyDef ; Analog Comparator A Int0 vector
		jmp irqEmptyDef ; Analog Comparator A Int1 vector
		jmp irqEmptyDef ; Analog Compatator A Window vector
		jmp irqEmptyDef ; ADC A Channel 0 vector
		jmp irqEmptyDef ; ADC A Channel 1 vector
		jmp irqEmptyDef ; ADC A Channel 2 vector
		jmp irqEmptyDef ; ADC A Channel 3 vector
		jmp irqEmptyDef ; vector 75
		jmp irqEmptyDef ; vector 76
		jmp irqEmptyDef ; Timer/Counter D Type 0 Overflow vector | Type 2 Low-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter D Type 0 Error vector | Type 2 High-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter D Type 0 Capture-Comp A vector | Type 2 Low-Byte Compare A vector
		jmp irqEmptyDef ; Timer/Counter D Type 0 Capture-Comp B vector | Type 2 Low-Byte Compare B vector
		jmp irqEmptyDef ; Timer/Counter D Type 0 Capture-Comp C vector | Type 2 Low-Byte Compare C vector
		jmp irqEmptyDef ; Timer/Counter D Type 0 Capture-Comp D vector | Type 2 Low-Byte Compare D vector
		jmp irqEmptyDef ; Timer/Counter D Type 1 Overflow vector
		jmp irqEmptyDef ; Timer/Counter D Type 1 Error vector
		jmp irqEmptyDef ; Timer/Counter D Type 1 Capture-Comp A vector
		jmp irqEmptyDef ; Timer/Counter D Type 1 Capture-Comp B vector
		jmp irqEmptyDef ; SPI D vector
		jmp irqEmptyDef ; USART D0 Data Complete vector
		jmp irqEmptyDef ; USART D0 Data Register Empty vector
		jmp irqEmptyDef ; USART D0 Transmit Complete vector
		jmp irqEmptyDef ; USART D1 Data Complete vector
		jmp irqEmptyDef ; USART D1 Data Register Empty vector
		jmp irqEmptyDef ; USART D1 Transmit Complete vector
		jmp irqEmptyDef ; vector 94
		jmp irqEmptyDef ; vector 95
		jmp irqEmptyDef ; vector 96
		jmp irqEmptyDef ; vector 97
		jmp irqEmptyDef ; vector 98
		jmp irqEmptyDef ; vector 99
		jmp irqEmptyDef ; vector 100
		jmp irqEmptyDef ; vector 101
		jmp irqEmptyDef ; vector 102
		jmp irqEmptyDef ; vector 103
		jmp irqEmptyDef ; Port F Int0 vector
		jmp irqEmptyDef ; Port F Int1 vector
		jmp irqEmptyDef ; vector 106
		jmp irqEmptyDef ; vector 107
		jmp irqEmptyDef ; Timer/Counter F Type 0 Overflow vector | Type 2 Low-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter F Type 0 Error vector | Type 2 High-Byte Underflow vector
		jmp irqEmptyDef ; Timer/Counter F Type 0 Capture-Comp A vector | Type 2 Low-Byte Compare A vector
		jmp irqEmptyDef ; Timer/Counter F Type 0 Capture-Comp B vector | Type 2 Low-Byte Compare B vector
		jmp irqEmptyDef ; Timer/Counter F Type 0 Capture-Comp C vector | Type 2 Low-Byte Compare C vector
		jmp irqEmptyDef ; Timer/Counter F Type 0 Capture-Comp D vector | Type 2 Low-Byte Compare D vector
		jmp irqEmptyDef ; vector 114
		jmp irqEmptyDef ; vector 115
		jmp irqEmptyDef ; vector 116
		jmp irqEmptyDef ; vector 117
		jmp irqEmptyDef ; vector 118
		jmp irqEmptyDef ; USART F0 Data Complete vector
		jmp irqEmptyDef ; USART F0 Data Register Empty vector
		jmp irqEmptyDef ; USART F0 Transmit Complete vector
		jmp irqEmptyDef ; vector 122
		jmp irqEmptyDef ; vector 123
		jmp irqEmptyDef ; vector 124
		jmp irqUSB ; USB Bus Event vector
		jmp irqUSB ; USB Transaction Complete vector
	)");
}
