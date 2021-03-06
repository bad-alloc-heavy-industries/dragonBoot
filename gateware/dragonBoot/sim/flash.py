# SPDX-License-Identifier: BSD-3-Clause
from arachne.core.sim import sim_case
from amaranth import Elaboratable, Module, Record
from amaranth.lib.fifo import AsyncFIFO
from amaranth.hdl.rec import DIR_FANOUT, DIR_FANIN
from amaranth.sim import Simulator, Settle

from ..platform import Flash
from ..flash import SPIFlash
from .dfu import dfuData

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
	flash = Flash(
		size = 512 * 1024,
		pageSize = 64,
		erasePageSize = 256,
		eraseCommand = 0x20
	)

	def request(self, name, number):
		assert name == 'flash'
		assert number == 0
		return bus

class DUT(Elaboratable):
	def __init__(self, *, resource, flashSize):
		self._fifo = AsyncFIFO(width = 8, depth = Platform.flash.erasePageSize, r_domain = 'sync', w_domain = 'usb')
		self._flash = SPIFlash(resource = resource, fifo = self._fifo, flashSize = flashSize)

		self.fillFIFO = False

		self.start = self._flash.start
		self.finish = self._flash.finish
		self.done = self._flash.done
		self.resetAddrs = self._flash.resetAddrs
		self.beginAddr = self._flash.beginAddr
		self.endAddr = self._flash.endAddr
		self.readAddr = self._flash.readAddr
		self.eraseAddr = self._flash.eraseAddr
		self.writeAddr = self._flash.writeAddr
		self.byteCount = self._flash.byteCount

	def elaborate(self, platform):
		m = Module()
		m.submodules.fifo = self._fifo
		m.submodules.flash = self._flash
		return m

@sim_case(
	domains = (('sync', 60e6), ('usb', 60e6)),
	platform = Platform(),
	dut = DUT(resource = ('flash', 0), flashSize = 512 * 1024)
)
def spiFlash(sim : Simulator, dut : SPIFlash):
	fifo = dut._fifo

	def spiTransact(copi = None, cipo = None, partial = False, continuation = False):
		if copi is not None and cipo is not None:
			assert len(copi) == len(cipo)
		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		assert (yield bus.clk.o) == 1
		assert (yield bus.cs.o) == (1 if continuation else 0)
		yield Settle()
		yield
		assert (yield bus.clk.o) == 1
		assert (yield bus.cs.o) == 1
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				assert (yield bus.clk.o) == 0
				if copi is not None and copi[byte] is not None:
					assert (yield bus.copi.o) == ((copi[byte] << bit) & 0x80) >> 7
				assert (yield bus.cs.o) == 1
				if cipo is not None and cipo[byte] is not None:
					yield bus.cipo.i.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield Settle()
				yield
				assert (yield bus.clk.o) == 1
				assert (yield bus.cs.o) == 1
				yield Settle()
				yield
			if cipo is not None and cipo[byte] is not None:
				yield bus.cipo.i.eq(0)
			if byte < bytes - 1:# or not partial:
				assert (yield bus.clk.o) == 1
				assert (yield bus.cs.o) == 1
				yield Settle()
				yield
		assert (yield dut.done) == 0
		if not partial:
			assert (yield bus.clk.o) == 1
			assert (yield bus.cs.o) == 0
			yield Settle()
			yield

	def domainSync():
		yield dut.beginAddr.eq(0)
		yield dut.endAddr.eq(4096)
		yield from spiTransact(copi = (0xAB,))
		yield Settle()
		yield
		yield Settle()
		yield
		yield dut.resetAddrs.eq(1)
		yield Settle()
		yield
		yield dut.resetAddrs.eq(0)
		yield Settle()
		yield
		yield dut.start.eq(1)
		yield dut.byteCount.eq(len(dfuData))
		yield Settle()
		yield
		assert (yield dut.readAddr) == 0
		assert (yield dut.eraseAddr) == 0
		assert (yield dut.writeAddr) == 0
		assert (yield bus.cs.o) == 0
		yield dut.start.eq(0)
		yield dut.byteCount.eq(0)
		yield Settle()
		yield
		yield from spiTransact(copi = (0x06,))
		yield from spiTransact(copi = (0x20, 0x00, 0x00, 0x00))
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))
		yield from spiTransact(copi = (0x06,))
		assert (yield fifo.r_rdy) == 0
		yield from spiTransact(copi = (0x02, 0x00, 0x00, 0x00), partial = True)
		yield
		assert (yield bus.cs.o) == 1
		assert (yield bus.clk.o) == 1
		assert (yield fifo.r_rdy) == 0
		assert (yield bus.cs.o) == 1
		assert (yield bus.clk.o) == 1
		yield Settle()
		yield
		assert (yield fifo.r_rdy) == 0
		assert (yield bus.cs.o) == 1
		assert (yield bus.clk.o) == 1
		dut.fillFIFO = True
		for _ in range(5):
			yield Settle()
			yield
			assert (yield bus.cs.o) == 1
			assert (yield bus.clk.o) == 1
		yield from spiTransact(copi = dfuData[0:64], continuation = True)
		assert (yield dut.writeAddr) == 64
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x03))
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))

		yield from spiTransact(copi = (0x06,))
		yield from spiTransact(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
		yield from spiTransact(copi = dfuData[64:128], continuation = True)
		assert (yield dut.writeAddr) == 128
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))

		yield from spiTransact(copi = (0x06,))
		yield from spiTransact(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
		yield from spiTransact(copi = dfuData[128:192], continuation = True)
		assert (yield dut.writeAddr) == 192
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))

		yield from spiTransact(copi = (0x06,))
		yield from spiTransact(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
		yield from spiTransact(copi = dfuData[192:256], continuation = True)
		assert (yield dut.writeAddr) == 256
		yield from spiTransact(copi = (0x05, None), cipo = (None, 0x00))

		assert (yield dut.done) == 1
		yield dut.finish.eq(1)
		yield Settle()
		yield
		assert (yield dut.done) == 1
		yield dut.finish.eq(0)
		yield Settle()
		yield
		assert (yield dut.done) == 0
		yield Settle()
		yield
		yield Settle()
		yield
	yield domainSync, 'sync'

	def domainUSB():
		while not dut.fillFIFO:
			yield
		yield fifo.w_en.eq(1)
		for byte in dfuData:
			yield fifo.w_data.eq(byte)
			yield
		yield fifo.w_en.eq(0)
		yield
	yield domainUSB, 'usb'
