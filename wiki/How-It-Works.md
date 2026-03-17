# How It Works

## High-Level Flow

1. `start-aniwatch.bat` is the orchestration entrypoint.
2. It validates dependencies and can repair/install them.
3. It starts services for AniWorld and/or AniWatch.
4. `download-server.mjs` serves the AniWatch UI and proxies API calls.
5. Download jobs are executed via WSL using `aniwatch-dl.sh`.

## Components

## Launcher (`start-aniwatch.bat`)

- Provides menu and startup options.
- Handles auto-install and recovery.
- Manages timeout-aware command execution.
- Writes structured logs and error codes.

## Download Server (`download-server.mjs`)

- Serves `aniwatch-ui/index.html`.
- Proxies `/api/v2/*` to local aniwatch-api.
- Manages queue and SSE stream for job output.
- Runs WSL wrapper commands for downloads.

## Download Script (`aniwatch-dl.sh`)

- Talks to the API endpoints.
- Resolves episodes, streams, and segments.
- Handles filtering options and downloads.

## Why WSL Is Used

WSL provides a Linux-compatible runtime for shell tooling (`curl`, `jq`, `ffmpeg`, `parallel`) and stable download workflow on Windows hosts.
