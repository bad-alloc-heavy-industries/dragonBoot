# SPDX-License-Identifier: BSD-3-Clause
# If you're looking for the target platforms this bootloader can be built for, look in platforms/
from torii.build import Platform
from torii.build.run import BuildPlan, BuildProducts, LocalBuildProducts
from torii.platform.vendor.lattice.ice40 import ICE40Platform
from abc import abstractmethod
from typing import Dict, Union

__all__ = (
	'Flash',
	'DragonICE40Platform',
	'platform'
)

sizeSuffixes = {
	0: 'B',
	1: 'kiB',
	2: 'MiB',
	3: 'GiB',
}

class Flash:
	""" The platform Flash configuration type. """
	def __init__(self, *, size : int, pageSize : int, erasePageSize : int, eraseCommand : int):
		"""
		Parameters
		----------
		size
			The total size, in bytes, of the SPI Flash on the target platform
		pageSize
			The size, in bytes, of a programable, readable page of Flash
		erasePageSize
			The size, in bytes, of an erase sector on the target Flash
		eraseCommand
			The numerical value of the command byte to send to the target Flash to erase a sector
		"""
		self.size = size
		self.pageSize = pageSize
		self.erasePageSize = erasePageSize
		self.eraseCommand = eraseCommand

	def platform(self, platform : Platform):
		""" Called during the initialisation of the platform, this calculates the slot information.

		The size of the bitstream and therefore of a slot cannot be derived without the platform instance the
		Flash instance is for, so initilisation of the object is two-stepped with this being the second step.
		"""
		assert isinstance(platform, Platform), 'platform must be derived from Platform'
		self._platform = platform

		self._calculateSlots()

	@property
	def slots(self) -> int:
		""" This property returns the number of configuration slots the Flash device has.

		Initially calculated when :py:member:platform is called, this can actually be overriden
		by the setter if one wishes to restrict the numeber of slots made available for any reason.
		Additionally, even if one tries to write a value outside the range of the Flash, this
		property ensures on retreival that a value in range is returned.
		"""
		usableSlots = self.size // self.slotSize
		slots = min(self._slots, usableSlots)
		assert slots > 1, f'Flash for platform has space for {slots} slots, need at least 2'
		return slots

	@slots.setter
	def slots(self, slots : int):
		assert slots >= 2, f'Flash slots cannot be set to less than 2, got {slots}'
		self._slots = slots

	@property
	def partitions(self) -> Dict[int, Dict[str, int]]:
		""" This property returns a dictionary describing the slot configuration Flash partioning.

		The dictionary returned is in the form::

			{
				slot: {
					'beginAddress': begin,
					'endAddress': end,
				}
			}
		"""
		partitions = {}
		beginAddress = self.erasePageSize
		for slot in range(self.slots):
			endAddress = self.slotSize if slot == 0 else beginAddress + self.slotSize
			partitions[slot] = {
				'beginAddress': beginAddress,
				'endAddress': endAddress
			}
			if slot == 0:
				beginAddress = self.slotSize
			else:
				beginAddress += self.slotSize
		return partitions

	@property
	def humanSize(self) -> str:
		""" Gets the Flash total size expressed in human readable units. """
		size = self.size
		iters = 0
		while size > 1024:
			iters += 1
			size /= 1024
		return f'{size}{sizeSuffixes[iters]}'

	def _calculateSlots(self):
		if isinstance(self._platform, ICE40Platform):
			self.slots = 4
			if (self._platform.device == 'iCE40HX8K' or self._platform.device == 'iCE40HX4K' or
	   			self._platform.device == 'iCE40LP8K' or self._platform.device == 'iCE40LP4K'):
				self.slotSize = 2 ** 18
			elif self._platform.device == 'iCE40UP5K' or self._platform.device == 'iCE40UP3K':
				self.slotSize = 2 ** 17
			else:
				raise NotImplementedError(f'iCE40 device {self._platform.device} not yet implemented')
		else:
			self.slots = 2
			raise NotImplementedError('I don\'t know how to size the slots on this platform')

class DragonICE40Platform(ICE40Platform):
	""" This is the base platform for all Lattice iCE40 bootloaders.

	This platform defines how to build a multi-boot Flash image on top of the normal bitstream building logic.
	It also includes logic required to enforce the presence and facilitate retrieval of Flash descriptor objects.
	"""

	@property
	@abstractmethod
	def flash(self) -> Flash:
		""" A :py:class:`Flash configuration <dragonBoot.platform.Flash>` describing the targets FPGA configuration Flash. """
		return self._flash

	@flash.setter
	def flash(self, value : Flash):
		assert isinstance(value, Flash), f'flash property must be populated with a Flash object, got {type(value)}'
		self._flash = value

	def __init__(self, toolchain = 'IceStorm'):
		"""
		Parameters
		----------
		toolchain
			Which toolchain synthesis, placement and routing should be performed via.
			Unless you have extremely good reason to do otherwise, the default IceStorm
			should be used.
		"""
		super().__init__(toolchain = toolchain)
		self.flash.platform(self)

	def build(self, elaboratable, name = "top", build_dir = "build", do_build = True,
		program_opts = None, do_program = False, pnrSeed = 0, **kwargs
	) -> Union[BuildPlan, BuildProducts, None]:
		""" This is called automatically by the bootloader CLI.

		This function builds both the upgrade bitstream, and the initial Flash layout to be
		written by either `SPIFlashProgrammer <https://github.com/bad-alloc-heavy-industries/SPIFlashProgrammer>`_,
		or any other tool capable of writing a raw Flash image to a target device.

		Once the upgrade bitstream has been created, this: builds the multi-boot slot
		configuration page; appends the upgrade bitstream in its proper location; pads
		out to the start of the next slot after; and, finally places a short bitstream there
		which instructs the FPGA to warmboot into the bootloader slot. This is done so that
		unconfigured devices enter the bootloader automatically untill written with a valid bitstream.

		Once building this initial Flash image has been built, this will (optionally) program the initial
		Flash image to a target device per your specification using the function :py:meth:`self.toolchain_program`.
		"""
		products : LocalBuildProducts = super().build(
			elaboratable, name, build_dir, do_build, do_program = False,
			synth_opts = '-abc9', nextpnr_opts = ['--tmg-ripup', f'--seed={pnrSeed}'],
			**kwargs
		)

		# Build the multi-boot bitstreams image to go along with the upgrade bitstream
		with open(f'{build_dir}/{name}.multi.bin', 'wb') as multiboot:
			# Build and write the slot data and first slot
			slotData = self.buildSlots()
			multiboot.write(slotData)
			multiboot.write(products.get(f'{name}.bin'))
			# Pad out to the start of the second slot
			begin = multiboot.tell()
			end = self.flash.partitions[1]['beginAddress']
			for _ in range(begin, end):
				multiboot.write(b'\xFF')
			# Grab a copy of the bootloader boot entry
			multiboot.write(slotData[32:64])

		if not do_program:
			return products
		self.toolchain_program(products, name, **(program_opts or {}))

	def buildSlots(self) -> bytes:
		""" Builds a multi-boot slot configuration for the platform.

		This first builds the slot configuration block that must sit at the start of Flash
		and then follows it with unset Flash (:code:`0xFF`) byte padding till we meet the
		end of the first Flash sector erase page where the dragonBoot warmboot slot begins.

		For further details on the inner workings, see :py:class:`dragonBoot.ice40.Slots`.
		"""
		from .ice40 import Slots
		slotData = bytearray(self.flash.erasePageSize)
		slots = Slots(self.flash).build()
		slotData[0:len(slots)] = slots
		for byte in range(len(slots), self.flash.erasePageSize):
			slotData[byte] = 0xFF
		return bytes(slotData)

def platform(cls):
	cls._dragonPlatform = True
	return cls
