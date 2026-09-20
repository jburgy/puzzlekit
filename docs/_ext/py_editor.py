"""A ``py-editor`` directive: PyScript's editable, runnable Python block.

PyScript ships the widget (CodeMirror editor, Run button, output pane) and the Pyodide
plumbing, so all this does is emit the tag and tell PyScript where to find puzzlekit.

The package source is copied into ``_static`` at build time and mapped into the
interpreter's filesystem by the ``files`` config, so the docs always demonstrate the
working tree rather than a published wheel.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

PYSCRIPT_VERSION = "2026.7.1"
CDN = f"https://pyscript.net/releases/{PYSCRIPT_VERSION}"
STATIC_SUBDIR = "pyscript"
ENV = "puzzlekit"

_ASSETS = f'<script type="module" src="{CDN}/core.js"></script>\n'


class PyEditorDirective(SphinxDirective):
    has_content = True

    def run(self) -> list[nodes.Node]:
        markup = ""
        config = None
        if not self.env.temp_data.get("pyscript_bootstrapped"):
            self.env.temp_data["pyscript_bootstrapped"] = True
            markup += _ASSETS
            config = html.escape(json.dumps(self._config()), quote=True)
        markup += _editor("\n".join(self.content), config=config)
        return [nodes.raw("", markup, format="html")]

    def _config(self) -> dict[str, Any]:
        """Map each module into the interpreter's working directory, which is on sys.path.

        Source URLs are relative to the *page*, so nested documents need the right number
        of ``../`` segments.
        """
        up = "../" * self.env.docname.count("/")
        modules = self.env.pyscript_modules  # type: ignore[attr-defined]
        return {"files": {f"{up}_static/{STATIC_SUBDIR}/{name}": f"./{name}" for name in modules}}


def _editor(code: str, *, config: str | None = None) -> str:
    """PyScript rejects a repeated config for one env, so only the first editor carries it."""
    if "</script" in code:
        raise ValueError("a py-editor body cannot contain '</script'")
    attrs = f" config='{config}'" if config else ""
    # The body is raw text: entities are not decoded inside <script>, so it must not be escaped.
    return f'<script type="py-editor" env="{ENV}"{attrs}>\n{code}\n</script>\n'


def _stage_sources(app: Sphinx) -> None:
    root = Path(app.srcdir).parent / "src"
    target = Path(app.srcdir) / "_static" / STATIC_SUBDIR
    shutil.rmtree(target, ignore_errors=True)
    names = []
    for path in sorted(root.rglob("*.py")):
        name = path.relative_to(root).as_posix()
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        names.append(name)
    app.env.pyscript_modules = names  # type: ignore[attr-defined]


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_directive("py-editor", PyEditorDirective)
    app.connect("builder-inited", _stage_sources)
    # Order matters: our overrides have the same specificity as core.css, so they lose
    # unless they come second. The module script stays in the body, loaded only on pages
    # that actually have an editor.
    app.add_css_file(f"{CDN}/core.css")
    app.add_css_file("py-editor.css")
    return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
