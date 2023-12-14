# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module, Instance, Signal, Const, ClockDomain, ClockSignal
from torii.build import Resource, Pins, Clock, Attrs
from torii.platform.resources.interface import SPIResource, DirectUSBResource
from ..platform import DragonICE40Platform, Flash, platform

__all__ = (
	'TinyFPGABXPlatform',
)

class USBPLL(Elaboratable):
	def elaborate(self, platform: 'TinyFPGABXPlatform'):
		m = Module()
		m.domains.sync = ClockDomain()
		m.domains.usb = ClockDomain()
		m.domains.usb_io = ClockDomain()

		platform.lookup(platform.default_clk).attrs['GLOBAL'] = False

		clk12MHz = Signal()
		clk16MHz = platform.request(platform.default_clk, dir = 'i').i
		clk48MHz = Signal()

		m.submodules.pll = Instance(
			'SB_PLL40_CORE',
			i_REFERENCECLK = clk16MHz,
			i_RESETB = Const(1),
			i_BYPASS = Const(0),

			o_PLLOUTGLOBAL = clk48MHz,

			p_FEEDBACK_PATH = 'SIMPLE',
			p_PLLOUT_SELECT = 'GENCLK',

			# 48MHz from 16MHz
			p_DIVR = 0,
			p_DIVF = 47,
			p_DIVQ = 4,
			p_FILTER_RANGE = 1,
		)

		# This isn't great but there's not much we can do about this thanks to how the package clock's been spec'd
		clkCounter = Signal(range(4))
		m.d.usb_io += clkCounter.eq(clkCounter + 1)

		platform.add_clock_constraint(clk12MHz, 12e6)
		platform.add_clock_constraint(clk48MHz, 48e6)

		m.d.comb += [
			clk12MHz.eq(clkCounter[1]),
			ClockSignal('sync').eq(clk12MHz),
			ClockSignal('usb').eq(clk12MHz),
			ClockSignal('usb_io').eq(clk48MHz),
		]
		return m

@platform
class TinyFPGABXPlatform(DragonICE40Platform):
	""" Platform for the `TinyFPGA BX <https://github.com/tinyfpga/TinyFPGA-BX>`_.

	Used to allow the device gateware to be upgraded or swapped out on the fly,
	this defines the bare minimum of the resources on the board requried to to perform this task:

	* A SPI resource to access the configuration Flash (An AT25SF081)
	* The direct USB interface used to provide USB LS/FS to the board
	* The clock resource used to run the non-USB logic
	* The Flash configuration object required to describe the AT25SF081 Flash
	"""

	device = 'iCE40LP8K'
	package = 'CM81'

	default_clk = 'sys_clk'

	resources = [
		Resource(
			'sys_clk', 0,
			Pins('B2', dir = 'i', assert_width = 1),
			Clock(16e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),

		SPIResource(
			'flash_spi', 0,
			clk = 'G7',
			copi = 'G6',
			cipo = 'H7',
			cs_n = 'F7',
			role = 'controller',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		DirectUSBResource(
			'usb', 0,
			d_p = 'B4',
			d_n = 'A4',
			pullup = 'A3',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS'),
		),
	]

	connectors = []

	flash = Flash(
		size = 1 * 1024 * 1024,
		pageSize = 256,
		erasePageSize = 4096,
		eraseCommand = 0x20
	)

	pll_type = USBPLL
	# Unlike other platforms, this one waits 1s for the USB connection to come up, and if that fails,
	# warmboots into w/e the user has in slot 1.
	timeout = 1e0
