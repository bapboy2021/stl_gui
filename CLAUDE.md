# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A PyQt desktop application for STL (3D model) manipulation — specifically rotation and translation transformations. Currently in early development: UI is designed, `main.py` is empty.

## Environment Setup

```bash
source venv/bin/activate          # activate Python 3.13 venv
pip install -r requirements.txt   # once requirements.txt exists
```

## Running the App

```bash
python main.py
```

## UI Files

Qt Designer `.ui` sources live in `qt_designer/` and compile into `app/<group>/generated/<name>_ui.py`. Regenerate after editing a `.ui`:

```bash
python tools/build_ui.py
```

The build script walks `qt_designer/` recursively and mirrors the tree under `app/*/generated/`. Generated files are tracked in git so clones run without a build step.

## Architecture

### UI layout
Three roles per UI element:
1. `qt_designer/<group>/<name>.ui` — design source, edited in Qt Designer
2. `app/<group>/generated/<name>_ui.py` — auto-generated `Ui_<Name>` class; never hand-edit
3. `app/<group>/<name>.py` — hand-written logic class using composition: `self.ui = Ui_<Name>(); self.ui.setupUi(self)`

Current groups: `panels/` (tools, scene, properties) and `dialogs/` (db_settings).

- **Main window** (`app/main_window.py`) — hand-coded `QMainWindow` with dockable panels; no `.ui` file.
- **`db_settings.ui`** — Network/credentials dialog: IP, port, Test Connection button, and Sign In flow

### Expected Code Layout (not yet implemented)
- `main.py` — entry point; instantiate QApplication and main window
- Business logic for rotation/translation math (likely numpy-based)
- Network logic for the settings dialog (IP/port connectivity check, auth)

### Key Design Note
The UI separates input representation from output representation — a user can input a rotation as Euler angles and output as a rotation matrix (or quaternion). The conversion math is the core of the application.
