// SPDX-License-Identifier: BSD-3-Clause
#include <usb/core.hxx>
#include <usb/drivers/dfu.hxx>
#include "platform.hxx"

void run() noexcept
{
	osc::init();
	usb::core::init();
	usb::dfu::registerHandlers({}, 1, 1);
	usb::core::attach();

	while (true)
		__asm__("wfi");
}

void irqUSB() noexcept { usb::core::handleIRQ(); }
