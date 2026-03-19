# Installation

## Prerequisites

- Python 3.10+ installed (3.13.x recommended)
- Internet connection
- Permissions to install packages on your system

## Supported Operating Systems

| OS          | Version           | Architecture      | Python       | Status           | Release      |
| ----------- | ----------------- | ----------------- | ------------ | ---------------- | ------------ |
| Windows     | 11 (24H2)         | x64 / ARM64       | 3.13.x       | ✅ Working       | v1.2.1       |
| Windows     | 10 (22H2)         | x86 / x64 / ARM64 | 3.13.x       | ✅ Working       | v1.2.1       |
| Windows     | 8.1               | x86 / x64         | ≤3.10        | ❌ Not Supported | -            |
| Windows     | 8                 | x86 / x64         | ≤3.9         | ❌ Not Supported | -            |
| Windows     | 7 (SP1)           | x86 / x64         | ≤3.8         | ❌ Not Supported | -            |
| Windows     | XP (SP3)          | x86               | ≤3.4         | ❌ Not Supported | -            |
| Ubuntu      | 22.04 LTS         | x64 / ARM64       | 3.10+        | ⚠️ Untested      | -            |
| Ubuntu      | 24.04 LTS         | x64 / ARM64       | 3.12+        | ⚠️ Untested      | -            |
| Debian      | 11 (Bullseye)     | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| Debian      | 12 (Bookworm)     | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| Debian      | 13 (Trixie)       | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| Fedora      | 39+               | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| Arch Linux  | 2025.01.01+       | x64               | 3.12+        | ⚠️ Untested      | -            |
| Linux Mint  | 21.x              | x64               | 3.10+        | ⚠️ Untested      | -            |
| openSUSE    | Leap / Tumbleweed | x64 / ARM64       | 3.10+        | ⚠️ Untested      | -            |
| macOS       | 13 Ventura        | x64 / ARM64       | 3.10+        | ⚠️ Untested      | -            |
| macOS       | 14 Sonoma         | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| ChromeOS    | ChromeOS          | x86 / x64 / ARM   | ?            | ❌ Not Supported | -            |
| FydeOS      | Latest            | x86 / x64 / ARM   | ?            | ❌ Not Supported | -            |
| ReactOS     | 0.4.15            | x86               | 3.4–3.8      | ❌ Not Supported | -            |
| Haiku       | R1 Beta 4         | x64               | 3.10         | ❌ Not Supported | -            |
| FreeBSD     | 13 / 14           | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |
| OpenBSD     | 7.x               | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |

> **Legend:** ✅ Confirmed working — ⚠️ Implemented but not tested - ❌ Not Implemented

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

- Installs/repairs dependencies via apt, dnf, pacman, or zypper
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
