import os
import sys

sys.path.insert(0, os.path.abspath('.'))

# Project information
project = 'website RTD'
author = 'David TBO'
release = '0.1'

# Sphinx extensions
extensions = [
    'nbsphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Paths to the templates and files to exclude
templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']

# HTML
html_theme = 'sphinx_rtd_theme'

# nbsphinx configuration
nbsphinx_execute = 'never'
nbsphinx_allow_errors = True

# Markdown supports and Notebooks
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
