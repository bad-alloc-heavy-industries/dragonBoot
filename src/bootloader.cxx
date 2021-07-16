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
	usb::dfu::detached(sysCtrl.resetCause | vals::sysCtrl::resetCauseSoftware);
	sysCtrl.resetCause = 0;
	usb::core::attach();

	while (true)
		__asm__("wfi");
}

void irqUSB() noexcept { usb::core::handleIRQ(); }
