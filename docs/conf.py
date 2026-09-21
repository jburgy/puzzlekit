import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_ext"))

project = "puzzlekit"
author = "Jan Burgy"
copyright = "2026, Jan Burgy"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "py_editor",
]

myst_enable_extensions = ["colon_fence", "deflist"]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "furo"
html_static_path = ["_static"]
html_extra_path = [
    "_extra",
    "simple",
    "packages",
]  # package index directories and llms.txt must land at the site root
html_title = "puzzlekit"
html_baseurl = "https://bur.gy/puzzlekit/"

autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
}

nitpicky = False
