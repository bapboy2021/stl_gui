"""Compile every .ui under qt_designer/ into the mirrored app/<group>/generated/ tree.

qt_designer/panels/tools_panel.ui -> app/panels/generated/tools_panel_ui.py
qt_designer/dialogs/db_settings.ui -> app/dialogs/generated/db_settings_ui.py

Usage: python tools/build_ui.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "qt_designer"
DST = ROOT / "app"


def compile_one(ui_path: Path) -> Path:
    group = ui_path.relative_to(SRC).parts[0]        # "panels" | "dialogs"
    out_dir = DST / group / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "__init__.py").touch(exist_ok=True)
    out_path = out_dir / f"{ui_path.stem}_ui.py"
    subprocess.run(
        [sys.executable, "-m", "PyQt6.uic.pyuic", "-x", str(ui_path), "-o", str(out_path)],
        check=True,
    )
    return out_path


def main() -> int:
    ui_files = sorted(SRC.rglob("*.ui"))
    if not ui_files:
        print(f"no .ui files under {SRC}")
        return 0
    for ui in ui_files:
        out = compile_one(ui)
        print(f"{ui.relative_to(ROOT)} -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
