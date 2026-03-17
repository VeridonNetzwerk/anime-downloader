# Installation

## Prerequisites

- Windows 10 or 11
- Internet connection
- Permission to install software

## Runtime Versions

- Node.js: LTS, tested with 24.x
- Python: 3.13.x recommended
- WSL: Ubuntu distro recommended

## First Setup (Recommended)

1. Run `start-aniwatch.bat`.
2. Select option `4` (`Install/Repair`).
3. Wait until progress reaches 100%.
4. Return to menu and launch option `1`, `2`, or `3`.

## What Option 4 Installs/Repairs

- Node.js and npm
- WSL + Ubuntu
- Python venv in `.venv`
- AniWorld Python package (pinned)
- aniwatch-api dependencies and build artifacts

## Notes About Python

AniWorld on Windows depends on curses compatibility behavior that is currently safer with Python 3.13.
The launcher prefers Python 3.13 and can recreate incompatible virtual environments automatically.
