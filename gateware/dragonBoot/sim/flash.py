# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module, Record
from torii.lib.fifo import AsyncFIFO
from torii.hdl.rec import DIR_FANOUT, DIR_FANIN
from torii.sim import Settle
from torii.test import ToriiTestCase

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
	def __init__(self, *, resource):
		self._fifo = AsyncFIFO(width = 8, depth = Platform.flash.erasePageSize, r_domain = 'sync', w_domain = 'usb')
		self._flash = SPIFlash(resource = resource, fifo = self._fifo)

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

	def elaborate(self, _):
		m = Module()
		m.submodules.fifo = self._fifo
		m.submodules.flash = self._flash
		return m

class SPIFlashTestCase(ToriiTestCase):
	dut : DUT = DUT
	dut_args = {
		'resource': ('flash', 0)
	}
	domains = (('sync', 60e6), ('usb', 60e6))
	platform = Platform()

	def spiTransact(self, copi = None, cipo = None, partial = False, continuation = False):
		if copi is not None and cipo is not None:
			self.assertEqual(len(copi), len(cipo))

		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		self.assertEqual((yield bus.clk.o), 1)
		if continuation:
			yield Settle()
			self.assertEqual((yield bus.cs.o), 1)
		else:
			self.assertEqual((yield bus.cs.o), 0)
			yield Settle()
		yield
		self.assertEqual((yield bus.clk.o), 1)
		self.assertEqual((yield bus.cs.o), 1)
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				self.assertEqual((yield bus.clk.o), 0)
				if copi is not None and copi[byte] is not None:
					self.assertEqual((yield bus.copi.o), ((copi[byte] << bit) & 0x80) >> 7)
				self.assertEqual((yield bus.cs.o), 1)
				yield Settle()
				if cipo is not None and cipo[byte] is not None:
					yield bus.cipo.i.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield
				self.assertEqual((yield bus.clk.o), 1)
				self.assertEqual((yield bus.cs.o), 1)
				yield Settle()
				yield
			if byte < bytes - 1:
				self.assertEqual((yield bus.clk.o), 1)
				self.assertEqual((yield bus.cs.o), 1)
			self.assertEqual((yield self.dut.done), 0)
			yield Settle()
			if cipo is not None and cipo[byte] is not None:
				yield bus.cipo.i.eq(0)
			if byte < bytes - 1:
				yield
		if not partial:
			assert (yield bus.clk.o) == 1
			assert (yield bus.cs.o) == 0
			yield Settle()
			yield

	@ToriiTestCase.simulation
	def testSPIFlash(self):
		fifo = self.dut._fifo

		@ToriiTestCase.sync_domain(domain = 'sync')
		def domainSync(self: SPIFlashTestCase):
			yield self.dut.beginAddr.eq(0)
			yield self.dut.endAddr.eq(4096)
			yield from self.spiTransact(copi = (0xAB,))
			yield Settle()
			yield
			yield Settle()
			yield
			yield self.dut.resetAddrs.eq(1)
			yield Settle()
			yield
			yield self.dut.resetAddrs.eq(0)
			yield Settle()
			yield
			yield self.dut.start.eq(1)
			yield self.dut.byteCount.eq(len(dfuData))
			yield Settle()
			yield
			yield self.dut.start.eq(0)
			yield self.dut.byteCount.eq(0)
			yield Settle()
			self.assertEqual((yield self.dut.readAddr), 0)
			self.assertEqual((yield self.dut.eraseAddr), 0)
			self.assertEqual((yield self.dut.writeAddr), 0)
			self.assertEqual((yield bus.cs.o), 0)
			yield
			yield from self.spiTransact(copi = (0x06,))
			yield from self.spiTransact(copi = (0x20, 0x00, 0x00, 0x00))
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x00))
			yield from self.spiTransact(copi = (0x06,))
			self.assertEqual((yield fifo.r_rdy), 0)
			yield from self.spiTransact(copi = (0x02, 0x00, 0x00, 0x00), partial = True)
			yield
			yield Settle()
			self.assertEqual((yield fifo.r_rdy), 0)
			self.assertEqual((yield bus.cs.o), 1)
			self.assertEqual((yield bus.clk.o), 1)
			yield
			yield Settle()
			self.assertEqual((yield fifo.r_rdy), 0)
			self.assertEqual((yield bus.cs.o), 1)
			self.assertEqual((yield bus.clk.o), 1)
			self.dut.fillFIFO = True
			for _ in range(6):
				yield Settle()
				yield
				self.assertEqual((yield bus.cs.o), 1)
				self.assertEqual((yield bus.clk.o), 1)
			yield from self.spiTransact(copi = dfuData[0:64], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 64)
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spiTransact(copi = (0x06,))
			yield from self.spiTransact(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
			yield from self.spiTransact(copi = dfuData[64:128], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 128)
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spiTransact(copi = (0x06,))
			yield from self.spiTransact(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
			yield from self.spiTransact(copi = dfuData[128:192], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 192)
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spiTransact(copi = (0x06,))
			yield from self.spiTransact(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
			yield from self.spiTransact(copi = dfuData[192:256], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 256)
			yield from self.spiTransact(copi = (0x05, None), cipo = (None, 0x00))

			self.assertEqual((yield self.dut.done), 1)
			yield self.dut.finish.eq(1)
			yield
			self.assertEqual((yield self.dut.done), 1)
			yield self.dut.finish.eq(0)
			yield Settle()
			yield
			self.assertEqual((yield self.dut.done), 0)
			yield from self.settle(2)
		domainSync(self)

		@ToriiTestCase.sync_domain(domain = 'usb')
		def domainUSB(self: SPIFlashTestCase):
			while not self.dut.fillFIFO:
				yield
			yield fifo.w_en.eq(1)
			for byte in dfuData:
				yield fifo.w_data.eq(byte)
				yield
			yield fifo.w_en.eq(0)
			yield
		domainUSB(self)
