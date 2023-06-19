// SPDX-License-Identifier: BSD-3-Clause
#include <usb/core.hxx>
#include "platform.hxx"

void run() noexcept
{
	osc::init();
	if (!mustEnterBootloader())
		rebootToFirmware();
	usb::core::init();
	usb::dfu::registerHandlers(firmwareZone, 0, 1);
	usb::dfu::detached(true);
	readSerialNumber();
	usb::core::attach();
	enableInterrupts();

	while (true)
		idle();
}
