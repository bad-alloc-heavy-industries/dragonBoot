// SPDX-License-Identifier: BSD-3-Clause
#include <array>
#include <usb/descriptors.hxx>
#include <usb/drivers/dfu.hxx>
#include "platform.hxx"

using namespace std::literals::string_view_literals;

namespace usb::descriptors
{
	const usbDeviceDescriptor_t deviceDescriptor
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
		3, // Serial string index
		configsCount
	};

	static const std::array<usbConfigDescriptor_t, configsCount> configDescs
	{{
		{
			sizeof(usbConfigDescriptor_t),
			usbDescriptor_t::configuration,
			sizeof(usbConfigDescriptor_t) + sizeof(usbInterfaceDescriptor_t) +
				sizeof(dfu::functionalDescriptor_t),
			interfaceCount,
			1, // This configuration
			4, // Configuration description string index
			usbConfigAttr_t::defaults,
			50 // 100mA (the max a typical SOT-23-5 3.3V regulator can reasonably provide)
		}
	}};

	const std::array<usbInterfaceDescriptor_t, interfaceDescriptorCount> interfaceDescriptors
	{{
		{
			sizeof(usbInterfaceDescriptor_t),
			usbDescriptor_t::interface,
			0, // Interface index 0
			0, // Alternate 0
			0, // No endpoints for this interface
			usbClass_t::application,
			uint8_t(subclasses::application_t::dfu),
			uint8_t(protocols::dfu_t::dfu),
			5, // "Device Firmware Upgrade interface" string index
		}
	}};

	static const dfu::functionalDescriptor_t dfuFunctionalDesc
	{
		sizeof(dfu::functionalDescriptor_t),
		dfu::descriptor_t::functional,
		{dfu::willDetach_t::yes, dfu::manifestationTolerant_t::no, dfu::canUpload_t::no, dfu::canDownload_t::yes},
		// Set the detach timeout to 1000ms which should be the upper bound for how long a PC takes to renumerate us
		1000,
		usb::dfu::flashPageSize, // Set the max transfer size to the size of a Flash page on the device
		0x0110 // This is 1.1 in USB's BCD format
	};

	static const std::array<usbMultiPartDesc_t, 3> configSecs
	{{
		{
			sizeof(usbConfigDescriptor_t),
			&configDescs[0]
		},
		{
			sizeof(usbInterfaceDescriptor_t),
			&interfaceDescriptors[0]
		},
		{
			sizeof(dfu::functionalDescriptor_t),
			&dfuFunctionalDesc
		}
	}};

#ifdef USB_MEM_SEGMENTED
	const std::array<flash_t<usbMultiPartTable_t>, configsCount> configDescriptors
	{{
		{{configSecs.begin(), configSecs.end()}}
	}};
#else
	const std::array<usbMultiPartTable_t, configsCount> configDescriptors
	{{
		{configSecs.begin(), configSecs.end()}
	}};
#endif

	static const std::array<usbStringDesc_t, stringCount> stringDescs
	{{
		{{u"bad_alloc Heavy Industries", 26}},
		{{u"dragonBoot DFU bootloader", 25}},
		{{serialNumber.data(), serialNumber.size()}},
		{{u"bootloader DFU configuration", 28}},
		{{u"Device Firmware Upgrade interface", 33}},
	}};

	static const std::array<std::array<usbMultiPartDesc_t, 2>, stringCount> stringParts
	{{
		stringDescs[0].asParts(),
		stringDescs[1].asParts(),
		stringDescs[2].asParts(),
		stringDescs[3].asParts(),
		stringDescs[4].asParts()
	}};

#ifdef USB_MEM_SEGMENTED
	const std::array<flash_t<usbMultiPartTable_t>, stringCount> strings
	{{
		{{stringParts[0].begin(), stringParts[0].end()}},
		{{stringParts[1].begin(), stringParts[1].end()}},
		{{stringParts[2].begin(), stringParts[2].end()}},
		{{stringParts[3].begin(), stringParts[3].end()}},
		{{stringParts[4].begin(), stringParts[4].end()}}
	}};
#else
	const std::array<usbMultiPartTable_t, stringCount> strings
	{{
		{stringParts[0].begin(), stringParts[0].end()},
		{stringParts[1].begin(), stringParts[1].end()},
		{stringParts[2].begin(), stringParts[2].end()},
		{stringParts[3].begin(), stringParts[3].end()},
		{stringParts[4].begin(), stringParts[4].end()}
	}};
#endif
} // namespace usb::descriptors
