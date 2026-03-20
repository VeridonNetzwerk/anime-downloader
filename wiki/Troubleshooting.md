# Troubleshooting

## 1) AniWorld fails with curses/_curses errors

Cause:
- Incompatible Python version in `.venv` (commonly Python 3.14).

Fix:
1. Run `python start-anime-downloader.py`.
2. Run launcher option `4`.
3. Let it recreate `.venv` with Python 3.13.
4. Retry option `1` or `3`.

## 2) AniWorld fails on Ubuntu/Debian with ensurepip or python3-venv errors

Cause:
- The system Python was installed without venv support.

Fix:
1. Run launcher option `4` once.
2. Retry option `1` or `3`.
3. If it still fails, install the missing package manually, for example `sudo apt install python3-venv`.
4. On version-specific Python installs, you may need `sudo apt install python3.12-venv` or the matching Python version.

## 3) npm install fails in aniwatch-api

The launcher has staged recovery:
- normal install
- install without lifecycle scripts
- clean install via npm@10
- npm cache clean + final install retry

Fix:
- Run option `4` and inspect `latest.log` for `ERROR_CODE=` entries.

## 4) FFmpeg not found (Windows)

Fix:
1. Run option `4`.
2. If FFmpeg or Node.js was just installed and is still not detected, close the launcher and terminal once.
3. Start the launcher again so Windows can reload the updated PATH entries.
4. Run option `4` again if needed.

Note:
- On Linux/macOS, option `4` installs FFmpeg via native package managers.
- A restart should only be necessary if Windows delays newly installed PATH entries for the current shell session.

## 5) API not available on port 4000

Fix:
- Use option `2` or `3` to restart the API.
- Check if another process is using port 4000.
- Check `latest.log` for build or startup errors.

## 6) Browser opens but UI is blank

Fix:
- Ensure `aniwatch-ui/index.html` exists.
- Restart with option `2` or `3`.
- Confirm local firewall is not blocking loopback ports.

## Reporting a Bug

Open a GitHub Issue and include:
- selected menu option
- exact error text
- `latest.log`
- OS, Node.js, Python versions
