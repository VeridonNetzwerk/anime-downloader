# Installation

---

## Prerequisites

- Python 3.10+ installed (3.13.x recommended)
- Internet connection
- Permissions to install packages on your system

---

## Supported Operating Systems

| OS          | Version           | Architecture      | Python       | Status           | Release      |
| ----------- | ----------------- | ----------------- | ------------ | ---------------- | ------------ |
| Windows     | 11 (24H2)         | x64 / ARM64       | 3.13.x       | ✅ Working       | v1.3         |
| Windows     | 10 (22H2)         | x86 / x64 / ARM64 | 3.13.x       | ✅ Working       | v1.3         |
| Windows     | 8.1               | x86 / x64         | ≤3.10        | ❌ Not Supported | -            |
| Windows     | 8                 | x86 / x64         | ≤3.9         | ❌ Not Supported | -            |
| Windows     | 7 (SP1)           | x86 / x64         | ≤3.8         | ❌ Not Supported | -            |
| Windows     | XP (SP3)          | x86               | ≤3.4         | ❌ Not Working   | -            |
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
| ChromeOS    | ChromeOS          | x86 / x64 / ARM   | ?            | ❌ Not Working   | -            |
| FydeOS      | Latest            | x86 / x64 / ARM   | ?            | ❌ Not Working   | -            |
| ReactOS     | 0.4.15            | x86               | 3.4–3.8      | ❌ Not Supported | -            |
| Haiku       | R1 Beta 4         | x64               | 3.10         | ❌ Not Supported | -            |
| FreeBSD     | 13 / 14           | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |
| OpenBSD     | 7.x               | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |

> **Legend:** ✅ Confirmed working — ⚠️ Implemented but not tested - ❌ Not Implemented

---

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

---

## Dependencies

Option `4` installs or repairs dependencies based on your operating system.

| Component | Version | Purpose | Auto-installed |
|-----------|---------|---------|----------------|
| Node.js | 24.x (LTS) | AniWatch API & download server | ✓ |
| npm | 11+ | Package manager for Node.js | ✓ |
| Python | 3.13.x (recommended) | AniWorld downloader runtime | ✓ |
| pip | Latest (in venv) | Python package manager | ✓ |
| ffmpeg | Latest | Video processing | ✓ |

---

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

---

## First Setup (Recommended)

### Windows 10

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://i.ibb.co/x8gq7N3R/grafik.png)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://i.ibb.co/QF9HDfd2/grafik.png)
3. Extract the archive.
![Extract All...](https://i.ibb.co/5hfCjVn4/3.png)
4. Click Extract.
![Click Extract](https://i.ibb.co/3mGN0Wcb/4.png)
5. Open the Extracted Archive.
![Open Folder](https://i.ibb.co/60zh5PRP/5.png)
6. Click on the address bar at the top and copy the path.
![Copy Path](https://i.ibb.co/9C36TRF/6.png)
7. Press the Windows-Key or use the search bar, type Microsoft Store and open it.
![Open MS Store](https://i.ibb.co/DfGRzYVD/7.png)
8. Search for Python 3.13 and click on it.
![Search Python](https://i.ibb.co/2J6XnDv/8.png)
9. Press Get in order to install Python 3.13.
![Install Python](https://i.ibb.co/n8YtnHtY/9.png)
10. After installing Python, press the Windows key or use the search bar, type cmd, and open it.
![Open cmd](https://i.ibb.co/JR67vwj1/10.png)
11. In the command prompt, type: cd (the path copied earlier)
![cd into downloader](https://i.ibb.co/rKW8kjW9/11.png)
12. Run `py start-anime-downloader.py` or `python start-anime-downloader.py` (sometimes it's `py`, sometimes `python`, or sometimes both work).
![py](https://i.ibb.co/GQY1hSCh/12.png)
![python](https://i.ibb.co/8n6YMFdQ/12-2.png)
13. A menu should open. On the first run, select option 4 to install all dependencies.
![Option 4](https://i.ibb.co/4ns8wGjD/13.png)
14. Once done, the downloader is successfully installed.
![Done](https://i.ibb.co/5XgpGvBC/14.png)

> ⚠️ **Note:** If you run into an error, feel free to open an issue.

### Windows 11

The setup on Windows 11 is identical to Windows 10. Follow the same steps as above.

---

## Notes About Python

AniWorld on Windows depends on curses compatibility behavior that is currently safer with Python 3.13.
The launcher prefers Python 3.13 and can recreate incompatible virtual environments automatically.
