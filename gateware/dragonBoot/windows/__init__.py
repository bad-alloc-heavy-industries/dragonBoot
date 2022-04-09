# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Module, Signal
from usb_protocol.types import USBRequestType, USBRequestRecipient
from usb_protocol.types.descriptors.microsoft import MicrosoftRequests
from usb_protocol.emitters.descriptors.microsoft import PlatformDescriptorCollection
from luna.gateware.usb.usb2.request import (
	USBRequestHandler, SetupPacket, USBOutStreamInterface
)

from .descriptorSet import GetDescriptorSetHandler

__all__ = (
	'WindowsRequestHandler',
)

class WindowsRequestHandler(USBRequestHandler):
	def __init__(self, descriptors : PlatformDescriptorCollection, maxPacketSize = 64):
		self.descriptors = descriptors
		self._maxPacketSize = maxPacketSize

		super().__init__()

	def elaborate(self, platform) -> Module:
		m = Module()
		interface = self.interface
		setup = interface.setup
		tx = interface.tx

		m.submodules.getDescriptorSet = descriptorSetHandler = GetDescriptorSetHandler(self.descriptors)
		m.d.comb += [
			descriptorSetHandler.request.eq(setup.request),
			descriptorSetHandler.length.eq(setup.length),
		]

		with m.If(self.handlerCondition(setup)):
			with m.FSM(domain = 'usb'):
				# IDLE -- not handling any active request
				with m.State('IDLE'):
					# If we've received a new setup packet, handle it.
					with m.If(setup.received):
						with m.Switch(setup.index):
							with m.Case(MicrosoftRequests.GET_DESCRIPTOR_SET):
								m.next = 'CHECK_GET_DESCRIPTOR_SET'
							with m.Default():
								m.next = 'UNHANDLED'

				# CHECK_GET_DESCRIPTOR_SET -- Validate a platform-specific descriptor set request
				with m.State('CHECK_GET_DESCRIPTOR_SET'):
					with m.If(setup.is_in_request & (setup.value == 0)):
						m.next = 'GET_DESCRIPTOR_SET'
					with m.Else():
						m.next = 'UNHANDLED'

				# GET_DESCRIPTOR_SET -- The host is trying to request a platform-specific descriptor set
				with m.State('GET_DESCRIPTOR_SET'):
					expectingAck = Signal()

					m.d.comb += [
						descriptorSetHandler.tx.attach(tx),
						interface.handshakes_out.stall.eq(descriptorSetHandler.stall),
					]

					with m.If(interface.data_requested):
						m.d.comb += descriptorSetHandler.start.eq(1)
						m.d.usb += expectingAck.eq(1)

					with m.If(interface.handshakes_in.ack & expectingAck):
						nextStartPosition = descriptorSetHandler.startPosition + self._maxPacketSize
						m.d.usb += [
							descriptorSetHandler.startPosition.eq(nextStartPosition),
							self.interface.tx_data_pid.eq(~self.interface.tx_data_pid),
							expectingAck.eq(0),
						]

					with m.If(interface.status_requested):
						m.d.comb += interface.handshakes_out.ack.eq(1)
						m.next = 'IDLE'
					with m.Elif(descriptorSetHandler.stall):
						m.next = 'IDLE'

				# UNHANDLED -- we've received a request we're not prepared to handle
				with m.State('UNHANDLED'):
					# Wen we next have an opportunity to stall, do so and then return to idle.
					with m.If(interface.data_requested | interface.status_requested):
						m.d.comb += interface.handshakes_out.stall.eq(1)
						m.next = 'IDLE'

		return m

	def handlerCondition(self, setup : SetupPacket):
		return (
			(setup.type == USBRequestType.VENDOR) &
			(setup.recipient == USBRequestRecipient.DEVICE) &
			(
				(setup.index == MicrosoftRequests.GET_DESCRIPTOR_SET) |
				(setup.index == MicrosoftRequests.SET_ALTERNATE_ENUM)
			)
		)
