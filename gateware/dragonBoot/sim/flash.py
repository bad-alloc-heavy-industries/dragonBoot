# SPDX-License-Identifier: BSD-3-Clause
from arachne.core.sim import sim_case
from amaranth import Record
from amaranth.hdl.rec import DIR_FANOUT, DIR_FANIN
from amaranth.sim import Simulator, Settle

from ..flash import SPIFlash
from .dfu import dfuData

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
	erasePageSize = 256
	eraseCommand = 0x20

	def request(self, name, number, xdr = None):
		assert name == 'flash'
		assert number == 0
		assert xdr is not None
		assert xdr['clk'] == 2
		return bus

@sim_case(
	domains = (('sync', 60e6),),
	platform = Platform(),
	dut = SPIFlash(resource = ('flash', 0), flashSize = 512 * 1024)
)
def spiFlash(sim : Simulator, dut : SPIFlash):
	def spiTransact(copi = None, cipo = None):
		if copi is not None and cipo is not None:
			assert len(copi) == len(cipo)
		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		yield Settle()
		yield
		assert (yield bus.cs.o) == 1
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				if cipo is not None and cipo[byte] is not None:
					yield bus.cipo.i.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield Settle()
				yield
				if copi is not None and copi[byte] is not None:
					assert (yield bus.copi.o) == ((copi[byte] << bit) & 0x80) >> 7
			if cipo is not None and cipo[byte] is not None:
				yield bus.cipo.i.eq(0)
			assert (yield bus.cs.o) == 1
			yield Settle()
			yield
		assert (yield bus.cs.o) == 0

	def domainSync():
		yield
		yield dut.start.eq(1)
		yield Settle()
		yield
		assert (yield dut.readAddr) == 0
		assert (yield dut.eraseAddr) == 0
		assert (yield dut.writeAddr) == 0
		yield dut.start.eq(0)
		yield Settle()
		yield
		assert (yield bus.cs.o) == 0
		yield Settle()
		yield from spiTransact(copi = (0x06,))
		yield
		yield from spiTransact(copi = (0x20, 0x00, 0x00, 0x00))
		yield
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))
		yield
	yield domainSync, 'sync'
