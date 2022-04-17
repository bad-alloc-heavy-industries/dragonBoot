# SPDX-License-Identifier: BSD-3-Clause
# If you're looking for the target platforms this bootloader can be built for, look in platforms/
from amaranth.build import Platform
from amaranth.build.run import LocalBuildProducts
from amaranth.vendor.lattice_ice40 import LatticeICE40Platform
from abc import abstractmethod
from typing import Dict, Type

__all__ = (
	'Flash',
	'DragonICE40Platform',
)

sizeSuffixes = {
	0: 'B',
	1: 'kiB',
	2: 'MiB',
	3: 'GiB',
}

class Flash:
	def __init__(self, *, size : int, pageSize : int, erasePageSize : int, eraseCommand : int):
		self.size = size
		self.pageSize = pageSize
		self.erasePageSize = erasePageSize
		self.eraseCommand = eraseCommand

	def platform(self, platform : Type):
		assert isinstance(platform, Platform), 'platform must be derived from Platform'
		self._platform = platform

		self._calculateSlots()

	@property
	def slots(self) -> int:
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
		size = self.size
		iters = 0
		while size > 1024:
			iters += 1
			size /= 1024
		return f'{size}{sizeSuffixes[iters]}'

	def _calculateSlots(self):
		if isinstance(self._platform, LatticeICE40Platform):
			self.slots = 4
			if self._platform.device == 'iCE40HX8K' or self._platform.device == 'iCE40HX4K':
				self.slotSize = 2 ** 18
			elif self._platform.device == 'iCE40UP5K' or self._platform.device == 'iCE40UP3K':
				self.slotSize = 2 ** 17
			else:
				raise NotImplementedError(f'iCE40 device {self._platform.device} not yet implemented')
		else:
			self.slots = 2
			raise NotImplementedError('I don\'t know how to size the slots on this platform')

class DragonICE40Platform(LatticeICE40Platform):
	@property
	@abstractmethod
	def flash(self) -> Flash:
		return self._flash

	@flash.setter
	def flash(self, value : Flash):
		assert isinstance(value, Flash), f'flash property must be populated with a Flash object, got {type(value)}'
		self._flash = value

	def __init__(self, toolchain = 'IceStorm'):
		super().__init__(toolchain = toolchain)
		self.flash.platform(self)

	def build(self, elaboratable, name = "top", build_dir = "build", do_build = True,
		program_opts = None, do_program = False, **kwargs
	):
		products : LocalBuildProducts = super().build(elaboratable, name, build_dir, do_build, do_program = False, **kwargs)
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

	def buildSlots(self):
		from .ice40 import Slots
		slotData = bytearray(self.flash.erasePageSize)
		slots = Slots(self.flash).build()
		slotData[0:len(slots)] = slots
		for byte in range(len(slots), self.flash.erasePageSize):
			slotData[byte] = 0xFF
		return bytes(slotData)
