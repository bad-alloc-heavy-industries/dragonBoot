# SPDX-License-Identifier: BSD-3-Clause
platform = subproject(
	'dragonTI',
	required: true,
	version: '>=0.0.1',
).get_variable(
	'dragonTI_dep'
).partial_dependency(
	compile_args: true,
	includes: true
)

platformSrc = files(
	'startup.cxx', 'platform.cxx', '../aarch32/irqs.cxx'
)
