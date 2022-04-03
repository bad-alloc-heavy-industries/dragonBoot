# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, Signal
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
	def __init__(self, *, resource, flashSize : int):
		self._flashResource = resource
		self._flashSize = flashSize

		self.start = Signal()
		self.done = Signal()
		self.readAddr = Signal(24)
		self.eraseAddr = Signal(24)
		self.writeAddr = Signal(24)
		self.endAddr = Signal(24)

	def elaborate(self, platform):
		m = Module()
		m.submodules.flash = flash = SPIBus(resource = self._flashResource)

		op = Signal(SPIFlashOp, reset = SPIFlashOp.none)
		enableStep = Signal(range(4))
		processStep = Signal(range(7))

		m.d.comb += flash.xfer.eq(0)

		with m.FSM(name = 'flash'):
			with m.State('IDLE'):
				m.d.sync += [
					enableStep.eq(0),
					processStep.eq(0),
				]
				with m.If(self.start):
					m.d.sync += op.eq(SPIFlashOp.erase)
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
						m.d.sync += self.eraseAddr.eq(self.eraseAddr + platform.erasePageSize)
						m.next = 'ERASE_WAIT'
			with m.State('ERASE_WAIT'):
				m.next = 'WRITE_ENABLE'
			with m.State('WRITE_CMD'):
				flash.w_data.eq(platform.eraseCommand)
				m.next = 'WRITE'
			with m.State('WRITE'):
				m.d.sync += op.eq(SPIFlashOp.write)
				m.next = 'WRITE_WAIT'
			with m.State('WRITE_WAIT'):
				m.next = 'IDLE'

		return m
