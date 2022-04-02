from amaranth import Elaboratable, Module
from luna.usb2 import USBDevice
from usb_protocol.emitters.descriptors.standard import (
	DeviceDescriptorCollection, LanguageIDs, DeviceClassCodes, InterfaceClassCodes,
	ApplicationSubclassCodes, DFUProtocolCodes
)
from usb_protocol.types.descriptors.dfu import *
from usb_protocol.contextmgrs.descriptors.dfu import *

__all__ = (
	'USBInterface',
)

class USBInterface(Elaboratable):
	def __init__(self, *, resource):
		self._ulpiResource = resource

	def elaborate(self, platform):
		m = Module()
		self.ulpiInterface = platform.request(*self._ulpiResource)
		m.submodules.device = device = USBDevice(bus = self.ulpiInterface, handle_clocking = True)

		descriptors = DeviceDescriptorCollection()
		with descriptors.DeviceDescriptor() as deviceDesc:
			deviceDesc.bDeviceClass = DeviceClassCodes.INTERFACE
			deviceDesc.bDeviceSubclass = 0
			deviceDesc.bDeviceProtocol = 0
			deviceDesc.idVendor = 0x1209
			deviceDesc.idProduct = 0xBADB
			deviceDesc.bcdDevice = 0.01
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
					functionalDesc.wTransferSize = platform.flashPageSize

		descriptors.add_language_descriptor((LanguageIDs.ENGLISH_US, ))
		ep0 = device.add_standard_control_endpoint(descriptors)


		# Signal that we always want LUNA to try connecting
		m.d.comb += [
			device.connect.eq(1),
			device.low_speed_only.eq(0),
			device.full_speed_only.eq(0),
		]
		return m
