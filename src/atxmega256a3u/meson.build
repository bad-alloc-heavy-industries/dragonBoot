# SPDX-License-Identifier: BSD-3-Clause
platform = dependency(
	'dragonAVR',
	required: true,
	version: '>=0.0.1',
	fallback: ['dragonAVR', 'dragonAVR_dep']
).partial_dependency(compile_args: true, includes: true)

platformSrc = files(
	#'startup.cxx', 'platform.cxx'
)
