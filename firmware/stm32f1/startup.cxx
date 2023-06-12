// SPDX-License-Identifier: BSD-3-Clause
#include <cstdint>
#include <array>
#include "stm32f1.hxx"
#include "stm32f1/constants.hxx"

extern const uint32_t stackTop;

using irqFunction_t = void (*)();

struct nvicTable_t final
{
	const void *stackTop;
	std::array<irqFunction_t, vals::irqs::systemIRQs + vals::irqs::peripheralIRQs> vectorTable;
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
		irqWindowWDT,
		irqProgVoltageDetector,
		irqTamper,
		irqRTC,
		irqFlash,
		irqRCC,
		irqEXTI0,
		irqEXTI1,
		irqEXTI2,
		irqEXTI3,
		irqEXTI4,
		irqDMA1Channel1,
		irqDMA1Channel2,
		irqDMA1Channel3,
		irqDMA1Channel4,
		irqDMA1Channel5,
		irqDMA1Channel6,
		irqDMA1Channel7,
		irqADC1And2,
		irqCANTxUSBHighPriority,
		irqCANRx0USBLowPriority,
		irqCANRx1,
		irqCANSCE,
		irqEXTI5Through9,
		irqTimer1Break,
		irqTimer1Update,
		irqTimer1TriggerComms,
		irqTimer1CaptureCompare,
		irqTimer2,
		irqTimer3,
		irqTimer4,
		irqI2C1Event,
		irqI2C1Error,
		irqI2C2Event,
		irqI2C2Error,
		irqSPI1,
		irqSPI2,
		irqUSART1,
		irqUSART2,
		irqUSART3,
		irqEXTI10Through15,
		irqRTCAlarm,
		irqUSBWakeup,
		irqTimer8Break,
		irqTimer8Update,
		irqTimer8TriggerComms,
		irqTimer8CaptureCompare,
		irqADC3,
		irqFSMC,
		irqSDIO,
		irqTimer5,
		irqSPI3,
		irqUART4,
		irqUART5,
		irqTimer6,
		irqTimer7,
		irqDMA2Channel1,
		irqDMA2Channel2,
		irqDMA2Channel3,
		irqDMA2Channel4And5,
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

WEAK_IRQ(void irqEXTI0() noexcept);
WEAK_IRQ(void irqEXTI1() noexcept);
WEAK_IRQ(void irqEXTI2() noexcept);
WEAK_IRQ(void irqEXTI3() noexcept);
WEAK_IRQ(void irqEXTI4() noexcept);
WEAK_IRQ(void irqEXTI5Through9() noexcept);
WEAK_IRQ(void irqEXTI10Through15() noexcept);

WEAK_IRQ(void irqDMA1Channel1() noexcept);
WEAK_IRQ(void irqDMA1Channel2() noexcept);
WEAK_IRQ(void irqDMA1Channel3() noexcept);
WEAK_IRQ(void irqDMA1Channel4() noexcept);
WEAK_IRQ(void irqDMA1Channel5() noexcept);
WEAK_IRQ(void irqDMA1Channel6() noexcept);
WEAK_IRQ(void irqDMA1Channel7() noexcept);
WEAK_IRQ(void irqDMA2Channel1() noexcept);
WEAK_IRQ(void irqDMA2Channel2() noexcept);
WEAK_IRQ(void irqDMA2Channel3() noexcept);
WEAK_IRQ(void irqDMA2Channel4And5() noexcept);

WEAK_IRQ(void irqADC1And2() noexcept);
WEAK_IRQ(void irqADC3() noexcept);

WEAK_IRQ(void irqCANTxUSBHighPriority() noexcept);
WEAK_IRQ(void irqCANRx0USBLowPriority() noexcept);
WEAK_IRQ(void irqCANRx1() noexcept);
WEAK_IRQ(void irqCANSCE() noexcept);
WEAK_IRQ(void irqUSBWakeup() noexcept);

WEAK_IRQ(void irqTimer1Break() noexcept);
WEAK_IRQ(void irqTimer1Update() noexcept);
WEAK_IRQ(void irqTimer1TriggerComms() noexcept);
WEAK_IRQ(void irqTimer1CaptureCompare() noexcept);
WEAK_IRQ(void irqTimer2() noexcept);
WEAK_IRQ(void irqTimer3() noexcept);
WEAK_IRQ(void irqTimer4() noexcept);
WEAK_IRQ(void irqTimer5() noexcept);
WEAK_IRQ(void irqTimer6() noexcept);
WEAK_IRQ(void irqTimer7() noexcept);
WEAK_IRQ(void irqTimer8Break() noexcept);
WEAK_IRQ(void irqTimer8Update() noexcept);
WEAK_IRQ(void irqTimer8TriggerComms() noexcept);
WEAK_IRQ(void irqTimer8CaptureCompare() noexcept);

WEAK_IRQ(void irqI2C1Event() noexcept);
WEAK_IRQ(void irqI2C1Error() noexcept);
WEAK_IRQ(void irqI2C2Event() noexcept);
WEAK_IRQ(void irqI2C2Error() noexcept);

WEAK_IRQ(void irqSPI1() noexcept);
WEAK_IRQ(void irqSPI2() noexcept);
WEAK_IRQ(void irqSPI3() noexcept);

WEAK_IRQ(void irqUSART1() noexcept);
WEAK_IRQ(void irqUSART2() noexcept);
WEAK_IRQ(void irqUSART3() noexcept);
WEAK_IRQ(void irqUART4() noexcept);
WEAK_IRQ(void irqUART5() noexcept);

WEAK_IRQ(void irqWindowWDT() noexcept);
WEAK_IRQ(void irqProgVoltageDetector() noexcept);
WEAK_IRQ(void irqTamper() noexcept);
WEAK_IRQ(void irqRTC() noexcept);
WEAK_IRQ(void irqFlash() noexcept);
WEAK_IRQ(void irqRCC() noexcept);
WEAK_IRQ(void irqRTCAlarm() noexcept);
WEAK_IRQ(void irqFSMC() noexcept);
WEAK_IRQ(void irqSDIO() noexcept);
