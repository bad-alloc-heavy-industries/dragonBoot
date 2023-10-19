# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module, Signal, Instance
from torii.platform.vendor.lattice.ice40 import ICE40Platform
from torii.platform.vendor.lattice.ecp5 import ECP5Platform

__all__ = (
	'Warmboot',
)

class Warmboot(Elaboratable):
	def __init__(self):
		self.trigger = Signal()

	def elaborate(self, platform) -> Module:
		m = Module()
		if isinstance(platform, ICE40Platform):
			warmbootSelect = Signal(2)
			m.d.comb += warmbootSelect.eq(0b01)

			m.submodules += Instance(
				'SB_WARMBOOT',
				i_BOOT = self.trigger,
				i_S0 = warmbootSelect[0],
				i_S1 = warmbootSelect[1],
			)
		elif isinstance(platform, ECP5Platform):
			raise NotImplementedError("ECP5 support is planned but not yet implemented")
		return m
