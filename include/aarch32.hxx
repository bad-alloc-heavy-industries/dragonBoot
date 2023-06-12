// SPDX-License-Identifier: BSD-3-Clause
#ifndef AARCH32_HXX
#define AARCH32_HXX

// NOLINTNEXTLINE(cppcoreguidelines-macro-usage)
#define WEAK_IRQ(function) [[gnu::weak, gnu::alias("irqEmptyDef")]] function

// Unused IRQ function
extern "C" void irqEmptyDef() noexcept;

// Core system handlers
void irqReset() noexcept;
void irqNMI() noexcept;
[[gnu::naked]] void irqHardFault() noexcept;

// Configurable priority system handlers
void irqMMUFault() noexcept;
void irqBusFault() noexcept;
void irqUsageFault() noexcept;
void irqServiceCall() noexcept;
void irqDebugMonitor() noexcept;
void irqPendingServiceCall() noexcept;
void irqSysTick() noexcept;

#endif /*AARCH32_HXX*/
