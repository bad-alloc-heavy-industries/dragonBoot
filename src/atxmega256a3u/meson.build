# SPDX-License-Identifier: BSD-3-Clause
add_global_arguments(
	cxx.get_supported_arguments('-fno-jump-tables'),
	language: 'cpp'
)

platform = dependency(
	'dragonAVR',
	required: true,
	version: '>=0.0.1',
	fallback: ['dragonAVR', 'dragonAVR_dep']
).partial_dependency(compile_args: true, includes: true)

add_project_arguments(
	cxx.get_supported_arguments('-Wno-misspelled-isr'),
	language: 'cpp'
)

platformSrc = files(
	#'startup.cxx', 'platform.cxx'
)
