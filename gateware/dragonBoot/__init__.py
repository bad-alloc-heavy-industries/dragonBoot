# SPDX-License-Identifier: BSD-3-Clause
# This must be the first thing done as we otherwise race LUNA and we want to set logging up our way
from .logging import configureLogging
configureLogging()

from .platforms import listPlatforms
from .bootloader import DragonBoot

__all__ = (
	'cli',
)

def cli():
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	from arachne.cli import register_cli

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter,
		description = 'dragonBoot')
	actions = parser.add_subparsers(dest = 'action', required = True)
	buildAction = actions.add_parser('build', help = 'build the dragonBoot DFU gateware')
	platforms = listPlatforms()
	buildAction.add_argument('--target', action = 'store', required = True, choices = platforms.keys())

	register_cli(parser = parser)
	args = parser.parse_args()

	if args.action == 'arachne-sim':
		from arachne.core.sim import run_sims
		run_sims(pkg = 'dragonBoot/sim', result_dir = 'build')
		return 0
	elif args.action == 'build':
		platform = platforms[args.target]()
		platform.build(DragonBoot(), name = 'dragonBoot')
		return 0
