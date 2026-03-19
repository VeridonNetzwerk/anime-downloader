# Installation

## Prerequisites

- Python 3.10+ installed (3.13.x recommended)
- Internet connection
- Permissions to install packages on your system

## Supported Operating Systems

| OS | Supported | Notes |
|----|-----------|-------|
| Windows 10/11 | Yes | Option 4 installs/repairs Node.js and FFmpeg automatically |
| Linux | Yes | Option 4 installs dependencies via apt, dnf, or pacman |
| macOS | Yes | Option 4 installs dependencies via Homebrew |

## Tested Configurations

| OS | Version | Architecture | Python | Status | Notes |
|----|---------|--------------|--------|--------|-------|
| Windows | 10 (22H2) | x64 | 3.13.x | ✅ Working | Tested on fresh VM; FFmpeg portable fallback active |
| Windows | 11 (24H2) | x64 | 3.13.x | ✅ Working | Tested on development machine |
| Linux | Ubuntu 22.04 LTS | x64 | 3.10+ | ⚠️ Untested | Expected to work; apt install path implemented |
| Linux | Fedora 39+ | x64 | 3.10+ | ⚠️ Untested | Expected to work; dnf install path implemented |
| Linux | Arch Linux | x64 | 3.10+ | ⚠️ Untested | Expected to work; pacman install path implemented |
| macOS | 13 Ventura+ | x64 / ARM | 3.10+ | ⚠️ Untested | Expected to work; Homebrew install path implemented |

> **Legend:** ✅ Confirmed working — ⚠️ Implemented but not yet tested on real hardware

## Launcher

Start the project with:

```bash
python start-anime-downloader.py
```

The launcher menu options are:

- `1` AniWorld only
- `2` AniWatch only
- `3` Start both
- `4` Install/Repair all dependencies
- `5` Exit

## Dependencies

Option `4` installs or repairs dependencies based on your operating system.

| Component | Version | Purpose | Auto-installed |
|-----------|---------|---------|----------------|
| Node.js | 24.x (LTS) | AniWatch API & download server | ✓ |
| npm | 11+ | Package manager for Node.js | ✓ |
| Python | 3.13.x (recommended) | AniWorld downloader runtime | ✓ |
| pip | Latest (in venv) | Python package manager | ✓ |
| ffmpeg | Latest | Video processing | ✓ |

## What Option 4 Does Per OS

### Windows

- Installs/repairs Node.js (winget, then MSI fallback)
- Installs/repairs FFmpeg for native video downloading
- Rebuilds Python venv for AniWorld (prefers Python 3.13)
- Runs npm install/build recovery for aniwatch-api

### Linux

- Installs/repairs dependencies via apt, dnf, or pacman
- Rebuilds Python venv for AniWorld
- Runs npm install/build recovery for aniwatch-api

### macOS

- Installs/repairs dependencies via Homebrew
- Rebuilds Python venv for AniWorld
- Runs npm install/build recovery for aniwatch-api

## First Setup (Recommended)

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://i.ibb.co/x8gq7N3R/grafik.png)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://i.ibb.co/QF9HDfd2/grafik.png)
3. Extract the archive.
4. Run `python start-anime-downloader.py`.
5. Select option `4` (`Install/Repair`).
6. After setup, start option `1`, `2`, or `3`.

## Notes About Python

AniWorld on Windows depends on curses compatibility behavior that is currently safer with Python 3.13.
The launcher prefers Python 3.13 and can recreate incompatible virtual environments automatically.
