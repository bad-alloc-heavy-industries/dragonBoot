# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Module, Signal, DomainRenamer, Cat, Memory, Const
from amaranth.hdl.rec import DIR_FANOUT
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
	dfuIdle = 2
	downloadSync = 3
	downloadBusy = 4
	downloadIdle = 5
	uploadIdle = 9
	error = 10

@unique
class DFUStatus(IntEnum):
	ok = 0

class DFUConfig:
	def __init__(self):
		self.status = Signal(4, decoder = DFUStatus)
		self.state = Signal(4, decoder = DFUState)

class DFURequestHandler(USBRequestHandler):
	def __init__(self, *, interface : int, resource : Tuple[str, int]):
		super().__init__()

		self._interface = interface
		self._flashResource = resource

		self.triggerReboot = Signal()

	def elaborate(self, platform) -> Module:
		m = Module()
		interface = self.interface
		setup = interface.setup

		rxTriggered = Signal()
		rxStream = USBOutStreamInterface(payload_width = 8)
		receiverStart = Signal()
		receiverDone = Signal()
		receiverCount = Signal.like(setup.length)
		receiverConsumed = Signal.like(setup.length)
		slot = Signal(8)

		_flash : Flash = platform.flash
		config = DFUConfig()
		self.printSlotInfo(_flash)

		m.submodules.bitstreamFIFO = bitstreamFIFO = AsyncFIFO(
			width = 8, depth = _flash.erasePageSize, r_domain = 'usb', w_domain = 'usb'
		)
		m.submodules.flash = flash = DomainRenamer({'sync': 'usb'})(
			SPIFlash(resource = self._flashResource, fifo = bitstreamFIFO, flashSize = _flash.size)
		)
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
				m.d.comb += self.triggerReboot.eq(1)

			# HANDLE_DOWNLOAD -- The host is trying to send us some data to program
			with m.State('HANDLE_DOWNLOAD'):
				with m.If(setup.is_in_request | (setup.length > _flash.erasePageSize)):
					m.next = 'UNHANDLED'
				with m.Elif(setup.length):
					m.d.comb += [
						flash.start.eq(1),
						flash.byteCount.eq(setup.length),
					]
					m.d.usb += config.state.eq(DFUState.downloadIdle)
					m.next = 'HANDLE_DOWNLOAD_DATA'
				with m.Else():
					m.next = 'HANDLE_DOWNLOAD_COMPLETE'

			with m.State('HANDLE_DOWNLOAD_DATA'):
				m.d.comb += interface.rx.connect(rxStream)
				with m.If(~rxTriggered):
					m.d.comb += receiverStart.eq(1)
					m.d.usb += [
						rxTriggered.eq(1),
						config.state.eq(DFUState.downloadBusy),
					]

				with m.If(interface.rx_ready_for_response):
					m.d.comb += interface.handshakes_out.ack.eq(1)
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()
				with m.If(self.interface.handshakes_in.ack):
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
				]
				m.d.comb += [
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
				]
				m.d.comb += transmitter.data[0].eq(Cat(config.state, 0))

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
				]
				m.d.comb += transmitter.data[0].eq(slot)

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
			receiverDone.eq(0),
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
						m.next = 'DONE'
            # DONE -- report our completion then go to idle
			with m.State('DONE'):
				m.d.comb += receiverDone.eq(1)
				m.next = 'IDLE'

		return m

	def handlerCondition(self, setup : SetupPacket):
		return (
			((setup.type == USBRequestType.CLASS) | (setup.type == USBRequestType.STANDARD)) &
			(setup.recipient == USBRequestRecipient.INTERFACE) &
			(setup.index == self._interface)
		)

	def printSlotInfo(self, flash : Flash):
		logging.info(f'Building for a {flash.humanSize} Flash with {flash.slots} boot slots')
		for partition, slot in flash.partitions.items():
			logging.info(f'Boot slot {partition} starts at {slot["beginAddress"]:#08x} and finishes at {slot["endAddress"]:#08x}')

	def generateROM(self, flash : Flash):
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
