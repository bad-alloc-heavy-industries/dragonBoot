# SPDX-License-Identifier: BSD-3-Clause
chip = get_option('chip')

if chip in ['tm4c123gh6pm']
	dfuOptions = [
		'dfuFlashBufferSize=128',
		'dfuFlashPageSize=4096'
	]
elif chip in ['atxmega256a3u']
	dfuOptions = [
		'dfuFlashBufferSize=256',
		'dfuFlashPageSize=4096'
	]
endif

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
	] + dfuOptions
)

subdir(chip)

bootloaderSrc = [
	platformSrc, 'bootloader.cxx', 'descriptors.cxx'
]

bootloader = executable(
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

objdump = find_program('objdump')
run_target(
	'disasm',
	command: [objdump, '-dC', bootloader]
)

size = find_program('get_fw_size.py', dirs: '@0@/../scripts'.format(meson.current_source_dir()))
run_target(
	'size',
	command: [
		size,
		'--flash-size=262144', # 256KiB of Flash
		'--ram-size=32768', # 32KiB of RAM
		'--size-prog=@0@'.format(find_program('size').path()),
		bootloader
	]
)
