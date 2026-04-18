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

Qt Designer `.ui` files live in `qt_file/`. Compile them to Python before use:

```bash
pyuic6 -x qt_file/main_win.ui -o py_qt/main_win.py
pyuic6 -x qt_file/db_settings.ui -o py_qt/db_settings.py
```

## Architecture

### UI Structure (`qt_file/`)
- **`main_win.ui`** — Main window (920×766). Two tabs: "STL Manipulation" (active) and a placeholder Tab 2. The STL tab has two sections:
  - **Rotation**: supports quaternion, Euler angles (configurable XYZ order), and 3×3 rotation matrix; input/output in radians or degrees
  - **Translation**: X/Y/Z inputs with unit selectors; optional conversion to 4×4 homogeneous transformation matrix
- **`db_settings.ui`** — Network/credentials dialog: IP, port, Test Connection button, and Sign In flow

### Expected Code Layout (not yet implemented)
- `main.py` — entry point; instantiate QApplication and main window
- Business logic for rotation/translation math (likely numpy-based)
- Network logic for the settings dialog (IP/port connectivity check, auth)

### Key Design Note
The UI separates input representation from output representation — a user can input a rotation as Euler angles and output as a rotation matrix (or quaternion). The conversion math is the core of the application.
