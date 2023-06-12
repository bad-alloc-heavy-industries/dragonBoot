// SPDX-License-Identifier: BSD-3-Clause
#ifndef STM32F1_HXX
#define STM32F1_HXX

#include "aarch32.hxx"

void irqEXTI0() noexcept;
void irqEXTI1() noexcept;
void irqEXTI2() noexcept;
void irqEXTI3() noexcept;
void irqEXTI4() noexcept;
void irqEXTI5Through9() noexcept;
void irqEXTI10Through15() noexcept;

void irqDMA1Channel1() noexcept;
void irqDMA1Channel2() noexcept;
void irqDMA1Channel3() noexcept;
void irqDMA1Channel4() noexcept;
void irqDMA1Channel5() noexcept;
void irqDMA1Channel6() noexcept;
void irqDMA1Channel7() noexcept;
void irqDMA2Channel1() noexcept;
void irqDMA2Channel2() noexcept;
void irqDMA2Channel3() noexcept;
void irqDMA2Channel4And5() noexcept;

void irqADC1And2() noexcept;
void irqADC3() noexcept;

void irqCANTxUSBHighPriority() noexcept;
void irqCANRx0USBLowPriority() noexcept;
void irqCANRx1() noexcept;
void irqCANSCE() noexcept;
void irqUSBWakeup() noexcept;

void irqTimer1Break() noexcept;
void irqTimer1Update() noexcept;
void irqTimer1TriggerComms() noexcept;
void irqTimer1CaptureCompare() noexcept;
void irqTimer2() noexcept;
void irqTimer3() noexcept;
void irqTimer4() noexcept;
void irqTimer5() noexcept;
void irqTimer6() noexcept;
void irqTimer7() noexcept;
void irqTimer8Break() noexcept;
void irqTimer8Update() noexcept;
void irqTimer8TriggerComms() noexcept;
void irqTimer8CaptureCompare() noexcept;

void irqI2C1Event() noexcept;
void irqI2C1Error() noexcept;
void irqI2C2Event() noexcept;
void irqI2C2Error() noexcept;

void irqSPI1() noexcept;
void irqSPI2() noexcept;
void irqSPI3() noexcept;

void irqUSART1() noexcept;
void irqUSART2() noexcept;
void irqUSART3() noexcept;
void irqUART4() noexcept;
void irqUART5() noexcept;

void irqWindowWDT() noexcept;
void irqProgVoltageDetector() noexcept;
void irqTamper() noexcept;
void irqRTC() noexcept;
void irqFlash() noexcept;
void irqRCC() noexcept;
void irqRTCAlarm() noexcept;
void irqFSMC() noexcept;
void irqSDIO() noexcept;

#endif /*STM32F1_HXX*/
