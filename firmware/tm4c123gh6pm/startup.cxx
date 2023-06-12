// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <array>
#include "tm4c123gh6pm.hxx"

extern const uint32_t stackTop;

using irqFunction_t = void (*)();

struct nvicTable_t final
{
	const void *stackTop{nullptr};
	std::array<irqFunction_t, 155> vectorTable{{}};
};

[[gnu::section(".nvic_table"), gnu::used]] static const nvicTable_t nvicTable
{
	&stackTop,
	{
		irqReset, /* Reset handler */
		irqNMI, /* NMI handler */
		irqHardFault, /* Hard Fault handler */

		/* Configurable priority handlers */
		irqMMUFault, /* MMU Fault handler */
		irqBusFault, /* Bus Fault handler */
		irqUsageFault, /* Usage Fault */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqServiceCall, /* SV Call */
		irqDebugMonitor, /* Debug Monitor */
		nullptr, /* Reserved */
		irqPendingServiceCall, /* Pending SV */
		irqSysTick, /* Sys Tick */

		/* Peripheral handlers */
		irqGPIOPortA, /* GPIO Port A */
		irqGPIOPortB, /* GPIO Port B */
		irqGPIOPortC, /* GPIO Port C */
		irqGPIOPortD, /* GPIO Port D */
		irqGPIOPortE, /* GPIO Port E */
		irqUART0, /* UART 0 */
		irqUART1, /* UART 1 */
		irqSSI0, /* SSI 0 */
		irqI2C0, /* I2C 0 */
		irqPWM0Fault, /* PWM 0 Fault */
		irqPWM0Gen0, /* PWM 0 Generator 0 */
		irqPWM0Gen1, /* PWM 0 Generator 1 */
		irqPWM0Gen2, /* PWM 0 Generator 2 */
		irqQEI0, /* QEI 0 */
		irqADC0Seq0, /* ADC 0 Sequence 0 */
		irqADC0Seq1, /* ADC 0 Sequence 1 */
		irqADC0Seq2, /* ADC 0 Sequence 2 */
		irqADC0Seq3, /* ADC 0 Sequence 3 */
		irqWDT, /* WDT */
		irqTimer0A, /* Timer 0 A (16/32-bit) */
		irqTimer0B, /* Timer 0 B (16/32-bit) */
		irqTimer1A, /* Timer 1 A (16/32-bit) */
		irqTimer1B, /* Timer 1 B (16/32-bit) */
		irqTimer2A, /* Timer 2 A (16/32-bit) */
		irqTimer2B, /* Timer 2 B (16/32-bit) */
		irqComp0, /* Analog Comparator 0 */
		irqComp1, /* Analog Comparator 1 */
		irqComp2, /* Analog Comparator 2 */
		irqSysCtl, /* SysCtl */
		irqNVMCtrl, /* Flash + EEPROM Ctl */
		irqGPIOPortF, /* GPIO Port F */
		irqGPIOPortG, /* GPIO Port G */
		irqGPIOPortH, /* GPIO Port H */
		irqUART2, /* UART 2 */
		irqSSI1, /* SSI 1 */
		irqTimer3A, /* Timer 3 A (16/32-bit) */
		irqTimer3B, /* Timer 3 B (16/32-bit) */
		irqI2C1, /* I2C 1 */
		irqQEI1, /* QEI 1 */
		irqCAN0, /* CAN 0 */
		irqCAN1, /* CAN 1 */
		irqCAN2, /* CAN 2 */
		nullptr, /* Reserved */
		irqHibernation, /* Hibernation Module */
		irqUSB, /* USB */
		irqPWM0Gen3, /* PWM 0 Generator 3 */
		irqUDMASoftwareComplete, /* UDMA Software Transfer Complete */
		irqUDMAError, /* UDMA Error */
		irqADC1Seq0, /* ADC 1 Sequence 0 */
		irqADC1Seq1, /* ADC 1 Sequence 1 */
		irqADC1Seq2, /* ADC 1 Sequence 2 */
		irqADC1Seq3, /* ADC 1 Sequence 3 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqGPIOPortJ , /* GPIO Port J */
		irqGPIOPortK , /* GPIO Port K */
		irqGPIOPortL , /* GPIO Port L */
		irqSSI2, /* SSI 2 */
		irqSSI3, /* SSI 3 */
		irqUART3, /* UART 3 */
		irqUART4, /* UART 4 */
		irqUART5, /* UART 5 */
		irqUART6, /* UART 6 */
		irqUART7, /* UART 7 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqI2C2, /* I2C 2 */
		irqI2C3, /* I2C 3 */
		irqTimer4A, /* Timer 4 A (16/32-bit) */
		irqTimer4B, /* Timer 4 B (16/32-bit) */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqTimer5A, /* Timer 5 A (16/32-bit) */
		irqTimer5B, /* Timer 5 B (16/32-bit) */
		irqWideTimer0A, /* Timer 0 A (32/64-bit) */
		irqWideTimer0B, /* Timer 0 B (32/64-bit) */
		irqWideTimer1A, /* Timer 1 A (32/64-bit) */
		irqWideTimer1B, /* Timer 1 B (32/64-bit) */
		irqWideTimer2A, /* Timer 2 A (32/64-bit) */
		irqWideTimer2B, /* Timer 2 B (32/64-bit) */
		irqWideTimer3A, /* Timer 3 A (32/64-bit) */
		irqWideTimer3B, /* Timer 3 B (32/64-bit) */
		irqWideTimer4A, /* Timer 4 A (32/64-bit) */
		irqWideTimer4B, /* Timer 4 B (32/64-bit) */
		irqWideTimer5A, /* Timer 5 A (32/64-bit) */
		irqWideTimer5B, /* Timer 5 B (32/64-bit) */
		irqFPU, /* FPU */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqI2C4, /* I2C 4 */
		irqI2C5, /* I2C 5 */
		irqGPIOPortM, /* GPIO Port M */
		irqGPIOPortN, /* GPIO Port N */
		irqQEI2, /* QEI 2 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqGPIOPortP0, /* GPIO Port P0/Summary */
		irqGPIOPortP1, /* GPIO Port P1 */
		irqGPIOPortP2, /* GPIO Port P2 */
		irqGPIOPortP3, /* GPIO Port P3 */
		irqGPIOPortP4, /* GPIO Port P4 */
		irqGPIOPortP5, /* GPIO Port P5 */
		irqGPIOPortP6, /* GPIO Port P6 */
		irqGPIOPortP7, /* GPIO Port P7 */
		irqGPIOPortQ0, /* GPIO Port Q0/Summary */
		irqGPIOPortQ1, /* GPIO Port Q1 */
		irqGPIOPortQ2, /* GPIO Port Q2 */
		irqGPIOPortQ3, /* GPIO Port Q3 */
		irqGPIOPortQ4, /* GPIO Port Q4 */
		irqGPIOPortQ5, /* GPIO Port Q5 */
		irqGPIOPortQ6, /* GPIO Port Q6 */
		irqGPIOPortQ7, /* GPIO Port Q7 */
		irqGPIOPortR, /* GPIO Port R */
		irqGPIOPortS, /* GPIO Port S */
		irqPWM1Gen0, /* PWM 1 Generator 0 */
		irqPWM1Gen1, /* PWM 1 Generator 1 */
		irqPWM1Gen2, /* PWM 1 Generator 2 */
		irqPWM1Gen3, /* PWM 1 Generator 3 */
		irqPWM1Fault, /* PWM 1 Fault */
	}
};

// This weak-linked implementation of irqEmptyDef() is required
// to satisfy the compiler's requirements on function aliasing.
// It will be replaced during linking with the implementation
// in aarch32/irqs.cxx. It could even be an empty function, as
// long as the definition is here to make it a defined symbol.
[[gnu::weak]] void irqEmptyDef() noexcept
{
	while (true)
		continue;
}

WEAK_IRQ(void irqGPIOPortA() noexcept);
WEAK_IRQ(void irqGPIOPortB() noexcept);
WEAK_IRQ(void irqGPIOPortC() noexcept);
WEAK_IRQ(void irqGPIOPortD() noexcept);
WEAK_IRQ(void irqGPIOPortE() noexcept);
WEAK_IRQ(void irqGPIOPortF() noexcept);
WEAK_IRQ(void irqGPIOPortG() noexcept);
WEAK_IRQ(void irqGPIOPortH() noexcept);
WEAK_IRQ(void irqGPIOPortI() noexcept);
WEAK_IRQ(void irqGPIOPortJ() noexcept);
WEAK_IRQ(void irqGPIOPortK() noexcept);
WEAK_IRQ(void irqGPIOPortL() noexcept);
WEAK_IRQ(void irqGPIOPortM() noexcept);
WEAK_IRQ(void irqGPIOPortN() noexcept);
WEAK_IRQ(void irqGPIOPortR() noexcept);
WEAK_IRQ(void irqGPIOPortS() noexcept);

WEAK_IRQ(void irqGPIOPortP0() noexcept);
WEAK_IRQ(void irqGPIOPortP1() noexcept);
WEAK_IRQ(void irqGPIOPortP2() noexcept);
WEAK_IRQ(void irqGPIOPortP3() noexcept);
WEAK_IRQ(void irqGPIOPortP4() noexcept);
WEAK_IRQ(void irqGPIOPortP5() noexcept);
WEAK_IRQ(void irqGPIOPortP6() noexcept);
WEAK_IRQ(void irqGPIOPortP7() noexcept);

WEAK_IRQ(void irqGPIOPortQ0() noexcept);
WEAK_IRQ(void irqGPIOPortQ1() noexcept);
WEAK_IRQ(void irqGPIOPortQ2() noexcept);
WEAK_IRQ(void irqGPIOPortQ3() noexcept);
WEAK_IRQ(void irqGPIOPortQ4() noexcept);
WEAK_IRQ(void irqGPIOPortQ5() noexcept);
WEAK_IRQ(void irqGPIOPortQ6() noexcept);
WEAK_IRQ(void irqGPIOPortQ7() noexcept);

WEAK_IRQ(void irqUART0() noexcept);
WEAK_IRQ(void irqUART1() noexcept);
WEAK_IRQ(void irqUART2() noexcept);
WEAK_IRQ(void irqUART3() noexcept);
WEAK_IRQ(void irqUART4() noexcept);
WEAK_IRQ(void irqUART5() noexcept);
WEAK_IRQ(void irqUART6() noexcept);
WEAK_IRQ(void irqUART7() noexcept);

WEAK_IRQ(void irqSSI0() noexcept);
WEAK_IRQ(void irqSSI1() noexcept);
WEAK_IRQ(void irqSSI2() noexcept);
WEAK_IRQ(void irqSSI3() noexcept);

WEAK_IRQ(void irqI2C0() noexcept);
WEAK_IRQ(void irqI2C1() noexcept);
WEAK_IRQ(void irqI2C2() noexcept);
WEAK_IRQ(void irqI2C3() noexcept);
WEAK_IRQ(void irqI2C4() noexcept);
WEAK_IRQ(void irqI2C5() noexcept);

WEAK_IRQ(void irqPWM0Fault() noexcept);
WEAK_IRQ(void irqPWM0Gen0() noexcept);
WEAK_IRQ(void irqPWM0Gen1() noexcept);
WEAK_IRQ(void irqPWM0Gen2() noexcept);
WEAK_IRQ(void irqPWM0Gen3() noexcept);
WEAK_IRQ(void irqPWM1Fault() noexcept);
WEAK_IRQ(void irqPWM1Gen0() noexcept);
WEAK_IRQ(void irqPWM1Gen1() noexcept);
WEAK_IRQ(void irqPWM1Gen2() noexcept);
WEAK_IRQ(void irqPWM1Gen3() noexcept);

WEAK_IRQ(void irqQEI0() noexcept);
WEAK_IRQ(void irqQEI1() noexcept);
WEAK_IRQ(void irqQEI2() noexcept);

WEAK_IRQ(void irqADC0Seq0() noexcept);
WEAK_IRQ(void irqADC0Seq1() noexcept);
WEAK_IRQ(void irqADC0Seq2() noexcept);
WEAK_IRQ(void irqADC0Seq3() noexcept);
WEAK_IRQ(void irqADC1Seq0() noexcept);
WEAK_IRQ(void irqADC1Seq1() noexcept);
WEAK_IRQ(void irqADC1Seq2() noexcept);
WEAK_IRQ(void irqADC1Seq3() noexcept);

WEAK_IRQ(void irqTimer0A() noexcept);
WEAK_IRQ(void irqTimer0B() noexcept);
WEAK_IRQ(void irqTimer1A() noexcept);
WEAK_IRQ(void irqTimer1B() noexcept);
WEAK_IRQ(void irqTimer2A() noexcept);
WEAK_IRQ(void irqTimer2B() noexcept);
WEAK_IRQ(void irqTimer3A() noexcept);
WEAK_IRQ(void irqTimer3B() noexcept);
WEAK_IRQ(void irqTimer4A() noexcept);
WEAK_IRQ(void irqTimer4B() noexcept);
WEAK_IRQ(void irqTimer5A() noexcept);
WEAK_IRQ(void irqTimer5B() noexcept);

WEAK_IRQ(void irqWideTimer0A() noexcept);
WEAK_IRQ(void irqWideTimer0B() noexcept);
WEAK_IRQ(void irqWideTimer1A() noexcept);
WEAK_IRQ(void irqWideTimer1B() noexcept);
WEAK_IRQ(void irqWideTimer2A() noexcept);
WEAK_IRQ(void irqWideTimer2B() noexcept);
WEAK_IRQ(void irqWideTimer3A() noexcept);
WEAK_IRQ(void irqWideTimer3B() noexcept);
WEAK_IRQ(void irqWideTimer4A() noexcept);
WEAK_IRQ(void irqWideTimer4B() noexcept);
WEAK_IRQ(void irqWideTimer5A() noexcept);
WEAK_IRQ(void irqWideTimer5B() noexcept);

WEAK_IRQ(void irqComp0() noexcept);
WEAK_IRQ(void irqComp1() noexcept);
WEAK_IRQ(void irqComp2() noexcept);

WEAK_IRQ(void irqCAN0() noexcept);
WEAK_IRQ(void irqCAN1() noexcept);
WEAK_IRQ(void irqCAN2() noexcept);

WEAK_IRQ(void irqUDMASoftwareComplete() noexcept);
WEAK_IRQ(void irqUDMAError() noexcept);

WEAK_IRQ(void irqWDT() noexcept);
WEAK_IRQ(void irqSysCtl() noexcept);
WEAK_IRQ(void irqNVMCtrl() noexcept);
WEAK_IRQ(void irqHibernation() noexcept);
WEAK_IRQ(void irqUSB() noexcept);
WEAK_IRQ(void irqFPU() noexcept);
