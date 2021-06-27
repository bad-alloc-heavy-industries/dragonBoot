# SPDX-License-Identifier: BSD-3-Clause
platform = dependency(
	'dragonTI',
	required: true,
	version: '>=0.0.1',
	fallback: ['dragonTI', 'dragonTI_dep']
).partial_dependency(compile_args: true, includes: true)

platformSrc = files(
	'startup.cxx'
)
