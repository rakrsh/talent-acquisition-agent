import os
import sys

import tomllib

sys.path.insert(0, os.path.abspath("../../services/api"))
sys.path.insert(0, os.path.abspath("../../services/search"))
sys.path.insert(0, os.path.abspath("../../src"))

# Read version from pyproject.toml
_pyproject_path = os.path.abspath("../../pyproject.toml")
with open(_pyproject_path, "rb") as _f:
    _pyproject = tomllib.load(_f)

_raw_version = _pyproject["project"]["version"]  # e.g. "0.1.0" or "0.1.dev0"

# Derive a short version slug for the docs folder:
#   "0.1.dev0" -> "dev"
#   "0.1.0"    -> "0.1"
#   "1.2.3"    -> "1.2"
if "dev" in _raw_version:
    version_slug = "dev"
else:
    _parts = _raw_version.split(".")
    version_slug = ".".join(_parts[:2])  # major.minor only

# Configuration file for Sphinx documentation
project = "Job Agent"
copyright = "2026, Job Agent"
author = "Job Agent"
release = _raw_version
version = version_slug

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinxcontrib.httpdomain",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = {}
