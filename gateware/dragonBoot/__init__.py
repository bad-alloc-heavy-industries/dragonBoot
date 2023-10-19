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

	# Build the command line parser
	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter,
		description = 'dragonBoot')
	parser.add_argument('--verbose', '-v', action = 'store_true', help = 'Enable debugging output')

	# Create action subparsers for building and simulation
	actions = parser.add_subparsers(dest = 'action', required = True)
	buildAction = actions.add_parser('build', help = 'build the dragonBoot DFU gateware')
	actions.add_parser('sim', help = 'Simulate and test the gateware components')

	# Populate the possible build targets
	platforms = listPlatforms()
	buildAction.add_argument('--target', action = 'store', required = True, choices = platforms.keys())

	# Parse the command line and, if `-v` is specified, bump the logging level
	args = parser.parse_args()
	if args.verbose:
		from logging import root, DEBUG
		root.setLevel(DEBUG)

	# Dispatch the action requested
	if args.action == 'sim':
		from .sim.framework import run_sims
		run_sims(pkg = 'dragonBoot/sim', result_dir = 'build')
		return 0
	elif args.action == 'build':
		platform = platforms[args.target]()
		platform.build(DragonBoot(), name = 'dragonBoot')
		return 0
