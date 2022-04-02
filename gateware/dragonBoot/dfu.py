from amaranth import Module, Signal

from luna.gateware.usb.usb2.request import (
	USBRequestHandler, SetupPacket
)

__all__ = (
	'DFURequestHandler',
)

class DFURequestHandler(USBRequestHandler):
	def __init__(self, *, interface):
		super().__init__()
		self._interface = interface

	def elaborate(self, platform):
		m = Module()
		interface = self.interface
		setup = interface.setup

		return m

	def handlerCondition(self, setup : SetupPacket):
		return Signal()
