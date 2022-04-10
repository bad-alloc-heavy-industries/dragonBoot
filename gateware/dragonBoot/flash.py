# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, Signal
from amaranth.lib.fifo import AsyncFIFO
from enum import IntEnum, auto, unique

from .spi import SPIBus

__all__ = (
	'SPIFlash',
	'SPIFlashOp',
)

@unique
class SPIFlashOp(IntEnum):
	none = auto()
	erase = auto()
	write = auto()

@unique
class SPIFlashCmd(IntEnum):
	pageProgram = 0x02
	readStatus = 0x05
	writeEnable = 0x06

class SPIFlash(Elaboratable):
	def __init__(self, *, resource, fifo : AsyncFIFO, flashSize : int):
		self._flashResource = resource
		self._fifo = fifo
		self._flashSize = flashSize

		self.start = Signal()
		self.done = Signal()
		self.finish = Signal()
		self.readAddr = Signal(24)
		self.eraseAddr = Signal(24)
		self.writeAddr = Signal(24)
		self.endAddr = Signal(24)
		self.byteCount = Signal(24)

	def elaborate(self, platform):
		m = Module()
		m.submodules.spi = flash = SPIBus(resource = self._flashResource)
		fifo = self._fifo

		op = Signal(SPIFlashOp, reset = SPIFlashOp.none)
		enableStep = Signal(range(4))
		processStep = Signal(range(7))
		writeTrigger = Signal()
		writeCount = Signal(range(platform.flashPageSize + 1))
		byteCount = Signal.like(self.byteCount)

		m.d.comb += [
			self.done.eq(0),
			flash.xfer.eq(0),
			flash.w_data.eq(fifo.r_data),
		]

		with m.FSM(name = 'flash'):
			with m.State('IDLE'):
				m.d.sync += [
					enableStep.eq(0),
					processStep.eq(0),
				]
				with m.If(self.start):
					m.d.sync += [
						op.eq(SPIFlashOp.erase),
						byteCount.eq(self.byteCount),
					]
					m.next = 'WRITE_ENABLE'
			with m.State('WRITE_ENABLE'):
				with m.Switch(enableStep):
					with m.Case(0):
						m.d.sync += [
							flash.cs.eq(1),
							enableStep.eq(1),
						]
					with m.Case(1):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.writeEnable),
						]
						m.d.sync += enableStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								enableStep.eq(3),
							]
					with m.Case(3):
						m.d.sync += enableStep.eq(0)
						with m.If(op == SPIFlashOp.erase):
							m.next = 'ERASE_CMD'
						with m.Else():
							m.next = 'WRITE_CMD'
			with m.State('ERASE_CMD'):
				with m.Switch(processStep):
					with m.Case(0):
						m.d.sync += [
							flash.cs.eq(1),
							processStep.eq(1),
						]
					with m.Case(1):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(platform.eraseCommand),
						]
						m.d.sync += processStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[16:24]),
							]
							m.d.sync += processStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[8:16]),
							]
							m.d.sync += processStep.eq(4)
					with m.Case(4):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[0:8]),
							]
							m.d.sync += processStep.eq(5)
					with m.Case(5):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								processStep.eq(6),
							]
					with m.Case(6):
						m.d.sync += [
							self.eraseAddr.eq(self.eraseAddr + platform.erasePageSize),
							processStep.eq(0),
						]
						m.next = 'ERASE_WAIT'
			with m.State('ERASE_WAIT'):
				with m.Switch(processStep):
					with m.Case(0):
						m.d.sync += [
							flash.cs.eq(1),
							processStep.eq(1),
						]
					with m.Case(1):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.readStatus),
						]
						m.d.sync += processStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(0),
							]
							m.d.sync += processStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								processStep.eq(4),
							]
					with m.Case(4):
						m.d.sync += processStep.eq(0)
						with m.If(~flash.r_data[0]):
							with m.If((self.writeAddr + byteCount) <= self.endAddr):
								m.d.sync += op.eq(SPIFlashOp.write)
							m.next = 'WRITE_ENABLE'
			with m.State('WRITE_CMD'):
				with m.Switch(processStep):
					with m.Case(0):
						m.d.sync += [
							flash.cs.eq(1),
							processStep.eq(1),
						]
					with m.Case(1):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.pageProgram),
						]
						m.d.sync += processStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[16:24]),
							]
							m.d.sync += processStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[8:16]),
							]
							m.d.sync += processStep.eq(4)
					with m.Case(4):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[0:8]),
							]
							m.d.sync += processStep.eq(5)
					with m.Case(5):
						with m.If(flash.done):
							m.d.sync += [
								writeTrigger.eq(1),
								processStep.eq(0)
							]
							m.next = 'WRITE'
			with m.State('WRITE'):
				m.d.sync += writeTrigger.eq(0)
				with m.If(flash.done | writeTrigger):
					with m.If(fifo.r_rdy):
						m.d.comb += [
							flash.xfer.eq(1),
							fifo.r_en.eq(1),
						]
						m.d.sync += [
							writeCount.eq(writeCount + 1),
							byteCount.eq(byteCount - 1),
						]
						with m.If((writeCount == platform.flashPageSize - 1) | (byteCount == 1)):
							m.next = 'WRITE_FINISH'
					with m.Else():
						m.next = 'DATA_WAIT'
			with m.State('DATA_WAIT'):
				with m.If(fifo.r_rdy):
					m.d.sync += writeTrigger.eq(1)
					m.next = 'WRITE'
			with m.State('WRITE_FINISH'):
				with m.Switch(processStep):
					with m.Case(0):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								processStep.eq(1),
							]
					with m.Case(1):
						m.d.sync += [
							self.writeAddr.eq(self.writeAddr + writeCount),
							writeCount.eq(0),
							processStep.eq(0),
						]
						m.next = 'WRITE_WAIT'
			with m.State('WRITE_WAIT'):
				with m.Switch(processStep):
					with m.Case(0):
						m.d.sync += [
							flash.cs.eq(1),
							processStep.eq(1),
						]
					with m.Case(1):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.readStatus),
						]
						m.d.sync += processStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(0),
							]
							m.d.sync += processStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								processStep.eq(4),
							]
					with m.Case(4):
						m.d.sync += processStep.eq(0)
						with m.If(~flash.r_data[0]):
							with m.If(byteCount):
								m.next = 'WRITE_ENABLE'
							with m.Else():
								m.d.sync += op.eq(SPIFlashOp.none)
								m.next = 'FINISH'
			with m.State('FINISH'):
				m.d.comb += self.done.eq(1)
				with m.If(self.finish):
					m.next = 'IDLE'

		return m
