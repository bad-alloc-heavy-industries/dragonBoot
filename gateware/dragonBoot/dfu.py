# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Module, Signal, DomainRenamer, Cat, Memory, Const
from amaranth.lib.fifo import AsyncFIFO
from usb_protocol.types import USBRequestType, USBRequestRecipient, USBStandardRequests
from usb_protocol.types.descriptors.dfu import DFURequests
from luna.gateware.usb.usb2.request import (
	USBRequestHandler, SetupPacket
)
from luna.gateware.usb.stream import USBInStreamInterface, USBOutStreamInterface
from luna.gateware.stream.generator import StreamSerializer
from enum import IntEnum, unique
from struct import pack as structPack, unpack as structUnpack
from typing import Tuple
import logging

from .platform import Flash
from .flash import SPIFlash

__all__ = (
	'DFURequestHandler',
)

@unique
class DFUState(IntEnum):
	""" An enumeration of the states the DFU request handler engine can be in. """
	dfuIdle = 2
	""" The DFU request handler is in an idle state. """
	downloadSync = 3
	""" The engine has just finished processing a download request and is awaiting a status request. """
	downloadBusy = 4
	""" The engine is processing a download request. """
	downloadIdle = 5
	""" The engine has processed at least one download request but is currently idle. """
	uploadIdle = 9
	""" The engine has processed at least one upload request but is currently idle. """
	error = 10
	""" The engine has encountered an error of some kind. """

@unique
class DFUStatus(IntEnum):
	""" An enumeration of the status states the DFU request handler engine can be in. """
	ok = 0
	""" The engine is not in error and all is in order. """

class DFUConfig:
	""" A tracking type for the current state and status of the DFU request handler engine.

	Attributes
	----------
	status : Signal(4, decoder = DFUStatus)
		A 4-bit register containing the current status of the DFU request handler from the :py:class:DFUStatus enum.
	state : Signal(4, decoder = DFUState)
		A 4-bit register containing the current state of the DFU request handler from the :py:class:DFUState enum.
	"""
	def __init__(self):
		self.status = Signal(4, decoder = DFUStatus)
		self.state = Signal(4, decoder = DFUState)

class DFURequestHandler(USBRequestHandler):
	""" The DFU request handling engine.

	Parameters
	----------
	configuration
		The USB configuration this handler should be bound on - must match the value in the descriptors.
	interface
		The USB interface number this handler should be bound on - must match the value in the descriptors.
	resource
		The fully qualified identifier for the platform resource defining the SPI bus to use to access
		the configuration Flash.

	Attributes
	----------
	triggerReboot : Signal(), output
		A signal indicating if the bootloader should trigger a reboot into the main gateware slot.

	Notes
	-----
	The handler operates by reacting to incoming setup packets for the DFU interface. Of most notable
	interest are how it handles DFU detach and download requests as the rest are essentailly boilerplate
	requried by the `DFU 1.1 standard <https://www.usb.org/sites/default/files/DFU_1.1.pdf>`_.

	Detach requests are handled by asserting the triggerReboot signal and stalling in the
	:code:`HANDLE_DETACH` state. Download requests are handled as follows:

	* First we enter the :code:`HANDLE_DOWNLOAD` state.
	* The length of the request is checked and if 0, we then enter the :code:`HANDLE_DOWNLOAD_COMPLETE` state.

	 	* Once in the new state we wait for the status phase where we respond with a ZLP,
		  and change the DFU state back to dfuIdle.
		* After completion of the status phase with the resulting acknowledgment returning to us,
		  we enter :code:`IDLE` again.

	* If the length of the request is non-zero but less than the Flash sector erase page size, we enter
	  :code:`HANDLE_DOWNLOAD_DATA` where the following steps are performed:

		* We first trigger the secondary download state machine which handles pulling the payload bytes
		  from the stream interface as they come in.
		* Once the data phase completes, sends the corresponding acknowledgement to let the
		  host know it was successful.
		* As the status phase starts, sends the corresponding ZLP.
		* Then transitions back to :code:`IDLE`, resetting the trigger on the download state machine,
		  when the ACK comes back from the host.

	* If the length of the request exceeds the Flash device's sector erase page size, then we send the host
	  a stall response to indicate failure, and return to :code:`IDLE` - this should technically be impossible
	  in a conforming implementation of DFU on the host, but we have to act defensively.

	It is of particular note that the download state machine pushes the payload bytes to the bitstream FIFO
	which is also passed through to the SPI Flash interface. This FIFO is created with enough entires
	to store a complete Flash sector erase page of data, and re-entry into the :code:`HANDLE_DOWNLOAD` state
	is gated using the DFU protocol's status system through which we indicate to a host that Flash operations
	are busy till not only is the FIFO exhausted, but the SPI Flash engine reports it has completed getting
	the data written back to the configuration Flash.

	If a DFU implementation tries to send a download request before we tell it we're ready for another,
	it would be considered non-conforming, however this should not hurt us as while it will corrupt
	the data written to the Flash, the FIFO can correctly handle exhaustion so should still allow operations
	to complete. Therefore we have not attempted to further handle this other than "well just don't do that then".
	"""
	def __init__(self, *, configuration : int, interface : int, resource : Tuple[str, int]):
		super().__init__()

		self._configuration = configuration
		self._interface = interface
		self._flashResource = resource

		self.triggerReboot = Signal()

	def elaborate(self, platform) -> Module:
		""" Describes the specific gateware needed to implement DFU and its handling on USB EP0.

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
		interface = self.interface
		setup = interface.setup

		rxTriggered = Signal()
		rxStream = USBOutStreamInterface(payload_width = 8)
		receiverStart = Signal()
		receiverCount = Signal.like(setup.length)
		receiverConsumed = Signal.like(setup.length)
		slot = Signal(8)

		_flash : Flash = platform.flash
		config = DFUConfig()
		self.printSlotInfo(_flash)

		m.submodules.bitstreamFIFO = bitstreamFIFO = AsyncFIFO(
			width = 8, depth = _flash.erasePageSize, r_domain = 'usb', w_domain = 'usb'
		)
		flash : SPIFlash = DomainRenamer({'sync': 'usb'})(
			SPIFlash(resource = self._flashResource, fifo = bitstreamFIFO)
		)
		m.submodules.flash = flash
		m.submodules.transmitter = transmitter = StreamSerializer(
			data_length = 6, domain = 'usb', stream_type = USBInStreamInterface, max_length_width = 3
		)
		slotROM = self.generateROM(_flash)
		m.submodules.slots = slots = slotROM.read_port(domain = 'usb', transparent = False)

		m.d.comb += [
			flash.start.eq(0),
			flash.finish.eq(0),
			flash.resetAddrs.eq(0),
		]

		with m.FSM(domain = 'usb', name = 'dfu'):
			# RESET -- do initial setup of the DFU handler state
			with m.State('RESET'):
				m.d.usb += [
					config.status.eq(DFUStatus.ok),
					config.state.eq(DFUState.dfuIdle),
					slot.eq(0),
				]
				with m.If(flash.ready):
					m.next = 'READ_SLOT_DATA'
			# IDLE -- no active request being handled
			with m.State('IDLE'):
				# If we've received a new setup packet
				with m.If(setup.received & self.handlerCondition(setup)):
					with m.If(setup.type == USBRequestType.CLASS):
						# Switch to the right state for what we need to handle
						with m.Switch(setup.request):
							with m.Case(DFURequests.DETACH):
								m.next = 'HANDLE_DETACH'
							with m.Case(DFURequests.DOWNLOAD):
								m.next = 'HANDLE_DOWNLOAD'
							with m.Case(DFURequests.GET_STATUS):
								m.next = 'HANDLE_GET_STATUS'
							with m.Case(DFURequests.CLR_STATUS):
								m.next = 'HANDLE_CLR_STATUS'
							with m.Case(DFURequests.GET_STATE):
								m.next = 'HANDLE_GET_STATE'
							with m.Default():
								m.next = 'UNHANDLED'
					with m.Elif(setup.type == USBRequestType.STANDARD):
						# Switch to the right state for what we need to handle
						with m.Switch(setup.request):
							with m.Case(USBStandardRequests.GET_INTERFACE):
								m.next = 'GET_INTERFACE'
							with m.Case(USBStandardRequests.SET_INTERFACE):
								m.next = 'SET_INTERFACE'
							with m.Default():
								m.next = 'UNHANDLED'
					# If the underlying Flash operation is complete, signal this by going downloadSync
					with m.If(flash.done):
						m.d.comb += flash.finish.eq(1)
						m.d.usb += config.state.eq(DFUState.downloadSync)

			# HANDLE_DETACH -- The host wishes us to reboot into run mode
			with m.State('HANDLE_DETACH'):
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()

				with m.If(interface.handshakes_in.ack):
					m.d.usb += self.triggerReboot.eq(1)

			# HANDLE_DOWNLOAD -- The host is trying to send us some data to program
			with m.State('HANDLE_DOWNLOAD'):
				with m.If(setup.is_in_request | (setup.length > _flash.erasePageSize)):
					m.next = 'UNHANDLED'
				with m.Elif(setup.length):
					m.d.comb += [
						flash.start.eq(1),
						flash.byteCount.eq(setup.length),
					]
					m.d.usb += config.state.eq(DFUState.downloadBusy)
					m.next = 'HANDLE_DOWNLOAD_DATA'
				with m.Else():
					m.next = 'HANDLE_DOWNLOAD_COMPLETE'

			with m.State('HANDLE_DOWNLOAD_DATA'):
				m.d.comb += interface.rx.connect(rxStream)
				with m.If(~rxTriggered):
					m.d.comb += receiverStart.eq(1)
					m.d.usb += rxTriggered.eq(1)

				with m.If(interface.rx_ready_for_response):
					m.d.comb += interface.handshakes_out.ack.eq(1)
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()
				with m.If(self.interface.handshakes_in.ack):
					m.d.usb += rxTriggered.eq(0)
					m.next = 'IDLE'

			with m.State('HANDLE_DOWNLOAD_COMPLETE'):
				with m.If(interface.status_requested):
					m.d.usb += config.state.eq(DFUState.dfuIdle)
					m.d.comb += self.send_zlp()
				with m.If(interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATUS'):
				# Hook up the transmitter ...
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(6),
					transmitter.data[0].eq(config.status),
					Cat(transmitter.data[1:4]).eq(0),
					transmitter.data[4].eq(Cat(config.state, 0)),
					transmitter.data[5].eq(0),
				]

				# ... then trigger it when requested if the lengths match ...
				with m.If(self.interface.data_requested):
					with m.If(setup.length == 6):
						m.d.comb += transmitter.start.eq(1)
					with m.Else():
						m.d.comb += interface.handshakes_out.stall.eq(1)
						m.next = 'IDLE'

				# ... and ACK our status stage.
				with m.If(interface.status_requested):
					m.d.comb += interface.handshakes_out.ack.eq(1)
					with m.If(config.state == DFUState.downloadSync):
						m.d.usb += config.state.eq(DFUState.downloadIdle)
					m.next = 'IDLE'

			with m.State('HANDLE_CLR_STATUS'):
				# If there is no data to follow, clear the status info
				with m.If(setup.length == 0):
					with m.If(config.state == DFUState.error):
						m.d.usb += [
							config.status.eq(DFUStatus.ok),
							config.state.eq(DFUState.dfuIdle),
						]
				with m.Else():
					m.d.comb += interface.handshakes_out.stall.eq(1)
					m.next = 'IDLE'

				# Provide a response for the status phase
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()
				# And when that gets ack'd, return to idle
				with m.If(interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATE'):
				# Hook up the transmitter ...
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
					transmitter.data[0].eq(Cat(config.state, 0)),
				]

				# ... then trigger it when requested if the lengths match ...
				with m.If(self.interface.data_requested):
					with m.If(setup.length == 1):
						m.d.comb += transmitter.start.eq(1)
					with m.Else():
						m.d.comb += interface.handshakes_out.stall.eq(1)
						m.next = 'IDLE'

				# ... and ACK our status stage.
				with m.If(interface.status_requested):
					m.d.comb += interface.handshakes_out.ack.eq(1)
					m.next = 'IDLE'

			# GET_INTERFACE -- The host is trying to ask what one of our interfaces' alt-mode is set to
			with m.State('GET_INTERFACE'):
				# Hook up the transmitter ...
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
					transmitter.data[0].eq(slot),
				]

				# ... then trigger it when requested if the lengths match ...
				with m.If(self.interface.data_requested):
					with m.If(setup.length == 1):
						m.d.comb += transmitter.start.eq(1)
					with m.Else():
						m.d.comb += interface.handshakes_out.stall.eq(1)
						m.next = 'IDLE'

				# ... and ACK our status stage.
				with m.If(interface.status_requested):
					m.d.comb += interface.handshakes_out.ack.eq(1)
					m.next = 'IDLE'

			# SET_INTERFACE -- The host is trying to switch to one of our interface alt-modes
			with m.State('SET_INTERFACE'):
				# Provide a response to the status stage
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()

				# Copy the value once we get back an ACK from the ZLP
				with m.If(interface.handshakes_in.ack):
					m.d.usb += slot.eq(setup.value[0:8])
					m.next = 'READ_SLOT_DATA'

			# UNHANDLED -- we've received a request we don't know how to handle
			with m.State('UNHANDLED'):
				# When we next have an opportunity to stall, do so,
				# and then return to idle.
				with m.If(interface.data_requested | interface.status_requested):
					m.d.comb += interface.handshakes_out.stall.eq(1)
					m.next = 'IDLE'

			# READ_SLOT_DATA -- Begin reading the slot data for the newly selected slot
			with m.State('READ_SLOT_DATA'):
				m.d.comb += slots.addr.eq(Cat(Const(0, 1), slot))
				m.next = 'READ_SLOT_BEGIN'

			# READ_SLOT_BEGIN -- Read the begin address for the newly selected slot
			with m.State('READ_SLOT_BEGIN'):
				m.d.comb += slots.addr.eq(Cat(Const(1, 1), slot))
				m.d.usb += flash.beginAddr.eq(slots.data)
				m.next = 'READ_SLOT_END'

			# READ_SLOT_BEGIN -- Read the end address for the newly selected slot
			with m.State('READ_SLOT_END'):
				m.d.usb += flash.endAddr.eq(slots.data)
				m.d.comb += flash.resetAddrs.eq(1)
				m.next = 'IDLE'

		m.d.comb += [
			bitstreamFIFO.w_en.eq(0),
			bitstreamFIFO.w_data.eq(rxStream.payload),
		]
		receiverContinue = (receiverConsumed < receiverCount)

		with m.FSM(domain = 'usb', name = 'download'):
			# IDLE -- we're not actively receiving
			with m.State('IDLE'):
				# Keep our consumption count at 0 while we've not yet consumed anything
				m.d.usb += receiverConsumed.eq(0)
				# Once the download handler requests we start, begin consuming the data
				with m.If(receiverStart):
					m.d.usb += receiverCount.eq(setup.length - 1)
					m.next = 'STREAMING'
			# STREAMING -- we're actively consuming data
			with m.State('STREAMING'):
				# If the current data byte becomes valid, store it and move to the next
				with m.If(rxStream.valid & rxStream.next):
					m.d.comb += bitstreamFIFO.w_en.eq(1)

					# Update the counter if we need to continue
					with m.If(receiverContinue):
						m.d.usb += receiverConsumed.eq(receiverConsumed + 1)
					# Otherwise go back to idle
					with m.Else():
						m.next = 'IDLE'

		return m

	def handlerCondition(self, setup : SetupPacket):
		""" Defines the setup packet conditions under which the request handler will operate.

		This is used to gate the handler's operation and forms part of the condition under which
		the stall-only handler in :py:class:`dragonBoot.bootloader.DragonBoot` will be triggered.

		Parameters
		----------
		setup
			A grouping of signals used to describe the most recent setup packet the control interface has seen.

		Returns
		-------
		:py:class:`amranth.hdl.ast.Operator`
			A combinatorial operation defining the sum conditions under which this handler will operate.

		Notes
		-----
		The condition for the operation of this handler is defined as being either:

		* A Standard request to the handler's interface, or
		* A Class-specific (ie, DFU) request to the handler's interface.

		This is as well as the current device configuration matching the one for this handler.
		"""
		return (
			(self.interface.active_config == self._configuration) &
			((setup.type == USBRequestType.CLASS) | (setup.type == USBRequestType.STANDARD)) &
			(setup.recipient == USBRequestRecipient.INTERFACE) &
			(setup.index == self._interface)
		)

	def printSlotInfo(self, flash : Flash):
		""" Prints out the slot configuration information for the given Flash object.

		Parameters
		----------
		flash
			A Flash object containing the :py:attr:`Flash.slots` and :py:attr:`Flash.partitions`
			information to be printed.
		"""
		logging.info(f'Building for a {flash.humanSize} Flash with {flash.slots} boot slots')
		for partition, slot in flash.partitions.items():
			logging.info(f'Boot slot {partition} starts at {slot["beginAddress"]:#08x} and finishes at {slot["endAddress"]:#08x}')

	def generateROM(self, flash : Flash) -> Memory:
		""" Generates the ROM for the layout of the Flash

		This ROM is laid out as follows:

		+---------+--------------+
		| Address |     Data     |
		+=========+==============+
		|    0    | Slot 0 Begin |
		+---------+--------------+
		|    1    | Slot 0 End   |
		+---------+--------------+
		|    2    | Slot 1 Begin |
		+---------+--------------+
		|    3    | Slot 1 End   |
		+---------+--------------+
		|     ... |              |
		+---------+--------------+

		Parameters
		----------
		flash
			The Flash object  from which the ROM image will be derived.

		Returns
		-------
		:py:class:`amaranth.hdl.mem.Memory`
			A Memory object defining the Flash slot address layout as described above.
			The memory object uses 24-bit entries as the Flash addresses are 24-bit,
			and has :math:`flash.slots * 2` entries.
		"""
		# 4 bytes per address, 2 addresses per slot (but the highest byte of each address will get truncated off)
		totalSize = flash.slots * 8
		rom = bytearray(totalSize)
		romAddress = 0
		for partition in range(flash.slots):
			slot = flash.partitions[partition]
			addressRange = structPack('>II', slot['beginAddress'], slot['endAddress'])
			rom[romAddress:romAddress + 8] = addressRange
			romAddress += 8

		romEntries = (rom[i:i + 4] for i in range(0, totalSize, 4))
		initialiser = [structUnpack('>I', romEntry)[0] for romEntry in romEntries]
		return Memory(width = 24, depth = flash.slots * 2, init = initialiser)
