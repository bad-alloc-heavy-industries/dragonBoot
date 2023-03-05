# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict, List, Union, Tuple
from arachne.util import *
from torii.sim import Simulator

__all__ = (
	'sim_case',
	'run_sims',
)

def _collect_sims(*, pkg) -> List[Dict[str, Union[str, Tuple[Simulator, str]]]]:
	from pkgutil   import walk_packages
	from importlib import import_module
	from inspect   import getmembers
	from os        import path

	def _case_predicate(member):
		return (
			isinstance(member, tuple) and
			len(member) == 2 and
			isinstance(member[0], Simulator) and
			isinstance(member[1], str)
		)

	sims = []

	if not path.exists(pkg):
		raise RuntimeError(f'The package {pkg} does not exist, unable to attempt to import test cases')

	for _, name, is_pkg in walk_packages(path = (pkg,), prefix = f'{pkg.replace("/", ".")}.'):
		pkg_import = import_module(name)
		cases_variables = getmembers(pkg_import, _case_predicate)
		if len(cases_variables) != 0:
			sims.append({
				'name' : name,
				'cases': [case for _, case in cases_variables]
			})

	return sims


def sim_case(*, domains, dut, platform = None, engine = 'pysim'):
	def _reg_sim(func):
		from torii.hdl.ir import Fragment

		sim = Simulator(
			Fragment.get(dut, platform = platform),
			engine = engine
		)

		for dom, clk in domains:
			sim.add_clock(1 / clk, domain = dom)

		for case, dom in func(sim, dut):
			sim.add_sync_process(case, domain = dom)

		return (sim, getattr(func, '__name__'))
	return _reg_sim

def run_sims(*, pkg, result_dir, skip = []):
	from os import path, mkdir, makedirs

	if not path.exists(result_dir):
		mkdir(result_dir)

	for sim in _collect_sims(pkg = pkg):
		log(f'Running simulation {sim["name"]}...')

		out_dir = path.join(result_dir, sim['name'].replace('.', '/'))
		if not path.exists(out_dir):
			makedirs(out_dir, exist_ok = True)

		for case, name in sim['cases']:
			inf(f' => Running {name}')

			with case.write_vcd(path.join(out_dir, f'{name}.vcd')):
				case.reset()
				case.run()
