// SPDX-License-Identifier: BSD-3-Clause
#ifndef TM4C123GH6PM_HXX
#define TM4C123GH6PM_HXX

#include "aarch32.hxx"

void irqGPIOPortA() noexcept;
void irqGPIOPortB() noexcept;
void irqGPIOPortC() noexcept;
void irqGPIOPortD() noexcept;
void irqGPIOPortE() noexcept;
void irqGPIOPortF() noexcept;
void irqGPIOPortG() noexcept;
void irqGPIOPortH() noexcept;
void irqGPIOPortJ() noexcept;
void irqGPIOPortK() noexcept;
void irqGPIOPortL() noexcept;
void irqGPIOPortM() noexcept;
void irqGPIOPortN() noexcept;
void irqGPIOPortR() noexcept;
void irqGPIOPortS() noexcept;

void irqGPIOPortP0() noexcept;
void irqGPIOPortP1() noexcept;
void irqGPIOPortP2() noexcept;
void irqGPIOPortP3() noexcept;
void irqGPIOPortP4() noexcept;
void irqGPIOPortP5() noexcept;
void irqGPIOPortP6() noexcept;
void irqGPIOPortP7() noexcept;

void irqGPIOPortQ0() noexcept;
void irqGPIOPortQ1() noexcept;
void irqGPIOPortQ2() noexcept;
void irqGPIOPortQ3() noexcept;
void irqGPIOPortQ4() noexcept;
void irqGPIOPortQ5() noexcept;
void irqGPIOPortQ6() noexcept;
void irqGPIOPortQ7() noexcept;

void irqUART0() noexcept;
void irqUART1() noexcept;
void irqUART2() noexcept;
void irqUART3() noexcept;
void irqUART4() noexcept;
void irqUART5() noexcept;
void irqUART6() noexcept;
void irqUART7() noexcept;

void irqSSI0() noexcept;
void irqSSI1() noexcept;
void irqSSI2() noexcept;
void irqSSI3() noexcept;

void irqI2C0() noexcept;
void irqI2C1() noexcept;
void irqI2C2() noexcept;
void irqI2C3() noexcept;
void irqI2C4() noexcept;
void irqI2C5() noexcept;

void irqPWM0Fault() noexcept;
void irqPWM0Gen0() noexcept;
void irqPWM0Gen1() noexcept;
void irqPWM0Gen2() noexcept;
void irqPWM0Gen3() noexcept;
void irqPWM1Fault() noexcept;
void irqPWM1Gen0() noexcept;
void irqPWM1Gen1() noexcept;
void irqPWM1Gen2() noexcept;
void irqPWM1Gen3() noexcept;

void irqQEI0() noexcept;
void irqQEI1() noexcept;
void irqQEI2() noexcept;

void irqADC0Seq0() noexcept;
void irqADC0Seq1() noexcept;
void irqADC0Seq2() noexcept;
void irqADC0Seq3() noexcept;
void irqADC1Seq0() noexcept;
void irqADC1Seq1() noexcept;
void irqADC1Seq2() noexcept;
void irqADC1Seq3() noexcept;

void irqTimer0A() noexcept;
void irqTimer0B() noexcept;
void irqTimer1A() noexcept;
void irqTimer1B() noexcept;
void irqTimer2A() noexcept;
void irqTimer2B() noexcept;
void irqTimer3A() noexcept;
void irqTimer3B() noexcept;
void irqTimer4A() noexcept;
void irqTimer4B() noexcept;
void irqTimer5A() noexcept;
void irqTimer5B() noexcept;

void irqWideTimer0A() noexcept;
void irqWideTimer0B() noexcept;
void irqWideTimer1A() noexcept;
void irqWideTimer1B() noexcept;
void irqWideTimer2A() noexcept;
void irqWideTimer2B() noexcept;
void irqWideTimer3A() noexcept;
void irqWideTimer3B() noexcept;
void irqWideTimer4A() noexcept;
void irqWideTimer4B() noexcept;
void irqWideTimer5A() noexcept;
void irqWideTimer5B() noexcept;

void irqComp0() noexcept;
void irqComp1() noexcept;
void irqComp2() noexcept;

void irqCAN0() noexcept;
void irqCAN1() noexcept;
void irqCAN2() noexcept;

void irqUDMASoftwareComplete() noexcept;
void irqUDMAError() noexcept;

void irqWDT() noexcept;
void irqSysCtl() noexcept;
void irqNVMCtrl() noexcept;
void irqHibernation() noexcept;
void irqUSB() noexcept;
void irqFPU() noexcept;

#endif /*TM4C123GH6PM_HXX*/
