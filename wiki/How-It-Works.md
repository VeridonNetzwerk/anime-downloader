# How It Works

## High-Level Flow

1. `start-anime-downloader.py` is the orchestration entrypoint.
2. It detects the user OS (Windows, Linux, macOS).
3. Option `4` applies OS-specific install/repair logic.
3. Services are started based on user selection:
   - **AniWorld**: Runs via `python -m aniworld --web-ui` in the Python venv
   - **AniWatch**: Runs Node.js API server + `download-server.mjs` frontend server
4. User interacts via web browser (localhost:8080 or localhost:4001).
5. Download requests trigger `download-server.mjs` → shell runtime → `aniwatch-dl.sh`.
6. Output streams back to browser via Server-Sent Events (SSE).

## Components

### Launcher (`start-anime-downloader.py`)

A Python launcher that orchestrates setup and startup across supported operating systems:
- **Menu system**: Offers single/dual service modes and install/repair
- **OS detection**: Chooses setup flow for Windows, Linux, or macOS
- **Dependency management**: Installs/repairs Node.js, Python venv, API build artifacts, and shell tools
- **Recovery**: Auto-detects failures and retries with fallback strategies (e.g., npm install → ignore-scripts → npm@10 CI mode)
- **Error tracking**: Logs with structured `ERROR_CODE=` entries for troubleshooting
- **Timeout handling**: Prevents hangs with watchdog timers

For detailed logic, see: [start-anime-downloader.py source](https://github.com/VeridonNetzwerk/anime-downloader/blob/master/start-anime-downloader.py)

### AniWorld Downloader (`python -m aniworld`)

Upstream: **[aniworld](https://pypi.org/project/aniworld/)** Python package

- CLI tool for searching and downloading anime from anworld.to
- Provides a web UI on port 8080 (via `--web-ui` flag)
- Handles episode resolution, subtitle/audio filtering, and mp4 output
- Full documentation: [AniWorld GitHub](https://github.com/awarent/aniworld)

### AniWatch API (`aniwatch-api/`)

Upstream: **[aniwatch-api](https://github.com/ghoshRitesh12/aniwatch-api)** by ghoshRitesh12

- TypeScript/Node.js backend that proxies HiAnime (aniwatchtv.to) data
- Exposes REST endpoints for:
  - Anime search and metadata (`/api/v2/hianime/search`, `/api/v2/hianime/anime/:id`)
  - Episode lists and streaming sources (`/api/v2/hianime/anime/:id/episodes`)
  - Server and source resolution (`/api/v2/hianime/episode/sources`)
- Runs on port 4000 locally
- Documentation: [aniwatch-api README](https://github.com/ghoshRitesh12/aniwatch-api#readme)

### Download Server (`download-server.mjs`)

Custom Node.js HTTP server that:
- **Hosts the AniWatch UI** on port 4001 (aniwatch-ui/index.html)
- **Proxies API calls** to the local aniwatch-api (port 4000)
- **Manages download queue** — serializes jobs and prevents parallel overwrites
- **Streams job output** via Server-Sent Events (SSE) to the browser for live progress
- **Executes downloads** by spawning WSL bash and piping `aniwatch-dl.sh` via stdin
- **Runtime selection**:
  - Windows: WSL bash
  - Linux/macOS: native bash
- **Handles settings** — stores user download folder and language separation preferences

Flow: UI → fetch(`/api/download`) → download-server.mjs → spawn shell runtime → aniwatch-dl.sh → ffmpeg/curl → mp4 files

### Download Script (`aniwatch-dl.sh`)

Bash script that runs inside the selected shell runtime (WSL on Windows, native shell on Linux/macOS) and handles the actual download workflow:
- Receives arguments from download-server.mjs (anime ID, episodes, audio type, resolution, etc.)
- Calls aniwatch-api endpoints to resolve episode streams and sources
- Uses **curl** to fetch m3u8 playlists or mp4 files
- Uses **ffmpeg** to re-encode/segment streams into standalone mp4 files
- Uses **parallel** to download multiple video segments concurrently
- Uses **jq** for JSON parsing of API responses
- Respects user settings for download folder and language-based subfolder organization

## Runtime Model

### Windows: WSL Runtime

WSL (Windows Subsystem for Linux) provides:

1. **Unix toolchain** — curl, ffmpeg, jq, parallel, bash all have mature implementations in Linux, simpler than Windows equivalents
2. **Stable downloads** — ffmpeg on Linux is more predictable for streaming protocols (m3u8 HLS, dash) than Windows PowerShell alternatives
3. **Concurrency** — GNU Parallel is designed for Unix and less reliable on Windows natively
4. **Encoding** — ffmpeg behavior is consistent across Linux/Mac/Windows when run via WSL
5. **Automated setup** — installable via option `4`

### Linux and macOS: Native Runtime

On Linux/macOS, `download-server.mjs` executes `aniwatch-dl.sh` directly with local bash and package-manager-managed tools.

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  User Browser (http://localhost:4001)                   │
│  AniWatch UI (aniwatch-ui/index.html)                   │
└────────────────────┬────────────────────────────────────┘
                     │ fetch(/api/download, {anime_id, episodes, ...})
                     │ fetch(/api/settings)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Download Server (download-server.mjs:4001)              │
│  ├─ Hosts UI                                             │
│  ├─ API proxy to port 4000                              │
│  ├─ Job queue manager                                   │
│  └─ SSE stream (live progress)                          │
└────────────────────┬────────────────────────────────────┘
                     │ [job serialization]
                     │ spawn(runtime shell)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Runtime shell (WSL Ubuntu or native bash)                │
│  ├─ curl → aniwatchtv.to / aniwatch-api                 │
│  ├─ jq → parse JSON responses                           │
│  ├─ ffmpeg → encode/segment video                       │
│  ├─ parallel → concurrent segment download             │
│  └─ fzf → interactive server/episode selection          │
└────────────────────┬────────────────────────────────────┘
                     │ → ~/.../Downloads/AniWatch/anime/
                     │    (or custom folder + language subfolder)
                     ▼
              [mp4 files]
```
