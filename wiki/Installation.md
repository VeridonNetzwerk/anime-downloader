# Installation

## Prerequisites

- Windows 10 or 11
- Administator rights on your Local Machine

## Dependencies

If you run Option 4 every Dependency will install automatically.

| Component | Version | Purpose | Auto-installed |
|-----------|---------|---------|----------------|
| Node.js | 24.x (LTS) | AniWatch API & download server | ✓ |
| npm | 11+ | Package manager for Node.js | ✓ |
| Python | 3.13.x (recommended) | AniWorld downloader runtime | ✓ |
| pip | Latest (in venv) | Python package manager | ✓ |
| WSL 2 | Latest | Linux subsystem for download tools | ✓ |
| Ubuntu | Latest LTS | WSL Linux distribution | ✓ |
| curl | Latest | HTTP client (in WSL) | ✓ |
| jq | Latest | JSON processor (in WSL) | ✓ |
| ffmpeg | Latest | Video processing (in WSL) | ✓ |
| parallel | Latest | Parallel job execution (in WSL) | ✓ |
| fzf | Latest | Fuzzy finder (in WSL) | ✓ |

## First Setup (Recommended)

1. Run `start-aniwatch.bat`.
2. Select option `4` (`Install/Repair`).
3. Wait until progress reaches 100%.
4. Return to menu and launch option `1`, `2`, or `3`.

## Notes About Python

AniWorld on Windows depends on curses compatibility behavior that is currently safer with Python 3.13.
The launcher prefers Python 3.13 and can recreate incompatible virtual environments automatically.
