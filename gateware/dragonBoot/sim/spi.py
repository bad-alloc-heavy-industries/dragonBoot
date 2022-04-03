# SPDX-License-Identifier: BSD-3-Clause
from arachne.core.sim import sim_case
from amaranth import Record
from amaranth.hdl.rec import DIR_FANOUT, DIR_FANIN
from amaranth.sim import Simulator, Settle

from ..spi import SPIBus

bus = Record((
	('clk', [
		('o0', 1, DIR_FANOUT),
		('o1', 1, DIR_FANOUT),
		('o_clk', 1, DIR_FANOUT),
	]),
	('cs', [
		('o', 1, DIR_FANOUT),
	]),
	('copi', [
		('o', 1, DIR_FANOUT),
	]),
	('cipo', [
		('i', 1, DIR_FANIN),
	]),
))

class Platform:
	flashSize = 512 * 1024

	def request(self, name, number, xdr = None):
		assert name == 'flash'
		assert number == 0
		assert xdr is not None
		assert xdr['clk'] == 2
		return bus

@sim_case(
	domains = (('sync', 60e6),),
	platform = Platform(),
	dut = SPIBus(resource = ('flash', 0))
)
def spiBus(sim : Simulator, dut : SPIBus):
	def sendRecv(dataOut, dataIn, overlap = False):
		yield dut.w_data.eq(dataOut)
		yield dut.xfer.eq(1)
		yield Settle()
		yield
		yield dut.xfer.eq(0)
		yield Settle()
		yield
		for bit in range(8):
			yield bus.cipo.i.eq((dataIn >> (7 - bit)) & 1)
			yield Settle()
			yield
			assert (yield bus.copi.o) == (dataOut >> (7 - bit)) & 1
		assert (yield dut.done) == 1
		if not overlap:
			yield
			yield Settle()
			assert (yield dut.done) == 0
			assert (yield dut.r_data) == dataIn

	def domainSync():
		yield
		yield dut.cs.eq(1)
		yield Settle()
		yield
		yield from sendRecv(0x0F, 0xF0)
		yield
		yield dut.cs.eq(0)
		yield Settle()
		yield
		yield dut.cs.eq(1)
		yield Settle()
		yield
		yield from sendRecv(0xAA, 0x55, overlap = True)
		yield from sendRecv(0x55, 0xAA, overlap = False)
		yield
		yield dut.cs.eq(0)
		yield Settle()
		yield
	yield domainSync, 'sync'
