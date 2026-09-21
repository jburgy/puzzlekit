from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
from pathlib import Path

ARTIFACT_SUFFIXES = (".whl", ".tar.gz", ".zip")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_distribution_artifact(path: Path) -> bool:
    return path.is_file() and any(path.name.endswith(suffix) for suffix in ARTIFACT_SUFFIXES)


def render_index(title: str, links: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'    <li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>'
        for label, href in links
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "  <head>\n"
        f'    <meta charset="utf-8">\n    <title>{html.escape(title)}</title>\n'
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{html.escape(title)}</h1>\n"
        "    <ul>\n"
        f"{items}\n"
        "    </ul>\n"
        "  </body>\n"
        "</html>\n"
    )


def build_index(dist_dir: Path, docs_dir: Path, package_name: str) -> None:
    normalized = normalize(package_name)
    package_dist_dir = docs_dir / "packages" / normalized
    package_simple_dir = docs_dir / "simple" / normalized
    package_dist_dir.mkdir(parents=True, exist_ok=True)
    package_simple_dir.mkdir(parents=True, exist_ok=True)

    for artifact in sorted(dist_dir.iterdir()):
        if is_distribution_artifact(artifact):
            shutil.copy2(artifact, package_dist_dir / artifact.name)

    package_links: list[tuple[str, str]] = []
    for artifact in sorted(package_dist_dir.iterdir()):
        if is_distribution_artifact(artifact):
            href = f"../../packages/{normalized}/{artifact.name}#sha256={sha256(artifact)}"
            package_links.append((artifact.name, href))

    (package_simple_dir / "index.html").write_text(
        render_index(f"Links for {package_name}", package_links),
        encoding="utf-8",
    )

    packages_root = docs_dir / "packages"
    root_links = []
    for child in sorted(packages_root.iterdir()):
        if child.is_dir():
            root_links.append((child.name, f"./{child.name}/"))

    simple_root = docs_dir / "simple"
    simple_root.mkdir(parents=True, exist_ok=True)
    (simple_root / "index.html").write_text(
        render_index("Simple package index", root_links),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--package-name", required=True)
    args = parser.parse_args()

    build_index(args.dist_dir, args.docs_dir, args.package_name)


if __name__ == "__main__":
    main()
