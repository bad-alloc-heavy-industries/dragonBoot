# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, Signal, Cat, ClockSignal

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
		bus = platform.request(*self._spiResource, xdr = {'clk': 2})

		bit = Signal(range(8))
		clkEn = Signal(1)
		cipo = bus.cipo.i
		copi = bus.copi.o

		dataIn = Signal.like(self.r_data)
		dataOut = Signal.like(self.w_data)

		m.d.comb += [
			clkEn.eq(0),
			self.done.eq(0),
		]

		with m.FSM(name = 'spi'):
			with m.State('IDLE'):
				with m.If(self.xfer):
					m.d.sync += dataOut.eq(self.w_data)
					m.next = 'TRANSFER'
			with m.State('TRANSFER'):
				m.d.comb += clkEn.eq(1)
				m.d.sync += [
					bit.eq(bit + 1),
					copi.eq(dataOut[7]),
					dataOut.eq(dataOut.shift_left(1)),
					dataIn.eq(Cat(cipo, dataIn[:-1])),
				]
				with m.If(bit == 7):
					m.next = 'DONE'
			with m.State('DONE'):
				m.d.comb += self.done.eq(1)
				m.d.sync += self.r_data.eq(Cat(cipo, dataIn[:-1]))
				with m.If(self.xfer):
					m.d.sync += dataOut.eq(self.w_data)
					m.next = 'TRANSFER'
				with m.Else():
					m.next = 'IDLE'

		m.d.comb += [
			bus.cs.o.eq(self.cs),
			bus.clk.o0.eq(clkEn),
			bus.clk.o1.eq(0),
			bus.clk.o_clk.eq(ClockSignal('sync')),
		]
		return m
