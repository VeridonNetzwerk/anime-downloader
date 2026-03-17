# AniWorld / AniWatch Launcher

Unified Windows launcher to install, repair, and run:

- AniWorld UI at `http://localhost:8080`
- AniWatch API at `http://localhost:4000`
- AniWatch UI at `http://localhost:4001`

## Overview

This project automates environment setup and startup for both stacks from a single menu-driven launcher.

Highlights:

- One-click dependency setup/repair (`Option 4`)
- Auto-recovery for common npm and Python issues
- WSL + Ubuntu checks and automatic provisioning
- Structured logging and error-code entries in `latest.log`

## Runtime Requirements

| Component | Requirement | Notes |
| --- | --- | --- |
| OS | Windows 10/11 | Required for launcher and WSL flow |
| Node.js | LTS (tested with 24.x) | Used for API/UI services |
| Python | 3.13.x recommended | Preferred for AniWorld compatibility |
| WSL | Ubuntu distro | Auto-installed/repaired by `Option 4` |

Important:

- Python 3.14 is not recommended for AniWorld in this setup due to curses compatibility behavior on Windows.

## Quick Start

1. Run `start-aniwatch.bat`
2. Select `4` once (`Install/Repair`)
3. Start services:

| Option | Action |
| --- | --- |
| `1` | Start AniWorld only |
| `2` | Start AniWatch only |
| `3` | Start both |
| `4` | Install/repair all dependencies |
| `5` | Exit |

## Download Sources

- https://anworld.to
- https://aniwatchtv.to

## Wiki

Detailed docs are provided in the `wiki/` folder:

- `wiki/Home.md`
- `wiki/Installation.md`
- `wiki/Usage-Guide.md`
- `wiki/How-It-Works.md`
- `wiki/Troubleshooting.md`
- `wiki/FAQ.md`

After pushing this repo, you can copy these pages into the GitHub Wiki if you want a separate wiki UI.

## Reporting Issues

If something breaks, open an issue and include:

- launcher option used (`1`/`2`/`3`/`4`)
- expected behavior vs actual behavior
- relevant `latest.log` output
- Windows, Node.js, and Python versions

An issue template is included at `.github/ISSUE_TEMPLATE/bug_report.md`.

## Legal Disclaimer

This project is provided as-is for educational and technical purposes.

I am not responsible for illegal use, copyright infringement, or any other misuse of this software.
Users are solely responsible for compliance with local laws, copyright rules, and platform terms.

## Built With AI

Parts of this project were created and refined with AI assistance.

## Attribution / Upstream Sources

Large parts and ideas were derived from:

- https://github.com/johanwestling/wsl-install
- https://github.com/nodejs/installer
- https://github.com/ruxartic/aniwatch-dl
- https://github.com/ghoshRitesh12/aniwatch-api
