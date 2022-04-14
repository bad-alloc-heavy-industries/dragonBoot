# SPDX-License-Identifier: BSD-3-Clause
from amaranth.build import Resource, Pins, Clock, Attrs
from amaranth_boards.resources.interface import SPIResource, ULPIResource
from ..platform import DragonICE40Platform, Flash

__all__ = (
	'AudioInterfacePlatform',
)

class AudioInterfacePlatform(DragonICE40Platform):
	device = 'iCE40HX8K'
	package = 'BG121'
	toolchain = 'IceStorm'

	default_clk = 'sys_clk'

	resources = [
		Resource(
			'sys_clk', 0,
			Pins('B6', dir = 'i', assert_width = 1),
			Clock(36.864e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),

		SPIResource(
			'flash_spi', 0,
			clk = 'L10',
			copi = 'K9',
			cipo = 'J9',
			cs_n = 'K10',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		# A7 is the internal config interface, E11 is the DAC's

		ULPIResource(
			'ulpi', 0,
			clk = 'G1', clk_dir = 'i',
			data = 'E1 F2 F1 G2 H2 H1 J2 J1',
			dir = 'D1',
			nxt = 'E2',
			stp = 'D2',
			rst = 'C1', rst_invert = True,
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS'),
			clk_attrs = Attrs(GLOBAL = True)
		),
	]

	connectors = []

	flash = Flash(
		size = 512 * 1024,
		pageSize = 256,
		erasePageSize = 4096,
		eraseCommand = 0x20
	)

	def build(self, elaboratable, name = 'top', build_dir = 'build', do_build = True,
		program_opts = None, do_program = False, **kwargs
	):
		super().build(
			elaboratable, name, build_dir, do_build, program_opts, do_program,
			synth_opts = ['-abc9'], nextpnr_opts = ['--tmg-ripup', '--seed=0'],
			**kwargs
			#'--opt-timing',
		)
