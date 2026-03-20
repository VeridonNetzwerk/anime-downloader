# Troubleshooting

## 1) AniWorld fails with curses/_curses errors

Cause:
- Incompatible Python version in `.venv` (commonly Python 3.14).

Fix:
1. Run `python start-anime-downloader.py`.
2. Run launcher option `4`.
3. Let it recreate `.venv` with Python 3.13.
4. Retry option `1` or `3`.

## 2) npm install fails in aniwatch-api

The launcher has staged recovery:
- normal install
- install without lifecycle scripts
- clean install via npm@10
- npm cache clean + final install retry

Fix:
- Run option `4` and inspect `latest.log` for `ERROR_CODE=` entries.

## 3) FFmpeg not found (Windows)

Fix:
1. Run option `4`.
2. If FFmpeg or Node.js was just installed and is still not detected, close the launcher and terminal once.
3. Start the launcher again so Windows can reload the updated PATH entries.
4. Run option `4` again if needed.

Note:
- On Linux/macOS, option `4` installs FFmpeg via native package managers.
- A restart should only be necessary if Windows delays newly installed PATH entries for the current shell session.

## 4) API not available on port 4000

Fix:
- Use option `2` or `3` to restart the API.
- Check if another process is using port 4000.
- Check `latest.log` for build or startup errors.

## 5) Browser opens but UI is blank

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
