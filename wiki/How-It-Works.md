# How It Works

## High-Level Flow

1. `start-anime-downloader.py` is the orchestration entrypoint.
2. It detects the user OS (Windows, Linux, macOS).
3. Option `4` applies OS-specific install/repair logic.
4. Services are started based on user selection:
   - **AniWorld**: Runs via `python -m aniworld --web-ui`
   - **AniWatch**: Runs Node.js API server + `download-server.mjs` frontend server
5. User interacts via browser (localhost:8080 or localhost:4001).
6. Download requests trigger `download-server.mjs` -> `aniwatch-dl.py` -> ffmpeg output.
7. Output streams back to browser via Server-Sent Events (SSE).

## Components

### Launcher (`start-anime-downloader.py`)

A Python launcher that orchestrates setup and startup across supported operating systems:
- **Menu system**: Offers single/dual service modes and install/repair
- **OS detection**: Chooses setup flow for Windows, Linux, or macOS
- **Dependency management**: Installs/repairs Node.js, FFmpeg, Python venv, API build artifacts
- **Recovery**: Auto-detects failures and retries with fallback strategies
- **Error tracking**: Logs with structured `ERROR_CODE=` entries for troubleshooting

For detailed logic, see: [start-anime-downloader.py source](https://github.com/VeridonNetzwerk/anime-downloader/blob/master/start-anime-downloader.py)

### AniWorld Downloader (`python -m aniworld`)

Upstream: **[aniworld](https://pypi.org/project/aniworld/)** Python package

- CLI tool for searching and downloading anime from anworld.to
- Provides a web UI on port 8080 (via `--web-ui`)
- Handles episode resolution, subtitle/audio filtering, and mp4 output

### AniWatch API (`aniwatch-api/`)

Upstream: **[aniwatch-api](https://github.com/ghoshRitesh12/aniwatch-api)**

- TypeScript/Node.js backend for HiAnime metadata and stream endpoints
- Runs on port 4000 locally
- Provides search, anime metadata, episode lists, servers, and sources endpoints

### Download Server (`download-server.mjs`)

Custom Node.js HTTP server that:
- **Hosts the AniWatch UI** on port 4001
- **Proxies API calls** to aniwatch-api (port 4000)
- **Manages queue** - serial execution of download jobs
- **Streams live output** via SSE to the browser
- **Executes downloads** by spawning native Python downloader `aniwatch-dl.py`
- **Stores settings** (`.aniwatch-settings.json`) for output directory and language folder separation

Flow: UI -> `/api/download` -> `download-server.mjs` -> `aniwatch-dl.py` -> ffmpeg -> mp4 files

### Native Downloader (`aniwatch-dl.py`)

Python script that performs the actual AniWatch download workflow:
- Resolves anime and episode metadata via local aniwatch-api
- Resolves server + source URLs (`/episode/servers`, `/episode/sources`)
- Downloads/muxes media through **ffmpeg**
- Downloads selected subtitle tracks
- Writes files to configured download path

## Runtime Model

### Windows

Native runtime:
- `download-server.mjs` starts `aniwatch-dl.py` directly
- `aniwatch-dl.py` uses local ffmpeg binary
- Option `4` installs/repairs Node.js + FFmpeg

### Linux and macOS

Native runtime as well:
- `download-server.mjs` starts `aniwatch-dl.py`
- ffmpeg is provided via system package manager (apt/dnf/pacman/brew)

## Data Flow Diagram

```
Browser UI (:4001)
  -> download-server.mjs
     -> queue manager + SSE
     -> aniwatch-dl.py
        -> aniwatch-api (:4000)
        -> ffmpeg
        -> mp4/subtitle files
```
