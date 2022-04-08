# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, Signal, Memory, DomainRenamer
from struct import pack as structPack, unpack as structUnpack
from usb_protocol.emitters.descriptors.microsoft import PlatformDescriptorCollection
from luna.gateware.usb.stream import USBInStreamInterface
from typing import Tuple

__all__ = (
	'GetDescriptorSetHandler',
)

class GetDescriptorSetHandler(Elaboratable):
	""" Gateware that handles responding to windows-specific GetDescriptorSet requests.

	I/O port:
		I: request[8]    -- The request field associated with the Get Descriptor Set request.
		                    Contains the descriptor set's vendor code.
		I: length[16]    -- The length field associated with the Get Descriptor Set request.
		                    Determines the maximum amount allowed in a response.

		I: start         -- Strobe that indicates when a descriptor should be transmitted.
		I: startPosition -- Specifies the starting position of the descriptor data to be transmitted.

		*: tx            -- The USBInStreamInterface that streams our descriptor data.
		O: stall         -- Pulsed if a STALL handshake should be generated, instead of a response.
	"""
	elementSize = 4

	def __init__(self, descriptorCollection : PlatformDescriptorCollection, maxPacketLength = 64, domain = 'usb'):
		"""
		Parameters
		----------
		descriptorCollection : PlatformDescriptorCollection
			The PlatformDescriptorCollection containing the descriptors to use for windows platform-specific responses.
		maxPacketLength: int
			Maximum EP0 packet length.
		domain: string
			The clock domain this generator should belong to. Defaults to 'usb'.
		"""
		self._descriptors = descriptorCollection
		self._maxPacketLength = maxPacketLength
		self._domain = domain

		#
		# I/O port
		#
		self.request = Signal(8)
		self.length = Signal(16)

		self.start = Signal()
		self.startPosition = Signal(11)

		self.tx = USBInStreamInterface()
		self.stall = Signal()

	@classmethod
	def _alignToElementSize(cls, n):
		""" Returns a given number rounded up to the next 'aligned' element size. """
		return (n + (cls.elementSize - 1)) // cls.elementSize

	def generateROM(self) -> Tuple[Memory, int, int]:
		""" Generates a ROM used to hold descriptor sets.

		Memory layout
		-------------

		All data is aligned to 4 byte boundaries

		Index offsets and descriptor set lengths
		----------------------------------------
		Each index of a descriptor set has an entry consistent of the length
		of the descriptor set (2 bytes) and the address of the first data
		byte (2 bytes).

		0000  Length of the first descriptor set
		0002  Address of the first descriptor set
		...

		Data
		----
		Descriptor data for each descriptor set. Padded by 0 to the next 4-byte address.

		...   Descriptor data

		"""

		descriptors = self._descriptors.descriptors
		assert max(descriptors.keys()) == len(descriptors), "descriptor sets have non-contiguous vendor codes!"
		assert min(descriptors.keys()) == 1, "descriptor sets must start at vendor code 1"

		maxVendorCode = max(descriptors.keys())
		maxDescriptorSize = 0
		romSizeTableEntries = len(descriptors) * self.elementSize

		romSizeDescriptors = 0
		for descriptorSet in descriptors.values():
			alignedSize = self._alignToElementSize(len(descriptorSet))
			romSizeDescriptors += alignedSize * self.elementSize
			maxDescriptorSize = max(maxDescriptorSize, len(descriptorSet))

		totalSize = romSizeTableEntries + romSizeDescriptors
		rom = bytearray(totalSize)

		nextFreeAddress = maxVendorCode * self.elementSize

		# First, generate a list of 'table pointers', which point to the address of each descriptor set, in memory.
		for vendor_code, descriptorSet in sorted(descriptors.items()):
			descriptorSetLen = len(descriptorSet)
			pointerBytes = structPack('>HH', descriptorSetLen, nextFreeAddress)
			pointerAddress = (vendor_code - 1) * self.elementSize
			rom[pointerAddress:pointerAddress + self.elementSize] = pointerBytes
			rom[nextFreeAddress:nextFreeAddress + descriptorSetLen] = descriptorSet

			alignedSize = self._alignToElementSize(descriptorSetLen)
			nextFreeAddress += alignedSize * self.elementSize

		assert totalSize == len(rom)
		elementSize = self.elementSize
		romEntries = (rom[i:i + elementSize] for i in range(0, totalSize, elementSize))
		initialiser = [structUnpack('>I', romEntry)[0] for romEntry in romEntries]
		return Memory(width = 32, depth = len(initialiser), init = initialiser), maxDescriptorSize, maxVendorCode

	def elaborate(self, platform) -> Module:
		m = Module()
		vendorCode = self.request
		rom, descriptorMaxLength, maxVendorCode = self.generateROM()
		m.submodules.readPort = readPort = rom.read_port(transparent = False)

		romLowerHalf = readPort.data.word_select(0, 16)
		romUpperHalf = readPort.data.word_select(1, 16)
		romElementPointer = romLowerHalf.bit_select(2, readPort.addr.width)
		romElementCount = romUpperHalf
		length = Signal(16)

		positionInStream = Signal(range(descriptorMaxLength))
		bytesSent = Signal.like(length)

		descriptorLength = Signal.like(length)
		descriptorDataBaseAddress = Signal(readPort.addr.width)

		onFirstPacket = positionInStream == self.startPosition
		onLastPacket = (
			(positionInStream == descriptorLength - 1) |
			(bytesSent + 1 >= length)
		)

		with m.FSM():
			with m.State('IDLE'):
				m.d.sync += bytesSent.eq(0)
				m.d.comb += readPort.addr.eq(vendorCode)
				with m.If(self.start):
					m.next = 'START'

			with m.State('START'):
				m.d.comb += readPort.addr.eq(vendorCode)
				m.d.sync += positionInStream.eq(self.startPosition)
				isValidSet = vendorCode <= maxVendorCode
				with m.If(isValidSet):
					m.next = 'LOOKUP_DESCRIPTOR'
				with m.Else():
					m.d.comb += self.stall.eq(1)
					m.next = 'IDLE'

			with m.State('LOOKUP_DESCRIPTOR'):
				m.d.comb += readPort.addr.eq((readPort.data + positionInStream) >> 2)
				m.d.sync += [
					descriptorDataBaseAddress.eq(romElementPointer),
					descriptorLength.eq(romElementCount),
				]
				m.next = 'SEND_DESCRIPTOR'

			with m.State('SEND_DESCRIPTOR'):
				wordInStream = positionInStream.shift_right(2)
				byteInStream = positionInStream.bit_select(0, 2)

				m.d.comb += [
					self.tx.valid.eq(1),
					readPort.addr.eq(descriptorDataBaseAddress + wordInStream),
					self.tx.payload.eq(readPort.data.word_select(3 - byteInStream, 8)),
					self.tx.first.eq(onFirstPacket),
					self.tx.last.eq(onLastPacket),
				]

				with m.If(self.tx.ready):
					with m.If(~onLastPacket):
						m.d.sync += [
							positionInStream.eq(positionInStream + 1),
							bytesSent.eq(bytesSent + 1),
						]
						m.d.comb += readPort.addr.eq(descriptorDataBaseAddress +
							(positionInStream + 1).bit_select(2, positionInStream.width - 2)),
					with m.Else():
						m.d.sync += [
							descriptorLength.eq(0),
							descriptorDataBaseAddress.eq(0),
						]
						m.next = 'IDLE'

		if self._domain != 'sync':
			m = DomainRenamer({'sync': self._domain})(m)
		return m
