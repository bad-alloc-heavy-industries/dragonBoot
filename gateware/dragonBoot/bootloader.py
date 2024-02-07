# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module, Signal, ClockDomain, ResetSignal
from torii.build import Platform
from sol_usb.usb2 import USBDevice
from usb_construct.emitters.descriptors.standard import (
	DeviceDescriptorCollection, LanguageIDs, DeviceClassCodes, InterfaceClassCodes,
	ApplicationSubclassCodes, DFUProtocolCodes
)
from usb_construct.types.descriptors.dfu import *
from usb_construct.contextmgrs.descriptors.dfu import *
from usb_construct.types.descriptors.microsoft import *
from usb_construct.emitters.descriptors.microsoft import PlatformDescriptorCollection
from usb_construct.contextmgrs.descriptors.microsoft import *

from .dfu import DFURequestHandler
from .windows import WindowsRequestHandler
from .warmboot import Warmboot
from .timeout import ConnectTimeout

__all__ = (
	'DragonBoot',
)

class DragonBoot(Elaboratable):
	""" The top-level of the dragonBoot gateware and implementation of the descriptors and SOL USB device.

	This top-level :py:class:`amaranth.hdl.ir.Elaboratable` does a few things, some of which are described in
	detail in other sections of the documentation:

	* It implements the :doc:`USB descriptors </gateware/descriptors>` required to tell the host what we are.
	* It houses the SOL USB device instance used to communicate with the host.
	* It houses and connects the platform-specific warmboot block needed to reboot and reconfigure the FPGA
	  on completion of operations.
	* It connects up and provides to the SOL USB device all the handlers required for USB endpoint 0 to work
	  and respond as needed to requests from the host.

	The SOL USB device uses what is ostensibly an ULPI interface, however it is possible to instead use a raw
	USB LS/FS interface even on a device such as the Lattice iCE40UP5K which is unable to work at ULPI speeds.
	We configure by default for the :py:class:`sol.gateware.usb.usb2.device.USBDevice` to connect in high speed
	mode and define the :code:`usb` clock domain, while SOL handles setting up clocking that domain appropriately.
	"""
	def elaborate(self, platform: Platform) -> Module:
		""" Describes the specific gateware needed to provide the descriptors and handlers and device logic to talk USB.

		Parameters
		----------
		platform
			The Amaranth platform for which the gateware will be synthesised.

		Returns
		-------
		:py:class:`amaranth.hdl.dsl.Module`
			A complete description of the gateware behaviour required.
		"""
		m = Module()
		if ('ulpi', 0) in platform.resources:
			m.domains.usb = ClockDomain()
			ulpiInterface = platform.request('ulpi', 0)
			m.submodules.device = device = USBDevice(bus = ulpiInterface, handle_clocking = True)
		elif ('usb', 0) in platform.resources:
			if not hasattr(platform, 'pll_type'):
				raise AssertionError('Platform does not define an implementation for a PLL to clock it')
			pllType = platform.pll_type
			m.submodules.clocking = pllType()
			usbInterface = platform.request('usb', 0)
			m.submodules.device = device = USBDevice(bus = usbInterface, handle_clocking = False)
		else:
			raise AssertionError('Platform fails to define any valid USB resources!')
		m.submodules.warmboot = warmboot = Warmboot()

		descriptors = DeviceDescriptorCollection()
		with descriptors.DeviceDescriptor() as deviceDesc:
			deviceDesc.bcdUSB = 2.01
			deviceDesc.bDeviceClass = DeviceClassCodes.INTERFACE
			deviceDesc.bDeviceSubclass = 0
			deviceDesc.bDeviceProtocol = 0
			deviceDesc.idVendor = 0x1209
			deviceDesc.idProduct = 0xBADB
			deviceDesc.bcdDevice = 0.03
			deviceDesc.iManufacturer = 'bad_alloc Heavy Industries'
			deviceDesc.iProduct = 'dragonBoot DFU bootloader'
			deviceDesc.bNumConfigurations = 1

		with descriptors.ConfigurationDescriptor() as configDesc:
			configDesc.bConfigurationValue = 1
			configDesc.iConfiguration = 'bootloader DFU configuration'
			# Bus powered with no remote wakeup support
			configDesc.bmAttributes = 0x80
			# 100mA max.
			configDesc.bMaxPower = 50

			for slot in platform.flash.partitions:
				with configDesc.InterfaceDescriptor() as interfaceDesc:
					interfaceDesc.bInterfaceNumber = 0
					interfaceDesc.bAlternateSetting = slot
					interfaceDesc.bInterfaceClass = InterfaceClassCodes.APPLICATION
					interfaceDesc.bInterfaceSubclass = ApplicationSubclassCodes.DFU
					interfaceDesc.bInterfaceProtocol = DFUProtocolCodes.DFU
					interfaceDesc.iInterface = f'DFU interface for slot {slot}'

					with FunctionalDescriptor(interfaceDesc) as functionalDesc:
						functionalDesc.bmAttributes = (
							DFUWillDetach.YES | DFUManifestationTolerant.NO | DFUCanUpload.NO | DFUCanDownload.YES
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

		dfuRequestHandler = DFURequestHandler(configuration = 1, interface = 0, resource = ('flash_spi', 0))
		ep0.add_request_handler(dfuRequestHandler)

		ep0.add_request_handler(WindowsRequestHandler(platformDescriptors))

		if hasattr(platform, 'timeout'):
			rebootTrigger = Signal()
			m.submodules.timeout = timeout = ConnectTimeout(timeout = platform.timeout, clockFreq = device.data_clock)
			m.d.comb += [
				timeout.stop.eq(device.reset_detected),
				rebootTrigger.eq(dfuRequestHandler.triggerReboot | timeout.triggerReboot),
			]
		else:
			rebootTrigger = dfuRequestHandler.triggerReboot

		# Signal that we always want LUNA to try connecting
		m.d.comb += [
			device.connect.eq(1),
			device.low_speed_only.eq(0),
			device.full_speed_only.eq(0),
			ResetSignal('usb').eq(0),
			warmboot.trigger.eq(rebootTrigger),
		]
		return m
