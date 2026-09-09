"""Refuse regeneration if existing outputs differ from the last recorded generation."""
from pathlib import Path
import hashlib
import json

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def manifest(root, name):
    return root / 'reference' / (name + '-generated-sha256.json')

def preflight(root, name, paths):
    saved = manifest(root, name)
    known = json.loads(saved.read_text()) if saved.exists() else {}
    changed = [str(p.relative_to(root)) for p in paths
               if p.exists() and known.get(str(p.relative_to(root))) != digest(p)]
    if changed:
        raise RuntimeError('Refusing to overwrite manual or unregistered edits: ' + ', '.join(changed)
                           + '. Reconcile in a separate scratch copy; see README regeneration workflow.')

def record(root, name, paths):
    saved = manifest(root, name)
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_text(json.dumps({str(p.relative_to(root)): digest(p) for p in paths}, indent=2) + '\n')
