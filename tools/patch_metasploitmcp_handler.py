#!/usr/bin/env python3
"""Targeted, reversible compatibility patch for Kali's GH05TCREW MetasploitMCP.

Usage:
 sudo python3 tools/patch_metasploitmcp_handler.py --check
 sudo python3 tools/patch_metasploitmcp_handler.py --apply
 sudo python3 tools/patch_metasploitmcp_handler.py --restore /path/to/backup
"""
import argparse
import ast
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

DEFAULT = Path("/usr/share/metasploitmcp/MetasploitMCP.py")
OLD = "payload_obj_to_pass = payload_obj # Pass the configured payload object"
NEW = """# H4X COMPAT: handler only; pass a payload *name*, not a PayloadModule.
                 # pymetasploit3 otherwise merges implicit non-scalar defaults
                 # (e.g. AutoLoadExtensions) into the Metasploit RPC options.
                 if full_module_path == 'exploit/multi/handler':
                     invalid = [k for k, v in payload_options.items()
                                if v is not None and not isinstance(v, (str, int, float, bool))]
                     if invalid:
                         raise ValueError(f'Non-scalar handler options: {invalid}')
                     unrepresented = [k for k in payload_options if k not in module_options]
                     if unrepresented:
                         raise ValueError(f'Handler options missing from module config: {unrepresented}')
                     conflicts = [k for k, v in payload_options.items()
                                  if k in module_options and module_options[k] != v]
                     if conflicts:
                         raise ValueError(f'Conflicting handler options: {conflicts}')
                     payload_obj_to_pass = payload_name
                 else:
                     payload_obj_to_pass = payload_obj # Existing behavior for other exploits"""


def patch_source(source: str) -> tuple[str, str]:
    if "# H4X COMPAT: handler only" in source:
        return source, "already-patched"
    if source.count(OLD) != 1:
        raise ValueError("Source signature absent or ambiguous: refusing to patch")
    patched = source.replace(OLD, NEW)
    ast.parse(patched)
    return patched, "patch-ready"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--apply", action="store_true")
    actions.add_argument("--restore", type=Path)
    parser.add_argument("--target", type=Path, default=DEFAULT)
    args = parser.parse_args()
    target = args.target.resolve()
    if not target.is_file():
        parser.error(f"File not found: {target}")
    if args.restore:
        backup = args.restore.resolve()
        if not backup.is_file() or not backup.name.startswith(target.name + ".bak-"):
            parser.error("Invalid backup filename")
        data = backup.read_text(encoding="utf-8")
        ast.parse(data)
        shutil.copy2(backup, target)
        print(f"Restored {target} from {backup}")
        return 0
    original = target.read_text(encoding="utf-8")
    updated, status = patch_source(original)
    print(f"{target}: {status}")
    if args.check or status == "already-patched":
        return 0
    backup = target.with_name(target.name + ".bak-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if backup.exists():
        parser.error("Backup collision; retry later")
    shutil.copy2(target, backup)
    try:
        target.write_text(updated, encoding="utf-8")
        os.chmod(target, stat.S_IMODE(backup.stat().st_mode))
        ast.parse(target.read_text(encoding="utf-8"))
    except Exception:
        shutil.copy2(backup, target)
        raise
    print(f"Patch applied. Backup: {backup}")
    print("Restart H4X and validate with your authorized lab.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
