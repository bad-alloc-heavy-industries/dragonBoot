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
		irqEmptyDef, /* UART 0 */
		irqEmptyDef, /* UART 1 */
		irqEmptyDef, /* SSI 0 */
		irqEmptyDef, /* I2C 0 */
		irqEmptyDef, /* PWM 0 Fault */
		irqEmptyDef, /* PWM 0 Generator 0 */
		irqEmptyDef, /* PWM 0 Generator 1 */
		irqEmptyDef, /* PWM 0 Generator 2 */
		irqEmptyDef, /* QEI 0 */
		irqEmptyDef, /* ADC 0 Sequence 0 */
		irqEmptyDef, /* ADC 0 Sequence 1 */
		irqEmptyDef, /* ADC 0 Sequence 2 */
		irqEmptyDef, /* ADC 0 Sequence 3 */
		irqEmptyDef, /* WDT */
		irqEmptyDef, /* Timer 0 A (16/32-bit) */
		irqEmptyDef, /* Timer 0 B (16/32-bit) */
		irqEmptyDef, /* Timer 1 A (16/32-bit) */
		irqEmptyDef, /* Timer 1 B (16/32-bit) */
		irqEmptyDef, /* Timer 2 A (16/32-bit) */
		irqEmptyDef, /* Timer 2 B (16/32-bit) */
		irqEmptyDef, /* Analog Comparator 0 */
		irqEmptyDef, /* Analog Comparator 1 */
		irqEmptyDef, /* Analog Comparator 2 */
		irqEmptyDef, /* SysCtl */
		irqEmptyDef, /* Flash + EEPROM Ctl */
		irqEmptyDef, /* GPIO Port F */
		irqEmptyDef, /* GPIO Port G */
		irqEmptyDef, /* GPIO Port H */
		irqEmptyDef, /* UART 2 */
		irqEmptyDef, /* SSI 1 */
		irqEmptyDef, /* Timer 3 A (16/32-bit) */
		irqEmptyDef, /* Timer 3 B (16/32-bit) */
		irqEmptyDef, /* I2C 1 */
		irqEmptyDef, /* QEI 1 */
		irqEmptyDef, /* CAN 0 */
		irqEmptyDef, /* CAN 1 */
		irqEmptyDef, /* CAN 2 */
		nullptr, /* Reserved */
		irqEmptyDef, /* Hibernation Module */
		irqUSB, /* USB */
		irqEmptyDef, /* PWM 0 Generator 3 */
		irqEmptyDef, /* UDMA SW */
		irqEmptyDef, /* UDMA Error */
		irqEmptyDef, /* ADC 1 Sequence 0 */
		irqEmptyDef, /* ADC 1 Sequence 1 */
		irqEmptyDef, /* ADC 1 Sequence 2 */
		irqEmptyDef, /* ADC 1 Sequence 3 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqEmptyDef, /* GPIO Port J */
		irqEmptyDef, /* GPIO Port K */
		irqEmptyDef, /* GPIO Port L */
		irqEmptyDef, /* SSI 2 */
		irqEmptyDef, /* SSI 3 */
		irqEmptyDef, /* UART 3 */
		irqEmptyDef, /* UART 4 */
		irqEmptyDef, /* UART 5 */
		irqEmptyDef, /* UART 6 */
		irqEmptyDef, /* UART 7 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqEmptyDef, /* I2C 2 */
		irqEmptyDef, /* I2C 3 */
		irqEmptyDef, /* Timer 4 A (16/32-bit) */
		irqEmptyDef, /* Timer 4 B (16/32-bit) */
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
		irqEmptyDef, /* Timer 5 A (16/32-bit) */
		irqEmptyDef, /* Timer 5 B (16/32-bit) */
		irqEmptyDef, /* Timer 0 A (32/64-bit) */
		irqEmptyDef, /* Timer 0 B (32/64-bit) */
		irqEmptyDef, /* Timer 1 A (32/64-bit) */
		irqEmptyDef, /* Timer 1 B (32/64-bit) */
		irqEmptyDef, /* Timer 2 A (32/64-bit) */
		irqEmptyDef, /* Timer 2 B (32/64-bit) */
		irqEmptyDef, /* Timer 3 A (32/64-bit) */
		irqEmptyDef, /* Timer 3 B (32/64-bit) */
		irqEmptyDef, /* Timer 4 A (32/64-bit) */
		irqEmptyDef, /* Timer 4 B (32/64-bit) */
		irqEmptyDef, /* Timer 5 A (32/64-bit) */
		irqEmptyDef, /* Timer 5 B (32/64-bit) */
		irqEmptyDef, /* FPU */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqEmptyDef, /* I2C 4 */
		irqEmptyDef, /* I2C 5 */
		irqEmptyDef, /* GPIO Port M */
		irqEmptyDef, /* GPIO Port N */
		irqEmptyDef, /* QEI 2 */
		nullptr, /* Reserved */
		nullptr, /* Reserved */
		irqEmptyDef, /* GPIO Port P0/Summary */
		irqEmptyDef, /* GPIO Port P1 */
		irqEmptyDef, /* GPIO Port P2 */
		irqEmptyDef, /* GPIO Port P3 */
		irqEmptyDef, /* GPIO Port P4 */
		irqEmptyDef, /* GPIO Port P5 */
		irqEmptyDef, /* GPIO Port P6 */
		irqEmptyDef, /* GPIO Port P7 */
		irqEmptyDef, /* GPIO Port Q0/Summary */
		irqEmptyDef, /* GPIO Port Q1 */
		irqEmptyDef, /* GPIO Port Q2 */
		irqEmptyDef, /* GPIO Port Q3 */
		irqEmptyDef, /* GPIO Port Q4 */
		irqEmptyDef, /* GPIO Port Q5 */
		irqEmptyDef, /* GPIO Port Q6 */
		irqEmptyDef, /* GPIO Port Q7 */
		irqEmptyDef, /* GPIO Port R */
		irqEmptyDef, /* GPIO Port S */
		irqEmptyDef, /* PWM 1 Generator 0 */
		irqEmptyDef, /* PWM 1 Generator 1 */
		irqEmptyDef, /* PWM 1 Generator 2 */
		irqEmptyDef, /* PWM 1 Generator 3 */
		irqEmptyDef, /* PWM 1 Fault */
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
