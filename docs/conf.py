# SPDX-License-Identifier: BSD-3-Clause
from datetime import date
from sys import path
from pathlib import Path

project = 'dragonBoot'
copyright = f'2022-{date.today().year}, Rachel Mant'
language  = 'en'

path.insert(0, str(Path('../gateware').resolve()))

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.intersphinx',
	'sphinx.ext.todo',
	'sphinx.ext.githubpages',
	'sphinx.ext.graphviz',
	'sphinx.ext.napoleon',
	'sphinxcontrib.platformpicker',
	'sphinx_rtd_theme',
	'sphinx_construct',
	'myst_parser',
]

source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

intersphinx_mapping = {
	'python': ('https://docs.python.org/3', None),
	'luna': ('https://luna.readthedocs.io/en/latest', None),
	'amaranth': ('https://amaranth-lang.org/docs/amaranth/latest', None),
	'construct': ('https://construct.readthedocs.io/en/latest', None),
}

autodoc_member_order = 'bysource'
autoclass_content = 'both'
autodoc_default_options = {
	'undoc-members': True
}

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
html_copy_source = False

myst_heading_anchors = 2

pygments_style = 'one-dark'

napoleon_use_ivar = True
