# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, Signal, Cat

__all__ = (
	'SPIBus',
)

class SPIBus(Elaboratable):
	def __init__(self, *, resource):
		self._spiResource = resource

		self.cs = Signal()
		self.xfer = Signal()
		self.done = Signal()
		self.r_data = Signal(8)
		self.w_data = Signal(8)

	def elaborate(self, platform):
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
				with m.If(clk):
					m.d.sync += [
						clk.eq(0),
						bit.eq(bit + 1),
						copi.eq(dataOut[7]),
					]
				with m.Else():
					m.d.sync += [
						clk.eq(1),
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
