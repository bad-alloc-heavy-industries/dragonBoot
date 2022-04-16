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
	releasePowerDown = 0xAB

class SPIFlash(Elaboratable):
	def __init__(self, *, resource, fifo : AsyncFIFO, flashSize : int):
		self._flashResource = resource
		self._fifo = fifo
		self._flashSize = flashSize

		self.ready = Signal()
		self.start = Signal()
		self.done = Signal()
		self.finish = Signal()
		self.resetAddrs = Signal()
		self.beginAddr = Signal(24)
		self.endAddr = Signal(24)
		self.byteCount = Signal(24)

		self.readAddr = Signal(24)
		self.eraseAddr = Signal(24)
		self.writeAddr = Signal(24)

	def elaborate(self, platform) -> Module:
		m = Module()
		m.submodules.spi = flash = SPIBus(resource = self._flashResource)
		fifo = self._fifo

		op = Signal(SPIFlashOp, reset = SPIFlashOp.none)
		resetStep = Signal(range(2))
		enableStep = Signal(range(3))
		eraseCmdStep = Signal(range(6))
		eraseWaitStep = Signal(range(4))
		writeCmdStep = Signal(range(5))
		writeFinishStep = Signal(range(2))
		writeWaitStep = Signal(range(4))
		writeTrigger = Signal()
		writeCount = Signal(range(platform.flash.pageSize + 1))
		byteCount = Signal.like(self.byteCount)

		m.d.comb += [
			self.ready.eq(0),
			self.done.eq(0),
			flash.xfer.eq(0),
			flash.w_data.eq(fifo.r_data),
		]

		with m.FSM(name = 'flash'):
			with m.State('RESET'):
				with m.Switch(resetStep):
					with m.Case(0):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.releasePowerDown),
						]
						m.d.sync += [
							flash.cs.eq(1),
							resetStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.comb += self.ready.eq(1)
							m.d.sync += [
								flash.cs.eq(0),
								enableStep.eq(0),
							]
							m.next = 'IDLE'
			with m.State('IDLE'):
				m.d.sync += [
					enableStep.eq(0),
					eraseCmdStep.eq(0),
					eraseWaitStep.eq(0),
					writeCmdStep.eq(0),
					writeFinishStep.eq(0),
					writeWaitStep.eq(0),
				]
				with m.If(self.resetAddrs):
					m.d.sync += [
						self.readAddr.eq(self.beginAddr),
						self.eraseAddr.eq(self.beginAddr),
						self.writeAddr.eq(self.beginAddr),
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
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.writeEnable),
						]
						m.d.sync += [
							flash.cs.eq(1),
							enableStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								enableStep.eq(2),
							]
					with m.Case(2):
						m.d.sync += enableStep.eq(0)
						with m.If(op == SPIFlashOp.erase):
							m.next = 'ERASE_CMD'
						with m.Else():
							m.next = 'WRITE_CMD'
			with m.State('ERASE_CMD'):
				with m.Switch(eraseCmdStep):
					with m.Case(0):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(platform.flash.eraseCommand),
						]
						m.d.sync += [
							flash.cs.eq(1),
							eraseCmdStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[16:24]),
							]
							m.d.sync += eraseCmdStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[8:16]),
							]
							m.d.sync += eraseCmdStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.eraseAddr[0:8]),
							]
							m.d.sync += eraseCmdStep.eq(4)
					with m.Case(4):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								eraseCmdStep.eq(5),
							]
					with m.Case(5):
						m.d.sync += [
							self.eraseAddr.eq(self.eraseAddr + platform.flash.erasePageSize),
							eraseCmdStep.eq(0),
						]
						m.next = 'ERASE_WAIT'
			with m.State('ERASE_WAIT'):
				with m.Switch(eraseWaitStep):
					with m.Case(0):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.readStatus),
						]
						m.d.sync += [
							flash.cs.eq(1),
							eraseWaitStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(0),
							]
							m.d.sync += eraseWaitStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								eraseWaitStep.eq(3),
							]
					with m.Case(3):
						m.d.sync += eraseWaitStep.eq(0)
						with m.If(~flash.r_data[0]):
							with m.If((self.writeAddr + byteCount) <= self.endAddr):
								m.d.sync += op.eq(SPIFlashOp.write)
							m.next = 'WRITE_ENABLE'
			with m.State('WRITE_CMD'):
				with m.Switch(writeCmdStep):
					with m.Case(0):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.pageProgram),
						]
						m.d.sync += [
							flash.cs.eq(1),
							writeCmdStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[16:24]),
							]
							m.d.sync += writeCmdStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[8:16]),
							]
							m.d.sync += writeCmdStep.eq(3)
					with m.Case(3):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(self.writeAddr[0:8]),
							]
							m.d.sync += writeCmdStep.eq(4)
					with m.Case(4):
						with m.If(flash.done):
							m.d.sync += [
								writeTrigger.eq(1),
								writeCmdStep.eq(0)
							]
							m.next = 'WRITE'
			with m.State('WRITE'):
				with m.If(flash.done | writeTrigger):
					m.d.sync += writeTrigger.eq(0)
					with m.If(fifo.r_rdy):
						m.d.comb += [
							flash.xfer.eq(1),
							fifo.r_en.eq(1),
						]
						m.d.sync += [
							writeCount.eq(writeCount + 1),
							byteCount.eq(byteCount - 1),
						]
						with m.If((writeCount == platform.flash.pageSize - 1) | (byteCount == 1)):
							m.next = 'WRITE_FINISH'
					with m.Else():
						m.next = 'DATA_WAIT'
			with m.State('DATA_WAIT'):
				with m.If(fifo.r_rdy):
					m.d.sync += writeTrigger.eq(1)
					m.next = 'WRITE'
			with m.State('WRITE_FINISH'):
				with m.Switch(writeFinishStep):
					with m.Case(0):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								writeFinishStep.eq(1),
							]
					with m.Case(1):
						m.d.sync += [
							self.writeAddr.eq(self.writeAddr + writeCount),
							writeCount.eq(0),
							writeFinishStep.eq(0),
						]
						m.next = 'WRITE_WAIT'
			with m.State('WRITE_WAIT'):
				with m.Switch(writeWaitStep):
					with m.Case(0):
						m.d.comb += [
							flash.xfer.eq(1),
							flash.w_data.eq(SPIFlashCmd.readStatus),
						]
						m.d.sync += [
							flash.cs.eq(1),
							writeWaitStep.eq(1),
						]
					with m.Case(1):
						with m.If(flash.done):
							m.d.comb += [
								flash.xfer.eq(1),
								flash.w_data.eq(0),
							]
							m.d.sync += writeWaitStep.eq(2)
					with m.Case(2):
						with m.If(flash.done):
							m.d.sync += [
								flash.cs.eq(0),
								writeWaitStep.eq(3),
							]
					with m.Case(3):
						m.d.sync += writeWaitStep.eq(0)
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
