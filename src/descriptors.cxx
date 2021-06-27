// SPDX-License-Identifier: BSD-3-Clause
#include <array>
#include <usb/descriptors.hxx>
#include "constants.hxx"

using namespace usb::constants;
using namespace usb::types;
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
	0, // No serial number string
	configsCount
};

static const std::array<usbConfigDescriptor_t, configsCount> usbConfigDesc
{{
	{
		sizeof(usbConfigDescriptor_t),
		usbDescriptor_t::configuration,
		sizeof(usbConfigDescirptor_t) + sizeof(usbInterfaceDescriptor_t) +
			sizeof(dfu::functionalDescriptor_t),
		interfaceCount,
		1, // This configuration
		3, // Configuration description string index
		usbConfigAttr_t::defaults,
		50 // 100mA (the max a typical SOT-23-5 3.3V regulator can reasonably provide)
	}
}};

static const std::array<usbInterfaceDescriptor_t, interfaceDescriptorCount> usbInterfaceDesc
{{
	{
		sizeof(usbInterfaceDescriptor_t),
		usbDescriptor_t::interface,
		0, // Interface index 0
		0, // Alternate 0
		0, // No endpoints for this interface
		usbClass_t::application,
		uint8_t(subclasses::applicaiton_t::dfu),
		uint8_t(protocols::application_t::runtime),
		4, // "Device Firmware Upgrade interface" string index
	}
}};

static const dfu::functionalDescriptor_t usbDFUFunctionalDesc
{
	sizeof(dfu::functionalDescriptor_t),
	dfu::descriptor_t::functional,
	{dfu::willDetach_t::yes, dfu::manifestationTolerant_t::no, dfu::canUpload_t::no, dfu::canDownload_t::yes},
	10, // Set the detach timeout to 10ms
	epBufferSize, // Set the max transfer size to the endpoint buffer size
	0x011A // Tis is 1.1a in USB's BCD format
};

static const std::array<usbMultiPartDesc_t, 6> usbConfigSecs
{{
	{
		sizeof(usbConfigDescriptor_t),
		&usbConfigDesc[0]
	},
	{
		sizeof(usbInterfaceDescriptor_t),
		&usbInterfaceDesc[0]
	},
	{
		sizeof(dfu::functionalDescriptor_t),
		&usbDFUFunctionalDesc
	}
}};

namespace usb::descriptors
{
	const std::array<usbMultiPartTable_t, configsCount> usbConfigDescriptors
	{{
		{usbConfigSecs.begin(), usbConfigSecs.end()}
	}};
} // namespace usb::descriptors

static const std::array<usbStringDesc_t, stringCount + 1U> usbStringDescs
{{
	{{u"\x0904", 1}},
	{{u"bad_alloc Heavy Industries", 26}},
	{{u"dragonUSB DFU bootloader", 24}},
	{{u"bootloader DFU configuration", 28}},
	{{u"Device Firmware Upgrade interface", 33}},
}};

static const std::array<std::array<usbMultiPartDesc_t, 2>, stringCount + 1U> usbStringParts
{{
	usbStringDescs[0].asParts(),
	usbStringDescs[1].asParts(),
	usbStringDescs[2].asParts(),
	usbStringDescs[3].asParts(),
	usbStringDescs[4].asParts()
}};

static const std::array<usbMultiPartTable_t, stringCount + 1U> usbStrings
{{
	{usbStringParts[0].begin(), usbStringParts[0].end()},
	{usbStringParts[1].begin(), usbStringParts[1].end()},
	{usbStringParts[2].begin(), usbStringParts[2].end()},
	{usbStringParts[3].begin(), usbStringParts[3].end()},
	{usbStringParts[4].begin(), usbStringParts[4].end()},
}};
