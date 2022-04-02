# SPDX-License-Identifier: BSD-3-Clause
project(
	'dragonBoot',
	'cpp',
	default_options: [
		'cpp_std=c++17',
		'warning_level=3',
		'buildtype=release',
		'strip=true',
		'b_ndebug=if-release',
		'b_lto=true'
	],
	version: '0.0.1',
	meson_version: '>= 0.53',
	subproject_dir: 'deps'
)

if not meson.is_cross_build()
	error('dragonUSB must be cross-compiled to the target microcontroller and cannot be built for the host machine')
endif

cxx = meson.get_compiler('cpp')

subdir('firmware')

runClangTidy = find_program('runClangTidy.py')
run_target(
	'clang-tidy',
	command: [runClangTidy, '-s', meson.current_source_dir(), '-p', meson.current_build_dir()]
)
