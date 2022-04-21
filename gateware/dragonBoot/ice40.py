# SPDX-License-Identifier: BSD-3-Clause
import logging
import construct
from construct import this
from enum import IntEnum, IntFlag, unique
from typing import Dict, List

from .platform import Flash

__all__ = (
	'Slots',
)

@unique
class Opcodes(IntEnum):
	"""Opcodes for operations the bitstream can request of the FPGA"""
	Special = 0
	BankNumber = 1
	CRCCheck = 2
	BootAddress = 4
	InternalOscRange = 5
	BankWidth = 6
	BankHeight = 7
	BankOffset = 8
	BootMode = 9

@unique
class SpecialOpcodes(IntEnum):
	"""Opcodes requested via :py:attr:`Opcodes.Special`"""
	CRAMData = 1
	BRAMData = 3
	ResetCRC = 5
	Wakeup = 6
	Reboot = 8

@unique
class BootModes(IntFlag):
	"""Boot mode bits that can be or'd together"""
	SimpleBoot = 0
	ColdBoot = 16
	WarmBoot = 32

Special = construct.Struct(
	'operation' / construct.Enum(construct.Int8ub, SpecialOpcodes),
)

BootMode = construct.Struct(
	'reserved' / construct.Const(0, construct.Int8ub),
	'mode'     / construct.FlagsEnum(construct.Int8ub, BootModes),
)

BankOffset = construct.Struct(
	'offset' / construct.Int16ub
)

BootAddress = construct.Struct(
	'addressLength' / construct.Const(3, construct.Int8ub),
	'address'       / construct.Int24ub,
)

Payload = construct.Switch(
	this.instruction,
	cases = {
		Opcodes.Special: Special,
		Opcodes.BootAddress: BootAddress,
		Opcodes.BankOffset: BankOffset,
		Opcodes.BootMode: BootMode,
	},
)

Instruction = construct.BitStruct(
	'instruction' / construct.Enum(construct.Nibble, Opcodes),
	construct.StopIf(this.instruction == 0xF),
	'byteCount'   / construct.Rebuild(construct.Nibble, lambda this: this._subcons.payload.sizeof(**this) // 8),
	'payload'     / construct.Bytewise(Payload),
)

Slot = construct.Struct(
	'bitstreamMagic' / construct.Const(0x7EAA997E, construct.Int32ub),
	'bitstream'      / construct.Padded(28, construct.GreedyRange(Instruction), pattern = b'\xFF'),
)

class Slots:
	""" A builder type that creates multi-boot slot configurations for the Lattice iCE40 FPGAs. """

	def __init__(self, flash : Flash):
		"""
		Parameters
		----------
		flash
			A Flash configuration object describing the target platform's Flash configuration
			to allow this type to generate a correct multi-boot layout for the target.
		"""
		self._flash = flash

	def build(self) -> bytearray:
		""" Generate a bytearray encoding the slot configuration for the Flash passed to the constructor.

		All valid iCE40 slot configurations consist of 5 slots that the FPGA will read from fixed addresses
		in the Flash. The slots are numbered in the order POR, Slot 0, Slot 1, Slot 2 and Slot 3.

		1. The POR slot is used to configure the FPGA from cold which we set to the Slot 1 configuration
		2. Slot 0 is this bootloader, which is only booted when the user asks for FPGA reconfiguration
		3. Slot 1 is the main gateware slot, which is booted by default
		4. Slot 2 depends on if there is sufficient room in the Flash - if there is, this is an auxilary slot;
		   if not, then this is a dupliate of Slot 1
		5. Slot 3 also depends on there being sufficient room in the Flash in the same way as Slot 2
		"""
		data = bytearray(32 * 5)
		logging.info(f'Serialising {len(data)} bytes of slot data')

		slots = self._buildSlots(self._flash)
		# Copy in the boot slot
		data[0:32] = slots[1]
		slotOffset = 32
		# And then populate the usable slots
		for slot in slots:
			assert len(slot) == 32
			data[slotOffset:slotOffset + 32] = slot
			slotOffset += 32
		# Then popualte any remaining slots with the entry for the last usable one
		slot = slots[-1]
		for _ in range(len(slots), 4):
			data[slotOffset:slotOffset + 32] = slot
			slotOffset += 32
		return data

	@staticmethod
	def _buildSlots(flash : Flash) -> List[bytes]:
		""" Go through the calculated max slots for the Flash and generate the slot data for each

		Returns
		-------
		A list containing the data for each valid warmboot slot
		"""
		partitions = flash.partitions
		slots = []
		for slot in range(flash.slots):
			slots.append(Slots._buildSlot(partitions[slot]))
		return slots

	@staticmethod
	def _buildSlot(partition : Dict[str, int]) -> bytes:
		""" Construct the slot configuration for a given slot

		Parameters
		----------
		partition
			A [begin, end) pair expressed as a dictionary of the area of Flash the slot covers

		Notes
		-----
		.. highlight:: python

		The partition dict comes from the Flash object's partition data and contains two entires::

			{
				'beginAddress': begin,
				'endAddress: end
			}

		"""
		return Slot.build({
			'bitstream': [
				{
					'instruction': Opcodes.BootMode,
					'payload': {'mode': BootModes.SimpleBoot}
				},
				{
					'instruction': Opcodes.BootAddress,
					'payload': {
						'address': partition['beginAddress']
					}
				},
				{
					'instruction': Opcodes.BankOffset,
					'payload': {
						'offset': 0,
					}
				},
				{
					'instruction': Opcodes.Special,
					'payload': {
						'operation': SpecialOpcodes.Reboot
					}
				}
			]
		})
