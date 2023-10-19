# SPDX-License-Identifier: BSD-3-Clause
from torii import Record
from torii.hdl.rec import DIR_FANOUT, DIR_FANIN
from torii.sim import Settle
from torii.test import ToriiTestCase

from ..spi import SPIBus

bus = Record((
	('clk', [
		('o', 1, DIR_FANOUT),
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

	def request(self, name, number):
		assert name == 'flash'
		assert number == 0
		return bus

class SPIBusTestCase(ToriiTestCase):
	dut : SPIBus = SPIBus
	dut_args = {
		'resource': ('flash', 0)
	}
	domains = (('sync', 60e6), )
	platform = Platform()

	def sendRecv(self, dataOut, dataIn, overlap = False):
		assert (yield bus.clk.o) == 1
		yield self.dut.w_data.eq(dataOut)
		yield self.dut.xfer.eq(1)
		yield from self.settle()
		assert (yield bus.clk.o) == 1
		yield self.dut.xfer.eq(0)
		yield from self.settle()
		for bit in range(8):
			assert (yield bus.clk.o) == 1
			yield bus.cipo.i.eq((dataIn >> (7 - bit)) & 1)
			yield from self.settle()
			assert (yield bus.clk.o) == 0
			assert (yield bus.copi.o) == (dataOut >> (7 - bit)) & 1
			yield from self.settle()
		assert (yield bus.clk.o) == 1
		assert (yield self.dut.done) == 1
		if not overlap:
			yield from self.settle()
			assert (yield bus.clk.o) == 1
			assert (yield self.dut.done) == 0
			assert (yield self.dut.r_data) == dataIn
		yield Settle()

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def testSPIBus(self):
		yield
		assert (yield bus.clk.o) == 1
		yield self.dut.cs.eq(1)
		yield from self.settle()
		yield from self.sendRecv(0x0F, 0xF0)
		yield
		assert (yield bus.clk.o) == 1
		yield self.dut.cs.eq(0)
		yield from self.settle()
		assert (yield bus.clk.o) == 1
		yield self.dut.cs.eq(1)
		yield from self.settle()
		yield from self.sendRecv(0xAA, 0x55, overlap = True)
		yield from self.sendRecv(0x55, 0xAA, overlap = False)
		yield
		yield self.dut.cs.eq(0)
		yield from self.settle()
