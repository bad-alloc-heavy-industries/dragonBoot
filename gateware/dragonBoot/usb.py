# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module
from luna.usb2 import USBDevice
from luna.gateware.usb.request import SetupPacket
from luna.gateware.usb.usb2.request import StallOnlyRequestHandler
from usb_protocol.types import USBRequestType
from usb_protocol.emitters.descriptors.standard import (
	DeviceDescriptorCollection, LanguageIDs, DeviceClassCodes, InterfaceClassCodes,
	ApplicationSubclassCodes, DFUProtocolCodes
)
from usb_protocol.types.descriptors.dfu import *
from usb_protocol.contextmgrs.descriptors.dfu import *
from usb_protocol.types.descriptors.microsoft import *
from usb_protocol.emitters.descriptors.microsoft import PlatformDescriptorCollection
from usb_protocol.contextmgrs.descriptors.microsoft import *

from .dfu import DFURequestHandler
from .windows import WindowsRequestHandler
from .warmboot import Warmboot

__all__ = (
	'USBInterface',
)

class USBInterface(Elaboratable):
	def __init__(self, *, resource, dfuResource):
		self._ulpiResource = resource
		self._dfuResource = dfuResource

	def elaborate(self, platform) -> Module:
		m = Module()
		self.ulpiInterface = platform.request(*self._ulpiResource)
		m.submodules.device = device = USBDevice(bus = self.ulpiInterface, handle_clocking = True)
		m.submodules.warmboot = warmboot = Warmboot()

		descriptors = DeviceDescriptorCollection()
		with descriptors.DeviceDescriptor() as deviceDesc:
			deviceDesc.bcdUSB = 2.01
			deviceDesc.bDeviceClass = DeviceClassCodes.INTERFACE
			deviceDesc.bDeviceSubclass = 0
			deviceDesc.bDeviceProtocol = 0
			deviceDesc.idVendor = 0x1209
			deviceDesc.idProduct = 0xBADB
			deviceDesc.bcdDevice = 0.02
			deviceDesc.iManufacturer = 'bad_alloc Heavy Industries'
			deviceDesc.iProduct = 'dragonBoot DFU bootloader'
			deviceDesc.bNumConfigurations = 1

		with descriptors.ConfigurationDescriptor() as configDesc:
			configDesc.bConfigurationValue = 1
			configDesc.iConfiguration = 'bootloader DFU configuration'
			# Bus powered with no remote wakeup support
			configDesc.bmAttributes = 0x80
			# 1000mA max.
			configDesc.bMaxPower = 50

			with configDesc.InterfaceDescriptor() as interfaceDesc:
				interfaceDesc.bInterfaceNumber = 0
				interfaceDesc.bAlternateSetting = 0
				interfaceDesc.bInterfaceClass = InterfaceClassCodes.APPLICATION
				interfaceDesc.bInterfaceSubclass = ApplicationSubclassCodes.DFU
				interfaceDesc.bInterfaceProtocol = DFUProtocolCodes.DFU
				interfaceDesc.iInterface = 'Device Firmware Upgrade interface'

				with FunctionalDescriptor(interfaceDesc) as functionalDesc:
					functionalDesc.bmAttributes = (
						DFUWillDetach.YES | DFUManifestationTollerant.NO | DFUCanUpload.NO | DFUCanDownload.YES
					)
					functionalDesc.wDetachTimeOut = 1000
					functionalDesc.wTransferSize = platform.flash.erasePageSize

		platformDescriptors = PlatformDescriptorCollection()
		with descriptors.BOSDescriptor() as bos:
			with PlatformDescriptor(bos, platform_collection = platformDescriptors) as platformDesc:
				with platformDesc.DescriptorSetInformation() as descSetInfo:
					descSetInfo.bMS_VendorCode = 1

					with descSetInfo.SetHeaderDescriptor() as setHeader:
						with setHeader.SubsetHeaderConfiguration() as subsetConfig:
							subsetConfig.bConfigurationValue = 1

							with subsetConfig.SubsetHeaderFunction() as subsetFunc:
								subsetFunc.bFirstInterface = 0

								with subsetFunc.FeatureCompatibleID() as compatID:
									compatID.CompatibleID = 'WINUSB'
									compatID.SubCompatibleID = ''

		descriptors.add_language_descriptor((LanguageIDs.ENGLISH_US, ))
		ep0 = device.add_standard_control_endpoint(descriptors)
		dfuRequestHandler = DFURequestHandler(interface = 0, resource = self._dfuResource)
		windowsRequestHandler = WindowsRequestHandler(platformDescriptors)

		def stallCondition(setup : SetupPacket):
			return ~(
				(setup.type == USBRequestType.STANDARD) |
				dfuRequestHandler.handlerCondition(setup) |
				windowsRequestHandler.handlerCondition(setup)
			)

		ep0.add_request_handler(dfuRequestHandler)
		ep0.add_request_handler(windowsRequestHandler)
		ep0.add_request_handler(StallOnlyRequestHandler(stall_condition = stallCondition))

		# Signal that we always want LUNA to try connecting
		m.d.comb += [
			device.connect.eq(1),
			device.low_speed_only.eq(0),
			device.full_speed_only.eq(0),
			warmboot.trigger.eq(dfuRequestHandler.triggerReboot),
		]
		return m
