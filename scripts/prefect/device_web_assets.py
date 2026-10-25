#!/usr/bin/env python3
"""Repair the cached DeviceWeb stamp and verify generated/installed runtime assets.

CMake caches device_page.stamp in the build tree, but writes the bundle into the
source tree. A fresh checkout therefore needs its bundle rebuilt even when the
cached stamp is newer than every input. Never delete native objects or source.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


PAGE = Path("src/slic3r/GUI/DeviceWeb/device_page")
RESOURCE = Path("resources/web/device_page/dist")
STAMP = Path("src/slic3r/GUI/DeviceWeb/device_page.stamp")


class AssetError(ValueError):
    pass


def contained(root, path):
    """Resolve before reading/deleting, including Windows junction targets."""
    result = path.resolve()
    if not result.is_relative_to(root.resolve()):
        raise AssetError(f"Path escapes workspace: {path}")
    return result


def relative(root, value):
    value = Path(value)
    if value.is_absolute() or ".." in value.parts:
        raise AssetError(f"Expected a workspace-relative path: {value}")
    return contained(root, root / value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    if not directory.is_dir():
        raise AssetError(f"Missing bundle directory: {directory}")
    files = {}
    for path in directory.rglob("*"):
        contained(directory, path)
        if path.is_file():
            if path.stat().st_size == 0:
                raise AssetError(f"Empty bundle asset: {path}")
            files[path.relative_to(directory).as_posix()] = digest(path)
    return files


class EntryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.required = []
        self.scripts = 0
        self.styles = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.required.append(attrs["src"])
            self.scripts += 1
        if tag == "link" and set(attrs.get("rel", "").lower().split()) & {
            "stylesheet", "modulepreload", "preload", "import"
        } and attrs.get("href"):
            self.required.append(attrs["href"])
            self.styles += int("stylesheet" in attrs.get("rel", "").lower().split())
        # rel=icon is optional: upstream index.html references absent /vite.svg.


def local_reference(bundle, parent, reference):
    parsed = urlsplit(reference.strip())
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None  # external/data URLs and anchors are not bundle files
    path = unquote(parsed.path)
    if "\\" in path or "\x00" in path:
        raise AssetError(f"Invalid asset URL: {reference}")
    target = bundle / path.lstrip("/") if path.startswith("/") else parent / path
    target = contained(bundle, target)
    if not target.is_file() or target.stat().st_size == 0:
        raise AssetError(f"Missing referenced runtime asset: {target}")
    return target


def validate_bundle(bundle, public):
    files = inventory(bundle)
    if "index.html" not in files:
        raise AssetError(f"Missing runtime entry point: {bundle / 'index.html'}")
    parser = EntryParser()
    parser.feed((bundle / "index.html").read_text(encoding="utf-8-sig"))
    if not parser.scripts or not parser.styles:
        raise AssetError("DeviceWeb entry point must load JavaScript and CSS")
    for ref in parser.required:
        local_reference(bundle, bundle, ref)
    # Include CSS subresources, including nested imports. Do not require optional
    # sourceMappingURL files: these are requested only by developer tools.
    for name in files:
        if name.endswith(".css"):
            css = (bundle / name).read_text(encoding="utf-8-sig")
            css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
            refs = re.findall(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", css)
            refs += re.findall(r"@import\s+['\"]([^'\"]+)['\"]", css)
            for ref in refs:
                local_reference(bundle, (bundle / name).parent, ref)
    if not public.is_dir():
        raise AssetError(f"Missing source public assets: {public}")
    for path in public.rglob("*"):
        contained(public, path)
        if path.is_file():
            name = path.relative_to(public).as_posix()
            if files.get(name) != digest(path):
                raise AssetError(f"Missing or changed public asset: {bundle / name}")
    return files


def verify_generated(root):
    public = relative(root, PAGE / "public")
    generated = validate_bundle(relative(root, PAGE / "dist"), public)
    resources = validate_bundle(relative(root, RESOURCE), public)
    if generated != resources:
        raise AssetError("Generated DeviceWeb bundle and resource copy differ")
    return resources


def repair(root, build_directory):
    relative(root, build_directory)  # Validate without hiding internal junctions.
    stamp = root / Path(build_directory) / STAMP
    # Resolve cannot by itself distinguish an in-workspace symlink to an
    # unrelated object. Reject every reparse point before the one-file delete.
    candidate = stamp
    while candidate != root:
        if candidate.exists() or candidate.is_symlink():
            attributes = getattr(candidate.lstat(), "st_file_attributes", 0)
            if candidate.is_symlink() or attributes & 0x400:
                raise AssetError(f"Reparse point refused for stamp repair: {candidate}")
        candidate = candidate.parent
    stamp = contained(root, stamp)
    try:
        files = verify_generated(root)
        return {"stamp_removed": False, "files": len(files)}
    except AssetError as error:
        reason = str(error)
    removed = False
    if stamp.exists():
        if not stamp.is_file() or stamp.is_symlink():
            raise AssetError(f"Expected a regular DeviceWeb stamp: {stamp}")
        stamp.unlink()  # Only this resolved stamp; preserve PCH/native object cache.
        removed = True
    return {"stamp_removed": removed, "rebuild_required": True, "reason": reason}


def verify(root, install_directory=None):
    files = verify_generated(root)
    if install_directory is not None:
        installed = relative(root, Path(install_directory) / RESOURCE)
        installed_files = validate_bundle(installed, relative(root, PAGE / "public"))
        if files != installed_files:
            raise AssetError("Installed DeviceWeb bundle differs from generated resources")
    return {"verified_files": len(files), "installed": install_directory is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("repair", "verify"))
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--build-directory", default="out/prefect-app")
    parser.add_argument("--install-directory")
    args = parser.parse_args()
    root = args.workspace.resolve()
    if not root.is_dir() or root == root.parent:
        parser.error("Workspace must be an existing non-root directory")
    if args.mode == "repair" and args.install_directory:
        parser.error("repair does not accept an install directory")
    try:
        result = repair(root, args.build_directory) if args.mode == "repair" else verify(root, args.install_directory)
        print(json.dumps(result, sort_keys=True))
    except (AssetError, OSError, UnicodeError) as error:
        print(f"DeviceWeb assets: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
