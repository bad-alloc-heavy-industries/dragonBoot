// SPDX-License-Identifier: BSD-3-Clause
#include <usb/descriptors.hxx>
#include "constants.hxx"

using namespace usb::descriptors;
using namespace std::literals::string_view_literals;

static const usbDeviceDescriptor_t usbDeviceDesc
{
	sizeof(usbDeviceDescriptor_t),
	usbDescriptor_t::device,
	0x0200, // This is 2.00 in USB's BCD format
	usbClass_t::none,
	uint8_t(subclasses::device_t::none),
	uint8_t(protocols::device_t::none),
	epBufferSize,
	vid,
	pid,
	0x0001, // BCD encoded device version
	1, // Manufacturer string index
	2, // Product string index
	0, // Temporarily do not support a serial number string
	configsCount
};
