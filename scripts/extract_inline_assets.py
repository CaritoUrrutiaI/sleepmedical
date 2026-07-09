#!/usr/bin/env python3
"""Extrae bloques <style>/<script> con id= que WordPress repite, byte a byte,
en varias paginas HTML del mirror, y los reemplaza por un <link>/<script src>
compartido en wp-content/generated/{css,js}/.

Pensado para volver a correrse despues de un futuro `wget --mirror` (ver
README.md "Origen"): solo toca bloques cuyo contenido es identico entre
paginas, en el mismo lugar del documento (preserva orden de cascada/ejecucion),
y nunca modifica el resultado renderizado.

Que NO se extrae, a proposito:
  - Bloques <style>/<script> sin atributo id (CSS por-widget de Pagelayer,
    JSON-LD por pagina, etc.): son legitimamente distintos por pagina.
  - <script type="application/json"> / type="importmap">: un `src` externo
    no se llega a cargar para esos tipos segun el spec de HTML, asi que
    externalizarlos rompe silenciosamente el contenido.
  - <script type="module">: semantica de carga distinta (defer implicito);
    no vale el riesgo para el ahorro que da.
  - Cualquier id cuyo contenido varia entre paginas (nonces, IDs de
    producto, stats de Jetpack, etc.) simplemente no forma un grupo
    duplicado y se deja donde esta.

Uso:
    python3 scripts/extract_inline_assets.py [--clean] [--dry-run]

  --clean     borra wp-content/generated/{css,js} antes de regenerar, para
              no dejar archivos huerfanos de una corrida anterior.
  --dry-run   solo reporta que haria, no escribe nada.
"""
import argparse
import glob
import hashlib
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS_OUT_DIR = "wp-content/generated/css"
JS_OUT_DIR = "wp-content/generated/js"

STYLE_TAG_RE = re.compile(
    r'<style id="([a-zA-Z0-9_@:.\/-]+)"([^>]*)>(.*?)</style>', re.DOTALL
)
SCRIPT_TAG_RE = re.compile(
    r'<script id="([a-zA-Z0-9_@:.\/-]+)"([^>]*)>(.*?)</script>', re.DOTALL
)

# type= values for <script> that are safe to externalize via src=. Anything
# else (application/json, importmap, module, ld+json, ...) is left inline.
SAFE_SCRIPT_TYPES = {None, "", "text/javascript", "application/javascript"}


def list_html_files():
    files = [f for f in glob.glob("**/*.html", recursive=True) if "@p=" not in f]
    files += [f for f in glob.glob("*.html") if "@p=" in f]
    return sorted(set(files))


def extract_type_attr(attrs):
    m = re.search(r'type=["\']([^"\']*)["\']', attrs)
    return m.group(1) if m else None


def collect_variants(files, tag_re, is_script):
    """id -> {content_hash: body}, only for ids present in >=2 files with
    identical content (singleton/unique-per-page content is left alone)."""
    raw = {}  # id -> hash -> body
    occurrence_count = {}  # (id, hash) -> count
    for f in files:
        content = open(f, encoding="utf-8", errors="ignore").read()
        for m in tag_re.finditer(content):
            tag_id, attrs, body = m.group(1), m.group(2), m.group(3)
            if is_script:
                if extract_type_attr(attrs) not in SAFE_SCRIPT_TYPES:
                    continue
                if not body.strip():
                    continue
            h = hashlib.md5(body.encode()).hexdigest()
            raw.setdefault(tag_id, {}).setdefault(h, body)
            occurrence_count[(tag_id, h)] = occurrence_count.get((tag_id, h), 0) + 1

    variants = {}
    for tag_id, hmap in raw.items():
        dup_hashes = {h: b for h, b in hmap.items() if occurrence_count[(tag_id, h)] >= 2}
        if dup_hashes:
            variants[tag_id] = dup_hashes
    return variants


def assign_filenames(variants, ext):
    hash_to_filename = {}
    for tag_id, hmap in variants.items():
        hashes = sorted(hmap.keys())
        for i, h in enumerate(hashes):
            suffix = "" if i == 0 else f"--v{i + 1}"
            hash_to_filename[(tag_id, h)] = f"{tag_id}{suffix}.{ext}"
    return hash_to_filename


def rewrite_files(files, tag_re, hash_to_filename, out_dir, is_script, dry_run):
    files_changed = 0
    total_replacements = 0
    for f in files:
        content = open(f, encoding="utf-8", errors="ignore").read()
        original = content
        file_dir = os.path.dirname(f) or "."
        rel_root = os.path.relpath(out_dir, start=file_dir).replace(os.sep, "/")

        def replace(m):
            nonlocal total_replacements
            tag_id, attrs, body = m.group(1), m.group(2), m.group(3)
            if is_script and extract_type_attr(attrs) not in SAFE_SCRIPT_TYPES:
                return m.group(0)
            h = hashlib.md5(body.encode()).hexdigest()
            fname = hash_to_filename.get((tag_id, h))
            if fname is None:
                return m.group(0)  # not a duplicate, leave inline
            total_replacements += 1
            path = f"{rel_root}/{fname}"
            if is_script:
                return f"<script id='{tag_id}' src='{path}'></script>"
            return f"<link rel='stylesheet' id='{tag_id}' href='{path}' media='all' />"

        content = tag_re.sub(replace, content)
        if content != original:
            files_changed += 1
            if not dry_run:
                with open(f, "w", encoding="utf-8") as out:
                    out.write(content)
    return files_changed, total_replacements


def write_assets(hash_to_filename, variants, out_dir, dry_run):
    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
    for (tag_id, h), fname in sorted(hash_to_filename.items(), key=lambda kv: kv[1]):
        path = os.path.join(out_dir, fname)
        if not dry_run:
            with open(path, "w", encoding="utf-8") as out:
                out.write(variants[tag_id][h])
        print(f"  {os.path.relpath(path, ROOT)}  ({len(variants[tag_id][h])} B)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clean", action="store_true", help="borra wp-content/generated/{css,js} antes de regenerar")
    parser.add_argument("--dry-run", action="store_true", help="no escribe nada, solo reporta")
    args = parser.parse_args()

    os.chdir(ROOT)

    if args.clean and not args.dry_run:
        for d in (CSS_OUT_DIR, JS_OUT_DIR):
            if os.path.isdir(d):
                shutil.rmtree(d)

    files = list_html_files()
    print(f"{len(files)} paginas HTML encontradas\n")

    print("== CSS ==")
    css_variants = collect_variants(files, STYLE_TAG_RE, is_script=False)
    css_map = assign_filenames(css_variants, "css")
    write_assets(css_map, css_variants, CSS_OUT_DIR, args.dry_run)
    css_changed, css_replacements = rewrite_files(files, STYLE_TAG_RE, css_map, CSS_OUT_DIR, False, args.dry_run)
    print(f"  -> {css_replacements} bloques <style> extraidos en {css_changed} paginas\n")

    print("== JS ==")
    js_variants = collect_variants(files, SCRIPT_TAG_RE, is_script=True)
    js_map = assign_filenames(js_variants, "js")
    write_assets(js_map, js_variants, JS_OUT_DIR, args.dry_run)
    js_changed, js_replacements = rewrite_files(files, SCRIPT_TAG_RE, js_map, JS_OUT_DIR, True, args.dry_run)
    print(f"  -> {js_replacements} bloques <script> extraidos en {js_changed} paginas")

    if args.dry_run:
        print("\n(dry-run: no se escribio nada)")


if __name__ == "__main__":
    main()
