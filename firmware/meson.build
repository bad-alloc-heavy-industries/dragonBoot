# SPDX-License-Identifier: BSD-3-Clause
chip = get_option('chip')

if chip in ['tm4c123gh6pm']
	dfuOptions = [
		'dfuFlashBufferSize=128',
		'dfuFlashPageSize=4096',
		'dfuFlashEraseSize=1024'
	]
	chipFlash = 262144 # 256KiB of Flash
	chipRAM = 32768 # 32KiB of RAM
	chipBaseAddr = 0 # Flash starts at 0x00000000
	bootloaderSerialLength = 0
elif chip in ['stm32f1']
	dfuOptions = [
		'dfuFlashBufferSize=1024',
		'dfuFlashPageSize=4096',
		'dfuFlashEraseSize=1024'
	]
	chipFlash = 131072 # 128KiB of Flash
	chipRAM = 20480 # 20KiB of RAM
	chipBaseAddr = 0x08000000 # Flash starts at 0x08000000
	bootloaderSerialLength = 8
elif chip in ['atxmega256a3u']
	dfuOptions = [
		'dfuFlashBufferSize=256',
		'dfuFlashPageSize=4096',
		'dfuFlashEraseSize=256'
	]
	chipFlash = 270336 # 256KiB + 8KiB of Flash
	chipRAM = 32768 # 32KiB of RAM
	chipBaseAddr = 0 # Flash starts at 0x00000000
	bootloaderSerialLength = 0
endif

subdir(chip)

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
		'strings=5',
		'drivers=dfu'
	] + dfuOptions
)

bootloaderSrc = [
	platformSrc, 'bootloader.cxx', 'descriptors.cxx'
]

bootloader = executable(
	'bootloader',
	bootloaderSrc,
	cpp_args: [
		'-DSERIAL_LENGTH=@0@'.format(bootloaderSerialLength),
		'-DBOOTLOADER_TARGET=@0@'.format(get_option('target').to_upper())
	],
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
		'--flash-size=@0@'.format(chipFlash),
		'--ram-size=@0@'.format(chipRAM),
		'--base-addr=@0@'.format(chipBaseAddr),
		'--size-prog=@0@'.format(find_program('size').path()),
		bootloader
	]
)
