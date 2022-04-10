# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Module, Signal, Record, DomainRenamer, Cat
from amaranth.hdl.rec import DIR_FANOUT
from amaranth.lib.fifo import AsyncFIFO
from usb_protocol.types import USBRequestType, USBRequestRecipient, USBStandardRequests
from usb_protocol.types.descriptors.dfu import DFURequests
from luna.gateware.usb.usb2.request import (
	USBRequestHandler, SetupPacket
)
from luna.gateware.usb.stream import USBInStreamInterface, USBOutStreamInterface
from luna.gateware.stream.generator import StreamSerializer
from enum import IntEnum, auto, unique

from .flash import SPIFlash

__all__ = (
	'DFURequestHandler',
)

@unique
class DFUState(IntEnum):
	dfuIdle = auto()
	downloadSync = auto()
	downloadBusy = auto()
	downloadIdle = auto()
	uploadIdle = auto()
	error = auto()

class DFUConfig(Record):
	def __init__(self):
		super().__init__((
			('status', 3, DIR_FANOUT),
		))

class DFURequestHandler(USBRequestHandler):
	def __init__(self, *, interface, resource):
		super().__init__()

		self._interface = interface
		self._flashResource = resource

	def elaborate(self, platform):
		m = Module()
		interface = self.interface
		setup = interface.setup

		rxTriggered = Signal()
		rxStream = USBOutStreamInterface(payload_width = 8)
		receiverStart = Signal()
		receiverStreaming = Signal()
		receiverDone = Signal()
		receiverConsumed = Signal.like(setup.length)

		config = DFUConfig()

		m.submodules.bitstreamFIFO = bitstreamFIFO = AsyncFIFO(
			width = 8, depth = platform.erasePageSize, r_domain = 'usb', w_domain = 'usb'
		)
		m.submodules.flash = flash = DomainRenamer({'sync': 'usb'})(
			SPIFlash(resource = self._flashResource, fifo = bitstreamFIFO, flashSize = platform.flashSize)
		)

		m.submodules.transmitter = transmitter = StreamSerializer(
			data_length = 6, domain = 'usb', stream_type = USBInStreamInterface, max_length_width = 3
		)

		m.d.comb += [
			flash.start.eq(0),
		]

		with m.FSM(domain = 'usb', name = 'dfu'):
			# RESET -- do initial setup of the DFU handler state
			with m.State('RESET'):
				m.d.usb += [
					config.status.eq(DFUState.dfuIdle),
				]
				m.next = 'IDLE'
			# IDLE -- no active request being handled
			with m.State('IDLE'):
				# If we've received a new setup packet
				with m.If(setup.received & self.handlerCondition(setup)):
					with m.If(setup.type == USBRequestType.CLASS):
						# Switch to the right state for what we need to handle
						with m.Switch(setup.request):
							with m.Case(DFURequests.DOWNLOAD):
								m.next = 'HANDLE_DOWNLOAD'
							with m.Case(DFURequests.GET_STATE):
								m.next = 'HANDLE_GET_STATE'
							with m.Default():
								m.next = 'UNHANDLED'
					with m.Elif(setup.type == USBRequestType.STANDARD):
						# Switch to the right state for what we need to handle
						with m.Switch(setup.request):
							with m.Default():
								m.next = 'UNHANDLED'

			# HANDLE_DOWNLOAD -- The host is trying to send us some data to program
			with m.State('HANDLE_DOWNLOAD'):
				with m.If(setup.is_in_request | (setup.length > platform.erasePageSize)):
					m.next = 'UNHANDLED'
				with m.Elif(setup.length):
					m.d.comb += flash.start.eq(1)
					m.d.usb += config.status.eq(DFUState.downloadIdle)
					m.next = 'HANDLE_DOWNLOAD_DATA'

			with m.State('HANDLE_DOWNLOAD_DATA'):
				m.d.comb += interface.rx.connect(rxStream)
				with m.If(~rxTriggered):
					m.d.comb += receiverStart.eq(1)
					m.d.usb += rxTriggered.eq(1)
				with m.Elif(receiverStreaming):
					m.d.usb += config.status.eq(DFUState.downloadBusy)

				with m.If(interface.rx_ready_for_response):
					m.d.comb += interface.handshakes_out.ack.eq(1)
				with m.If(interface.status_requested):
					m.d.comb += self.send_zlp()
				with m.If(self.interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATE'):
				# Hook up the transmitter ...
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
				]
				m.d.comb += transmitter.data[0].eq(Cat(config.status, 0))

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

			# UNHANDLED -- we've received a request we don't know how to handle
			with m.State('UNHANDLED'):
				# When we next have an opportunity to stall, do so,
				# and then return to idle.
				with m.If(interface.data_requested | interface.status_requested):
					m.d.comb += interface.handshakes_out.stall.eq(1)
					m.next = 'IDLE'

		m.d.comb += [
			receiverDone.eq(0),
			bitstreamFIFO.w_en.eq(0),
			bitstreamFIFO.w_data.eq(rxStream.payload),
		]
		receiverContinue = (receiverConsumed < setup.length)

		with m.FSM(domain = 'usb', name = 'download'):
            # IDLE -- we're not actively receiving
			with m.State('IDLE'):
                # Keep our consumption count at 0 while we've not yet consumed anything
				m.d.usb += receiverConsumed.eq(0)
                # Once the download handler requests we start, begin consuming the data
				with m.If(receiverStart):
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
