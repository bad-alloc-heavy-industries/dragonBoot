# SPDX-License-Identifier: BSD-3-Clause
platform = subproject(
	'dragonSTM32',
	required: true,
	version: '>=0.0.1',
).get_variable(
	'dragonSTM32_dep'
).partial_dependency(
	compile_args: true,
	includes: true
)

platformSrc = files(
	'startup.cxx', 'platform.cxx', '../aarch32/irqs.cxx'
)
