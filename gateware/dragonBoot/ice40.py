# SPDX-License-Identifier: BSD-3-Clause
import logging
import construct
from construct import this, len_
from enum import IntEnum, unique
from typing import Dict, List

from .platform import Flash

__all__ = (
	'Slots',
)

@unique
class Opcodes(IntEnum):
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
	CRAMData = 1
	BRAMData = 3
	ResetCRC = 5
	Wakeup = 6
	Reboot = 8

@unique
class BootModes(IntEnum):
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
	def __init__(self, flash : Flash):
		self._flash = flash

	def build(self) -> bytearray:
		data = bytearray(32 * 5)
		logging.info(f'Serialising {len(data)} bytes of slot data')

		slots = self._buildSlots(self._flash)
		# Copy in the boot slot
		data[0:32] = slots[0]
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
		partitions = flash.partitions
		slots = []
		for slot in range(flash.slots):
			slots.append(Slots._buildSlot(partitions[slot]))
		return slots

	@staticmethod
	def _buildSlot(partition : Dict[str, int]) -> bytes:
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
