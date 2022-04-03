# SPDX-License-Identifier: BSD-3-Clause
from amaranth import Elaboratable, Module, ClockDomain, ResetSignal
from .usb import USBInterface

__all__ = (
	'DragonBoot',
)

class DragonBoot(Elaboratable):
	def elaborate(self, platform):
		m = Module()
		m.domains += ClockDomain('usb')
		m.submodules.usb = usb = USBInterface(resource = ('ulpi', 0), dfuResource = ('flash_spi', 0))

		m.d.comb += ResetSignal('usb').eq(0)
		return m
