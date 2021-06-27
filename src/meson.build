# SPDX-License-Identifier: BSD-3-Clause
chip = get_option('chip')

dragonUSB = dependency(
	'dragonUSB',
	required: true,
	version: '>=0.0.1',
	fallback: ['dragonUSB', 'dragonUSB_dep'],
	default_options: [
		'chip=@0@'.format(chip),
		'interfaces=1',
		'endpoints=0',
		'epBufferSize=64',
		'configDescriptors=1',
		'ifaceDescriptors=1',
		'endpointDescriptors=0',
		'strings=4',
		'drivers=dfu'
	]
)

subdir(chip)

bootloaderSrc = [
	platformSrc, 'bootloader.cxx', 'descriptors.cxx'
]

executable(
	'bootloader',
	bootloaderSrc,
	include_directories: include_directories('../include'),
	dependencies: [platform, dragonUSB],
	link_args: ['-T', '@0@/@1@/linkerScript.ld'.format(meson.current_source_dir(), chip)],
	gnu_symbol_visibility: 'inlineshidden',
	name_suffix: 'elf',
	build_by_default: true,
	install: false
)
