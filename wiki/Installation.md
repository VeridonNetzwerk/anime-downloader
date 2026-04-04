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
| Windows     | 11 (24H2)         | x64 / ARM64       | 3.13         | ✅ Working       | v1.3.2       |
| Windows     | 10 (22H2)         | x86 / x64 / ARM64 | 3.13         | ✅ Working       | v1.3.2       |
| Windows     | 8.1               | x86 / x64         | ≤3.10        | ⚠️ Untested      | -            |
| Windows     | 8                 | x86 / x64         | ≤3.9         | ⚠️ Untested      | -            |
| Windows     | 7 (SP1)           | x86 / x64         | ≤3.8         | ❌ Not Supported | -            |
| Windows     | XP (SP3)          | x86               | ≤3.4         | ❌ Not Supported | -            |
| Ubuntu      | 22.04 LTS         | x64 / ARM64       | 3.10.12      | ✅ Working       | v1.3.0       |
| Ubuntu      | 24.04 LTS         | x64 / ARM64       | 3.12.2       | ✅ Working       | v1.3.0       |
| Debian      | 11 (Bullseye)     | x64 / ARM64       | 3.9.2        | ✅ Working       | v1.3.0       |
| Debian      | 12 (Bookworm)     | x64 / ARM64       | 3.11.2       | ✅ Working       | v1.3.0       |
| Debian      | 13 (Trixie)       | x64 / ARM64       | 3.12.3       | ✅ Working       | v1.3.0       |
| Fedora      | 39+               | x64 / ARM64       | 3.12.0       | ✅ Working       | v1.3.0       |
| Arch Linux  | 2025.01.01+       | x64               | 3.12+        | ⚠️ Untested      | -            |
| Linux Mint  | 22                | x64               | 3.12.3       | ✅ Working       | v1.3.0       |
| openSUSE    | Leap / Tumbleweed | x64 / ARM64       | 3.10+        | ⚠️ Untested      | -            |
| macOS       | 13 Ventura        | x64 / ARM64       | 3.10+        | ⚠️ Untested      | -            |
| macOS       | 14 Sonoma         | x64 / ARM64       | 3.11+        | ⚠️ Untested      | -            |
| ChromeOS    | ChromeOS          | x86 / x64 / ARM   | ?            | ❌ Not Supported | -            |
| FydeOS      | Latest            | x86 / x64 / ARM   | ?            | ❌ Not Supported | -            |
| ReactOS     | 0.4.15            | x86               | 3.4–3.8      | ❌ Not Supported | -            |
| Haiku       | R1 Beta 4         | x64               | 3.10         | ❌ Not Supported | -            |
| FreeBSD     | 13 / 14           | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |
| OpenBSD     | 7.x               | x64 / ARM64       | 3.9+         | ❌ Not Supported | -            |

> **Legend:** 
> OS: Operating System Type
> Version: OS Version
> Architexture: Supported Architextures by the OS
> Python: The Python Version it was tested on
> Status: ✅ Confirmed working — ⚠️ Implemented but not tested - ❌ Not Implemented
> Release: The Release it was tested on

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

Option `4` installs or repairs dependencies based on your operating system and what's already installed.

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
- Downloads AniWatch API + AniWatch runtime files
- Runs npm install/build recovery for aniwatch-api
- Uses standalone dependency root: `C:\anime-downloader  dependencies`

### Linux

- Installs/repairs dependencies via apt, dnf, pacman, or zypper
- Rebuilds Python venv for AniWorld
- Downloads AniWatch API + AniWatch runtime files
- Runs npm install/build recovery for aniwatch-api
- Uses standalone dependency root: `~/.anime-downloader-dependencies` (override with `ANIME_DOWNLOADER_DEPS_DIR`)

### macOS

- Installs/repairs dependencies via Homebrew
- Rebuilds Python venv for AniWorld
- Downloads AniWatch API + AniWatch runtime files
- Runs npm install/build recovery for aniwatch-api
- Uses standalone dependency root: `~/.anime-downloader-dependencies` (override with `ANIME_DOWNLOADER_DEPS_DIR`)

---

## First Setup (Recommended)

### Windows 10

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/1.png?raw=true)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/2.png?raw=true)
3. Extract the archive.
![Extract All...](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/3.png?raw=true)
4. Click Extract.
![Click Extract](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/4.png?raw=true)
5. Open the Extracted Archive.
![Open Folder](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/5.png?raw=true)
6. Click on the address bar at the top and copy the path.
![Copy Path](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/6.png?raw=true)
7. Press the Windows-Key or use the search bar, type Microsoft Store and open it.
![Open MS Store](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/7.png?raw=true)
8. Search for Python 3.13 and click on it.
![Search Python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/8.png?raw=true)
9. Press Get in order to install Python 3.13.
![Install Python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/9.png?raw=true)
10. After installing Python, press the Windows key or use the search bar, type cmd, and open it.
![Open cmd](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/10.png?raw=true)
11. In the command prompt, type: `cd <the path copied earlier>`
![cd into downloader](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/11.png?raw=true)
12. Run `py start-anime-downloader.py` or `python start-anime-downloader.py` (sometimes it's `py`, sometimes `python`, or sometimes both work).
![py](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/12.png?raw=true)
![python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/12-2.png?raw=true)
13. A menu should open. On the first run, select option 4 to install all dependencies.
![Option 4](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/13.png?raw=true)
14. Once done, the downloader is successfully installed.
![Done](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/14.png?raw=true)

> **Note:** If you run into an error, feel free to open an issue.

### Windows 11

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/1.png?raw=true)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/2.png?raw=true)
3. Extract the archive.
![Extract All...](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/3.png?raw=true)
4. Click Extract.
![Click Extract](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/4.png?raw=true)
5. Open the Extracted Archive.
![Open Folder](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/5.png?raw=true)
6. Click on the address bar at the top and copy the path.
![Copy Path](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/6.png?raw=true)
7. Press the Windows-Key or use the search bar, type Microsoft Store and open it.
![Open MS Store](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/7.png?raw=true)
8. Search for Python 3.13 and click on it.
![Search Python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/8.png?raw=true)
9. Press Get in order to install Python 3.13.
![Install Python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/9.png?raw=true)
10. After installing Python, press the Windows key or use the search bar, type cmd, and open it.
![Open cmd](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/10.png?raw=true)
11. In the command prompt, type: `cd <the path copied earlier>`
![cd into downloader](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/11.png?raw=true)
12. Run `py start-anime-downloader.py` or `python start-anime-downloader.py` (sometimes it's `py`, sometimes `python`, or sometimes both work).
![py](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/12.png?raw=true)
![python](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/12.png?raw=true)
13. A menu should open. On the first run, select option 4 to install all dependencies.
![Option 4](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/13.png?raw=true)
14. Once done, the downloader is successfully installed.
![Done](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2011/14.png?raw=true)

### Ubuntu 22

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/1.png?raw=true)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/2.png?raw=true)
3. Extract the archive.
![Extract archive](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/3.png?raw=true)
4. Open a terminal in the extracted folder.
![Open terminal](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/4.png?raw=true)
5. Install Python and required base tools.
![Install prerequisites](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/Screenshot%202026-03-21%20162854.png?raw=true)
6. Start the launcher with `python3 start-anime-downloader.py`.
![Start launcher](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/6.png?raw=true)
7. Select option `4` (`Install/Repair`) on the first run.
![Option 4](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/7.png?raw=true)
8. Wait until install and repair are complete.
![Install progress](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/8.png?raw=true)
9. Start option `1`, `2`, or `3`.
![Done](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2022/9.png?raw=true)

### Ubuntu 24

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/1.png?raw=true)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/2.png?raw=true)
3. Extract the archive.
![Extract archive](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/3.png?raw=true)
4. Open a terminal in the extracted folder.
![Open terminal](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/4.png?raw=true)
5. Install Python and required base tools.
![Install prerequisites](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/5.png?raw=true)
6. Start the launcher with `python3 start-anime-downloader.py`.
![Start launcher](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/6.png?raw=true)
7. Select option `4` (`Install/Repair`) on the first run.
![Option 4](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/7.png?raw=true)
8. Wait until install and repair are complete.
![Install progress](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/8.png?raw=true)
9. Start option `1`, `2`, or `3`.
![Done](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Ubuntu%2024/9.png?raw=true)

### Debian 11

1. Navigate to [Releases](https://github.com/VeridonNetzwerk/anime-downloader/releases).
![Where to find releases](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/1.png?raw=true)
2. Download the Source code (zip) from the latest release.
![Download Source code (zip)](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Windows%2010/2.png?raw=true)
3. Extract the archive.
![Extract archive](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/3.png?raw=true)
4. Open a terminal in the extracted folder.
![Open terminal](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/4.png?raw=true)
5. Install Python and required base tools.
![Install prerequisites](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/5.png?raw=true)
6. Start the launcher with `python3 start-anime-downloader.py`.
![Start launcher](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/6.png?raw=true)
7. Select option `4` (`Install/Repair`) on the first run.
![Option 4](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/7.png?raw=true)
8. Wait until install and repair are complete.
![Install progress](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/8.png?raw=true)
9. Start option `1`, `2`, or `3`.
![Done](https://github.com/VeridonNetzwerk/assets/blob/main/Aniworld%20Downloader/wiki/Installation.md/Debian%2011/9.png?raw=true)

---

## Notes About Python

AniWorld on Windows depends on curses compatibility behavior that is currently safer with Python 3.13.
The launcher prefers Python 3.13 and can recreate incompatible virtual environments automatically.
