// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include "platform.hxx"
#include "aarch32.hxx"

extern const uint32_t endText;
// NOLINTNEXTLINE(cppcoreguidelines-avoid-non-const-global-variables)
extern uint32_t beginData;
extern const uint32_t endData;
// NOLINTNEXTLINE(cppcoreguidelines-avoid-non-const-global-variables)
extern uint32_t beginBSS;
extern const uint32_t endBSS;

using ctorFuncs_t = void (*)();
extern const ctorFuncs_t beginCtors, endCtors;

void irqReset() noexcept
{
	while (true)
	{
		const auto *src{&endText};
		for (auto *dst{&beginData}; dst < &endData; ++dst, ++src)
			*dst = *src;
		for (auto *dst{&beginBSS}; dst < &endBSS; ++dst)
			*dst = 0;
		for (const auto *ctor{&beginCtors}; ctor != &endCtors; ++ctor)
			(*ctor)();

		run();
	}
}

void irqNMI() noexcept
{
	while (true)
		continue;
}

void irqHardFault() noexcept
{
	/* Get some information about the fault for the debugger.. */
	__asm__(R"(
		movs	r0, #4
		movs	r1, lr
		tst		r0, r1
		beq		_MSP
		mrs		r0, psp
		b		_HALT
	_MSP:
		mrs		r0, msp
	_HALT:
		ldr		r1, [r0, 0x00] /* r0 */
		ldr		r2, [r0, 0x04] /* r1 */
		ldr		r3, [r0, 0x08] /* r2 */
		ldr		r4, [r0, 0x0C] /* r3 */
		ldr		r5, [r0, 0x10] /* r12 */
		ldr		r6, [r0, 0x14] /* lr */
		ldr		r7, [r0, 0x18] /* pc */
		ldr		r8, [r0, 0x1C] /* xpsr */
		bkpt	#0
	_DEADLOOP:
		b		_DEADLOOP
	)");
	/* The lowest 8 bits of r8 (xpsr) contain which handler triggered this, if there is a signal handler frame before this. */
}

void irqEmptyDef() noexcept
{
	while (true)
		continue;
}

WEAK_IRQ(void irqMMUFault() noexcept);
WEAK_IRQ(void irqBusFault() noexcept);
WEAK_IRQ(void irqUsageFault() noexcept);
WEAK_IRQ(void irqServiceCall() noexcept);
WEAK_IRQ(void irqDebugMonitor() noexcept);
WEAK_IRQ(void irqPendingServiceCall() noexcept);
WEAK_IRQ(void irqSysTick() noexcept);
