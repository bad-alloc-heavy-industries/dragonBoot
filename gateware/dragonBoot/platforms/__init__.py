# SPDX-License-Identifier: BSD-3-Clause
from amaranth.build.plat import Platform
from inspect import isclass
from typing import Dict

__all__ = (
	'listPlatforms',
)

def listPlatforms() -> Dict:
	from pkgutil import walk_packages
	from importlib import import_module
	from inspect import getmembers

	def platformPredicate(member):
		return (
			isclass(member) and
			issubclass(member, Platform) and
			hasattr(member, '_dragonPlatform') and
			member._dragonPlatform
		)

	def mapPlatform(name : str) -> str:
		assert name.endswith('Platform')
		name = name.removesuffix('Platform')
		return f'{name[0].lower()}{name[1:]}'

	platforms = {}
	for _, name, _ in walk_packages(path = ('dragonBoot/platforms',), prefix = f'{__package__}.'):
		pkgImport = import_module(name)
		for name, platform in getmembers(pkgImport, platformPredicate):
			platforms[mapPlatform(name)] = platform
	return platforms
