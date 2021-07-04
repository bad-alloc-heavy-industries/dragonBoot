// SPDX-License-Identifier: BSD-3-Clause
#ifndef PLATFORM__HXX
#define PLATFORM__HXX

extern void run() noexcept;
extern void irqUSB() noexcept;

namespace osc { extern void init() noexcept; }

extern bool mustEnterBootloader() noexcept;
[[noreturn]] extern void rebootToFirmware() noexcept;

#endif /*PLATFORM__HXX*/
