#!/usr/bin/env python3
"""Sync project folders from the local portfolio directory into the site.

Run this whenever a folder is added to SOURCE_DIR. It regenerates
web-optimized images under assets/work/<slug>/ and updates work.json.
Existing title/category for a slug are preserved across reruns; only
new slugs get placeholder metadata (edit work.json to fix titles).
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path("/Users/nolaschroeder/Coding Stuff/portfolio")
SITE_DIR = Path(__file__).resolve().parent.parent
WORK_DIR = SITE_DIR / "assets" / "work"
MANIFEST = SITE_DIR / "work.json"
MANIFEST_JS = SITE_DIR / "work.js"

THUMB_LONG_EDGE = 700
FULL_LONG_EDGE = 1800
QUALITY = 82

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def natural_key(path):
    parts = re.split(r"(\d+)", path.stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_cover(folder):
    for child in folder.iterdir():
        if child.is_dir() and child.name.strip().lower() == "cover image":
            imgs = sorted(
                [f for f in child.iterdir() if f.suffix.lower() in IMAGE_EXTS],
                key=natural_key,
            )
            if imgs:
                return imgs[0]
    return None


def convert(src, dst, long_edge):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["cwebp", "-quiet", "-q", str(QUALITY), "-resize", str(long_edge), "0",
         str(src), "-o", str(dst)],
        check=True,
    )


def main():
    if not SOURCE_DIR.is_dir():
        print(f"Source folder not found: {SOURCE_DIR}", file=sys.stderr)
        sys.exit(1)

    existing = {}
    if MANIFEST.exists():
        for p in json.loads(MANIFEST.read_text()):
            existing[p["slug"]] = p

    folders = sorted(
        [d for d in SOURCE_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    manifest = []
    added, updated = [], []

    for folder in folders:
        slug = slugify(folder.name)
        direct_images = sorted(
            [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS],
            key=natural_key,
        )

        cover_file = find_cover(folder)
        if cover_file:
            cover_hash = file_hash(cover_file)
            direct_images = [f for f in direct_images if file_hash(f) != cover_hash]
            images = [cover_file] + direct_images
        else:
            images = direct_images

        if not images:
            continue

        prev = existing.get(slug, {})
        is_new = slug not in existing

        # Regenerate from scratch each run so index-based filenames (01.webp, ...)
        # never point at stale content when files are added, removed, or reordered.
        shutil.rmtree(WORK_DIR / slug, ignore_errors=True)

        image_names = []
        for i, img in enumerate(images, start=1):
            fname = f"{i:02d}.webp"
            image_names.append(fname)
            full_dst = WORK_DIR / slug / "full" / fname
            thumb_dst = WORK_DIR / slug / "thumb" / fname
            convert(img, full_dst, FULL_LONG_EDGE)
            convert(img, thumb_dst, THUMB_LONG_EDGE)

        entry = {
            "slug": slug,
            "title": prev.get("title") or folder.name.title(),
            "category": prev.get("category", ""),
            "year": prev.get("year", ""),
            "accent": prev.get("accent") or ("pink" if len(manifest) % 2 == 0 else "blue"),
            "cover": f"assets/work/{slug}/thumb/01.webp",
            "images": image_names,
        }
        manifest.append(entry)

        if is_new:
            added.append(slug)
        elif prev.get("images") != image_names:
            updated.append(slug)

    removed = set(existing) - {p["slug"] for p in manifest}

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    MANIFEST_JS.write_text(
        "window.WORK_PROJECTS = " + json.dumps(manifest, indent=2) + ";\n"
    )

    print(f"{len(manifest)} project(s) in manifest.")
    if added:
        print("  new:", ", ".join(added), "(placeholder title/category — edit work.json)")
    if updated:
        print("  updated images:", ", ".join(updated))
    if removed:
        print("  no longer present locally (left in assets, remove manually if desired):", ", ".join(removed))


if __name__ == "__main__":
    main()
