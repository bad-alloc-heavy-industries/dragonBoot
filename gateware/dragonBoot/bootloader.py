from amaranth import Elaboratable, Module

__all__ = (
	'DragonBoot',
)

class DragonBoot(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		return m
