# How It Works

## High-Level Flow

1. `start-aniatch.bat` is the orchestration entrypoint — provides a menu-driven UI on Windows.
2. It validates/installs Node.js, Python, and WSL + Ubuntu via system APIs.
3. Services are started based on user selection:
   - **AniWorld**: Runs via `python -m aniworld --web-ui` in the Python venv
   - **AniWatch**: Runs Node.js API server + `download-server.mjs` frontend server
4. User interacts via web browser (localhost:8080 or localhost:4001).
5. Download requests trigger `download-server.mjs` → WSL bash → `aniwatch-dl.sh`.
6. Output streams back to browser via Server-Sent Events (SSE).

## Components

### Launcher (`start-aniwatch.bat`)

A Windows batch script that orchestrates all setup and startup:
- **Menu system**: Offers single/dual service modes and install/repair
- **Dependency management**: Installs Node.js 24.x, Python 3.13.x, WSL, and Ubuntu distro
- **Recovery**: Auto-detects failures and retries with fallback strategies (e.g., npm install → ignore-scripts → npm@10 CI mode)
- **Error tracking**: Logs with structured `ERROR_CODE=` entries for troubleshooting
- **Timeout handling**: Prevents hangs with watchdog timers

For detailed logic, see: [start-aniwatch.bat source](https://github.com/VeridonNetzwerk/anime-downloader/blob/master/start-aniwatch.bat)

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
- **Handles settings** — stores user download folder and language separation preferences

Flow: UI → fetch(`/api/download`) → download-server.mjs → spawn WSL → aniwatch-dl.sh → ffmpeg/curl → mp4 files

### Download Script (`aniwatch-dl.sh`)

Bash script that runs inside WSL Ubuntu and handles the actual download workflow:
- Receives arguments from download-server.mjs (anime ID, episodes, audio type, resolution, etc.)
- Calls aniwatch-api endpoints to resolve episode streams and sources
- Uses **curl** to fetch m3u8 playlists or mp4 files
- Uses **ffmpeg** to re-encode/segment streams into standalone mp4 files
- Uses **parallel** to download multiple video segments concurrently
- Uses **jq** for JSON parsing of API responses
- Respects user settings for download folder and language-based subfolder organization

## Why WSL Is Used

**WSL (Windows Subsystem for Linux)** provides:

1. **Unix toolchain** — curl, ffmpeg, jq, parallel, bash all have mature implementations in Linux, simpler than Windows equivalents
2. **Stable downloads** — ffmpeg on Linux is more predictable for streaming protocols (m3u8 HLS, dash) than Windows PowerShell alternatives
3. **Concurrency** — GNU Parallel is designed for Unix and less reliable on Windows natively
4. **Encoding** — ffmpeg behavior is consistent across Linux/Mac/Windows when run via WSL
5. **Zero admin overhead** — auto-installable via `wsl --install` on Windows 10/11 Pro+

The launcher automatically detects and installs WSL + Ubuntu distro if missing.

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
                     │ spawn('wsl', ['bash', '-c', wrapper_cmd])
                     ▼
┌─────────────────────────────────────────────────────────┐
│  WSL 2 Ubuntu Distro (aniwatch-dl.sh runtime)            │
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
