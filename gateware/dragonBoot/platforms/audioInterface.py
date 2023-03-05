# SPDX-License-Identifier: BSD-3-Clause
from torii.build import Attrs
from torii.platform.resources.interface import SPIResource, ULPIResource
from ..platform import DragonICE40Platform, Flash, platform

__all__ = (
	'AudioInterfacePlatform',
)

@platform
class AudioInterfacePlatform(DragonICE40Platform):
	""" Platform for `HeadphoneAmp's audio interface <https://github.com/dragonmux/HeadphoneAmp>`_.

	Used to allow the device gateware to be upgraded or swapped out on the fly,
	this defines the bare minimum of the resources on the board requried to to perform this task:

	* A SPI resource to access the configuration Flash (A GD25Q40C)
	* The UPLI PHY used to provide USB HS to the board

		* This resource is also responsible for providing our operating clock -
		  the PHY on the board is a USB3318 which produces a 60MHz clock from its associated
		  13MHz clock source.

	* The Flash configuration object required to describe the GD25Q40C Flash
	"""

	device = 'iCE40HX8K'
	package = 'BG121'

	resources = [
		SPIResource(
			'flash_spi', 0,
			clk = 'L10',
			copi = 'K9',
			cipo = 'J9',
			cs_n = 'K10',
			role = 'controller',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

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
