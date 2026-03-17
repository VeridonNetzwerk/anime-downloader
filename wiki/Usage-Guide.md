# Usage Guide

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

## Endpoints

- AniWorld UI: `http://localhost:8080`
- AniWatch API: `http://localhost:4000`
- AniWatch UI: `http://localhost:4001`

## Logs

- Main log file: `latest.log`
- Installer and launcher steps are logged with timestamps and thread labels.

## Queue Behavior (AniWatch)

- Download jobs are queued in submission order.
- Only one job runs at a time.
- You can stream progress via SSE endpoints used by the UI.
- Running jobs can be cancelled.
