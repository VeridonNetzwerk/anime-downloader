# Usage Guide

## Start Command

Run the launcher with:

```bash
python start-anime-downloader.py
```

## Launcher Menu

- `1` AniWorld only
- `2` AniWatch only
- `3` Start both
- `4` Install/Repair all dependencies
- `5` Exit

## Recommended Workflow

1. Run `4` once after cloning/downloading the project.
2. Use `3` for full stack startup.
3. Use `1` or `2` if you only need one side.

OS behavior for option `4`:

- Windows: installs/repairs Node.js and WSL + Ubuntu
- Linux: installs dependencies via apt/dnf/pacman
- macOS: installs dependencies via Homebrew

## Source Selection

- AniWorld is best suited for German Sub / Dub content.
- AniWatch is best suited for English Sub / Dub content.
- If you are unsure, start both with `3` and use the source that matches your preferred language.

## Endpoints

- AniWorld UI: `http://localhost:8080`
- AniWatch API: `http://localhost:4000`
- AniWatch UI: `http://localhost:4001`

## Logs

- Main log file: `latest.log`
- Installer and launcher steps are logged with timestamps and thread labels.
- Structured installer failures include `ERROR_CODE=` markers for diagnosis.

## Queue Behavior (AniWatch)

- Download jobs are queued in submission order.
- Only one job runs at a time.
- You can stream progress via SSE endpoints used by the UI.
- Running jobs can be cancelled.
