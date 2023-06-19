// SPDX-License-Identifier: BSD-3-Clause
#ifndef PLATFORM__HXX
#define PLATFORM__HXX

#include <usb/drivers/dfu.hxx>
#include "constants.hxx"

extern const std::array<usb::dfu::zone_t, 1> firmwareZone;
extern std::array<char16_t, serialLength> serialNumber;

void run() noexcept;
void enableInterrupts() noexcept;
void idle() noexcept;
namespace osc { void init() noexcept; }

void readSerialNumber() noexcept;
bool mustEnterBootloader() noexcept;
[[noreturn]] void rebootToFirmware() noexcept;

#endif /*PLATFORM__HXX*/
