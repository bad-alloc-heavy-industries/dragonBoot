# SPDX-License-Identifier: BSD-3-Clause
from torii.hdl import Elaboratable, Module, Signal, Cat
from typing import Tuple

__all__ = (
	'SPIBus',
)

class SPIBus(Elaboratable):
	""" SPI bus controller gateware for talking to the Flash.

	Attributes
	--------
	cs : Signal(), input
		Chip Select (non-inverted) signal to be passed through to the Flash.
	xfer : Signal(), input
		Strobe that signals to start a SPI transfer.
	done : Signal(), output
		Strobe that indicates the completion of a SPI transfer.

	r_data : Signal(8), output
		Data read from the Flash in the last completed transfer.
	w_data : Signal(8), input
		Data to be written to the Flash in the next transfer.
	"""

	def __init__(self, *, resource : Tuple[str, int]):
		"""
		Parameters
		----------
		resource
			The fully qualified identifier for the platform resource defining the SPI bus to use.
		"""

		self._spiResource = resource

		self.cs = Signal()
		self.xfer = Signal()
		self.done = Signal()
		self.r_data = Signal(8)
		self.w_data = Signal(8)

	def elaborate(self, platform) -> Module:
		""" Describes the specific gateware needed to talk SPI protocol.

		Parameters
		----------
		platform
			The Amaranth platform for which the gateware will be synthesised.

		Returns
		-------
		:py:class:`torii.hdl.dsl.Module`
			A complete description of the gateware behaviour required.
		"""
		m = Module()
		bus = platform.request(*self._spiResource)

		bit = Signal(range(8))
		clk = Signal(reset = 1)
		cipo = bus.cipo.i
		copi = bus.copi.o

		dataIn = Signal.like(self.r_data)
		dataOut = Signal.like(self.w_data)

		m.d.comb += self.done.eq(0)

		with m.FSM(name = 'spi'):
			with m.State('IDLE'):
				m.d.sync += clk.eq(1)
				with m.If(self.xfer):
					m.d.sync += dataOut.eq(self.w_data)
					m.next = 'TRANSFER'
			with m.State('TRANSFER'):
				m.d.sync += clk.eq(clk ^ 1)
				with m.If(clk):
					m.d.sync += [
						bit.eq(bit + 1),
						copi.eq(dataOut[7]),
					]
				with m.Else():
					m.d.sync += [
						dataOut.eq(dataOut.shift_left(1)),
						dataIn.eq(Cat(cipo, dataIn[:-1])),
					]
					with m.If(bit == 0):
						m.next = 'DONE'
			with m.State('DONE'):
				m.d.comb += self.done.eq(1)
				m.d.sync += self.r_data.eq(dataIn)
				with m.If(self.xfer):
					m.d.sync += dataOut.eq(self.w_data)
					m.next = 'TRANSFER'
				with m.Else():
					m.next = 'IDLE'

		m.d.comb += [
			bus.cs.o.eq(self.cs),
			bus.clk.o.eq(clk),
		]
		return m
