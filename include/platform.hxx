// SPDX-License-Identifier: BSD-3-Clause
#ifndef PLATFORM__HXX
#define PLATFORM__HXX

#include <usb/drivers/dfu.hxx>

extern const std::array<usb::dfu::zone_t, 1> firmwareZone;

extern void run() noexcept;
extern void enableInterrupts() noexcept;
extern void idle() noexcept;
namespace osc { extern void init() noexcept; }

extern bool mustEnterBootloader() noexcept;
[[noreturn]] extern void rebootToFirmware() noexcept;

#endif /*PLATFORM__HXX*/
