/**
 * AniWatch Download Server (port 4001)
 * - Serves the Web UI at /
 * - Proxies aniwatch-api requests (/api/v2/*) to localhost:4000
 * - Handles download jobs via WSL + aniwatch-dl.sh
 */

import http from 'node:http';
import { spawn } from 'node:child_process';
import { readFileSync, appendFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
import { networkInterfaces } from 'node:os';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const UI_PORT = 4001;
const API_PORT = 4000;
const DEBUG_ENABLED = process.env.ANIWATCH_DEBUG !== '0';
const LOG_PATH = path.join(__dirname, 'latest.log');
const SETTINGS_PATH = path.join(__dirname, '.aniwatch-settings.json');
const IS_WINDOWS = process.platform === 'win32';

// Default settings with Windows Downloads folder fallback
const DEFAULT_SETTINGS = {
    downloadFolder: '',
    separateLanguageFolders: false,
};

function getDefaultDownloadFolder() {
    // Try to get Windows Downloads folder
    const home = process.env.USERPROFILE || process.env.HOME || process.env.HOMEPATH || '';
    if (home) return path.join(home, 'Downloads', 'AniWatch');
    return path.join(__dirname, 'downloads');
}

function loadSettings() {
    try {
        if (existsSync(SETTINGS_PATH)) {
            const data = readFileSync(SETTINGS_PATH, 'utf8');
            return JSON.parse(data);
        }
    } catch (e) {
        // Fall through to defaults
    }
    return { ...DEFAULT_SETTINGS };
}

function saveSettings(settings) {
    try {
        writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2), 'utf8');
    } catch (e) {
        // Log but don't crash
        console.error('Failed to save settings:', e.message);
    }
}

let currentSettings = loadSettings();
if (!currentSettings.downloadFolder) {
    currentSettings.downloadFolder = getDefaultDownloadFolder();
    saveSettings(currentSettings);
}

function timeNow() {
    return new Date().toTimeString().slice(0, 8);
}

function log(level, thread, message) {
    const line = `[${timeNow()}] [${thread}/${level}]: ${message}`;
    console.log(line);
    try {
        appendFileSync(LOG_PATH, `${line}\n`, 'utf8');
    } catch {
        // Do not crash if log file cannot be written.
    }
}

function debug(thread, message) {
    if (!DEBUG_ENABLED) return;
    const line = `[${timeNow()}] [${thread}/DEBUG]: ${message}`;
    try {
        appendFileSync(LOG_PATH, `${line}\n`, 'utf8');
    } catch {
        // Do not crash if log file cannot be written.
    }
}

// Determine the Windows-side IP that WSL 2 can reach.
// Node.js runs on Windows and can read the vEthernet (WSL) adapter directly -
// no guessing needed inside WSL.
function getWslHostIp() {
    const nets = networkInterfaces();
    // Primary: the dedicated WSL virtual adapter
    for (const [name, addrs] of Object.entries(nets)) {
        if (/wsl/i.test(name)) {
            for (const addr of addrs) {
                if (addr.family === 'IPv4' && !addr.internal) return addr.address;
            }
        }
    }
    // Secondary: any vEthernet adapter (Hyper-V)
    for (const [name, addrs] of Object.entries(nets)) {
        if (/vethernet/i.test(name)) {
            for (const addr of addrs) {
                if (addr.family === 'IPv4' && !addr.internal) return addr.address;
            }
        }
    }
    return 'localhost'; // WSL 1 or single-NIC fallback
}
const DOWNLOAD_API_HOST = IS_WINDOWS ? getWslHostIp() : '127.0.0.1';
log('INFO', 'Server thread', `Download runtime: ${IS_WINDOWS ? 'WSL' : 'native bash'} (${process.platform})`);
log('INFO', 'Server thread', `Download API host detected: ${DOWNLOAD_API_HOST}`);
debug('Server thread', `DEBUG enabled: ${DEBUG_ENABLED}`);

// Read the shell script once at startup.
// At spawn time we pipe it via stdin into WSL itself (/tmp/aniwatch-<id>.sh),
// so there are zero Windows-to-WSL path translation issues.
const SCRIPT_CONTENT = readFileSync(path.join(__dirname, 'aniwatch-dl.sh'));


// Strip ANSI escape codes from terminal output
const ANSI_RE = /\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])/g;
const stripAnsi = (s) => s.replace(ANSI_RE, '');

// Job store: id -> { id, title, episodes, wrapperCmd, status, process, clients, output, exitCode }
const jobs = new Map();
const jobQueue = []; // job IDs in submission order

function processQueue() {
    const running = [...jobs.values()].some(j => j.status === 'running');
    if (running) return;
    debug('Queue thread', `Processing queue. Total jobs: ${jobQueue.length}`);
    for (const id of jobQueue) {
        const job = jobs.get(id);
        if (job && job.status === 'waiting') { runJob(job); return; }
    }
}

function runJob(job) {
    job.status = 'running';
    log('INFO', 'Download thread', `Job started: ${job.id} (${job.title})`);
    debug('Download thread', `Job args: episodes=${job.episodes}`);
    const proc = IS_WINDOWS
        ? spawn('wsl', ['bash', '-c', job.wrapperCmd], {
            windowsHide: true,
            env: Object.assign({}, process.env),
            cwd: 'C:\\',
        })
        : spawn('bash', ['-c', job.wrapperCmd], {
            env: Object.assign({}, process.env),
            cwd: __dirname,
        });
    job.process = proc;
    proc.stdin.write(SCRIPT_CONTENT);
    proc.stdin.end();

    const broadcast = (text) => {
        const clean = stripAnsi(text);
        job.output.push(clean);
        const msg = `data: ${JSON.stringify(clean)}\n\n`;
        for (const client of job.clients) client.write(msg);
    };

    const utf16Bufs = [];
    const handleChunk = (buf) => {
        const looksUtf16 = buf.length >= 4 && buf[1] === 0 && buf[3] === 0;
        if (looksUtf16) utf16Bufs.push(buf);
        else broadcast(buf.toString('utf8'));
    };

    proc.stdout.on('data', handleChunk);
    proc.stderr.on('data', handleChunk);
    proc.on('error', (err) => {
        log('ERROR', 'Download thread', `Could not start WSL process: ${err.message}`);
        broadcast(`\n[ERROR] Could not start WSL: ${err.message}\n`);
        job.status = 'error';
        job.exitCode = -1;
        const doneMsg = `event: done\ndata: -1\n\n`;
        for (const client of job.clients) { client.write(doneMsg); client.end(); }
        job.clients.clear();
        processQueue();
    });
    proc.on('close', (code) => {
        debug('Download thread', `Job closed with raw exit code: ${String(code)}`);
        if (utf16Bufs.length > 0) {
            const combined = Buffer.concat(utf16Bufs);
            const text = combined.toString('utf16le').replace(/\r\n/g, '\n').replace(/\0/g, '');
            broadcast(text);
        }
        const NO_DISTRO = IS_WINDOWS && code === 4294967295;
        if (NO_DISTRO) {
            log('WARN', 'Download thread', 'No WSL Linux distribution installed');
            broadcast(
                '\nWarning: No WSL Linux distribution installed.\n' +
                'Fix: Open PowerShell as Administrator and run:\n\n' +
                '    wsl --install\n\n' +
                'Then restart Windows. Recommended distro: Ubuntu.\n'
            );
        }
        job.status = code === 0 ? 'done' : 'error';
        job.exitCode = code ?? -1;
        log(job.status === 'done' ? 'INFO' : 'ERROR', 'Download thread', `Job ${job.id} finished with status=${job.status}, Code=${job.exitCode}`);
        const doneMsg = `event: done\ndata: ${job.exitCode}\n\n`;
        for (const client of job.clients) { client.write(doneMsg); client.end(); }
        job.clients.clear();
        processQueue();
    });
}

// -- Helpers -----------------------------------------------------------------

function serveHtml(res) {
    try {
        const content = readFileSync(path.join(__dirname, 'aniwatch-ui', 'index.html'));
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(content);
        debug('HTTP thread', 'UI index.html served successfully');
    } catch {
        log('ERROR', 'HTTP thread', 'UI index.html was not found');
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>UI not found</h1><p>Expected: <code>aniwatch-ui/index.html</code></p>');
    }
}

function json(res, status, data) {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let raw = '';
        req.on('data', (chunk) => {
            raw += chunk;
            if (raw.length > 64 * 1024) {
                reject(new Error('Request body too large'));
                req.destroy();
            }
        });
        req.on('end', () => {
            try { resolve(JSON.parse(raw)); }
            catch { reject(new Error('Invalid JSON')); }
        });
        req.on('error', reject);
    });
}

function proxyToApi(req, res, pathname, search) {
    debug('Proxy thread', `Proxy Request: ${req.method} ${pathname}${search || ''}`);
    const opts = {
        hostname: 'localhost',
        port: API_PORT,
        path: pathname + (search || ''),
        method: req.method,
        headers: { 'user-agent': 'aniwatch-ui/1.0', 'accept': 'application/json' },
    };
    const proxyReq = http.request(opts, (proxyRes) => {
        const headers = Object.assign({}, proxyRes.headers, {
            'Access-Control-Allow-Origin': '*',
        });
        delete headers['transfer-encoding'];
        res.writeHead(proxyRes.statusCode, headers);
        proxyRes.pipe(res);
    });
    proxyReq.on('error', () => {
        log('ERROR', 'Proxy thread', `aniwatch-api unreachable for ${pathname}${search || ''}`);
        json(res, 502, { error: 'aniwatch-api unreachable - is port 4000 running?' });
    });
    req.pipe(proxyReq);
}

// Only allow safe characters; strip anything that could inject into shell args
function sanitize(val, maxLen = 200) {
    if (!val || typeof val !== 'string') return null;
    const clean = val.replace(/[;&|`$(){}!\n\r\\]/g, '').trim();
    return clean.length ? clean.slice(0, maxLen) : null;
}

// -- HTTP Server --------------------------------------------------------------

const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${UI_PORT}`);
    const { pathname } = url;
    debug('HTTP thread', `Incoming: ${req.method} ${pathname}${url.search || ''}`);

    // Global CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

    // -- GET / -> Web UI -----------------------------------------------------
    if (req.method === 'GET' && (pathname === '/' || pathname === '/index.html')) {
        log('INFO', 'HTTP thread', `UI Request: ${pathname}`);
        serveHtml(res);
        return;
    }

    // -- GET /api/v2/* -> proxy to aniwatch-api ------------------------------
    if (req.method === 'GET' && pathname.startsWith('/api/v2/')) {
        log('INFO', 'Proxy thread', `Proxy API Request: ${pathname}`);
        proxyToApi(req, res, pathname, url.search);
        return;
    }

    // -- GET /api/settings -> get download settings ---------------------------
    if (req.method === 'GET' && pathname === '/api/settings') {
        log('INFO', 'HTTP thread', 'Settings request received');
        json(res, 200, currentSettings);
        return;
    }

    // -- POST /api/settings -> update download settings -----------------------
    if (req.method === 'POST' && pathname === '/api/settings') {
        log('INFO', 'HTTP thread', 'Settings update request received');
        let body;
        try { body = await parseBody(req); }
        catch (e) {
            log('ERROR', 'HTTP thread', `Invalid settings request: ${e.message}`);
            json(res, 400, { error: e.message });
            return;
        }
        
        if (body.downloadFolder !== undefined) {
            currentSettings.downloadFolder = String(body.downloadFolder).trim();
        }
        if (body.separateLanguageFolders !== undefined) {
            currentSettings.separateLanguageFolders = Boolean(body.separateLanguageFolders);
        }
        
        saveSettings(currentSettings);
        log('INFO', 'HTTP thread', `Settings updated: downloadFolder=${currentSettings.downloadFolder}, separateLangs=${currentSettings.separateLanguageFolders}`);
        json(res, 200, { success: true, settings: currentSettings });
        return;
    }

    // -- POST /api/download -> start download --------------------------------
    if (req.method === 'POST' && pathname === '/api/download') {
        log('INFO', 'HTTP thread', 'New download request received');
        let body;
        try { body = await parseBody(req); }
        catch (e) {
            log('ERROR', 'HTTP thread', `Invalid request body: ${e.message}`);
            json(res, 400, { error: e.message });
            return;
        }

        const animeId   = sanitize(body.anime_id);
        const animeName = sanitize(body.anime_name);
        if (!animeId && !animeName) {
            log('WARN', 'HTTP thread', 'Rejected download request without anime_id/anime_name');
            json(res, 400, { error: 'anime_id or anime_name required' });
            return;
        }

        const id = crypto.randomUUID();

        // Write the script into the active shell runtime's /tmp filesystem via stdin,
        // then run it. On Windows this is WSL, on Unix-like hosts it is native bash.
        // Embed args directly in the bash -c string so Windows quote-escaping
        // can't corrupt them (passing "$@" through WSL.exe loses the quotes).
        // sanitize() has already removed all shell-special chars; we single-quote
        // each value for defence-in-depth. Single quotes cannot appear in sanitized values.
        const sq = (s) => `'${s}'`;

        const wslScriptPath = `/tmp/aniwatch-${id}.sh`;
        const scriptArgs = [];
        if (animeId)   scriptArgs.push('-i', sq(animeId));
        else           scriptArgs.push('-a', sq(animeName));

        const episodes = sanitize(body.episodes);
        if (episodes) scriptArgs.push('-e', sq(episodes));

        scriptArgs.push('-o', body.audio === 'dub' ? 'dub' : 'sub');

        const resolution = sanitize(body.resolution);
        if (resolution && /^\d+$/.test(resolution)) scriptArgs.push('-r', resolution);

        const srv = sanitize(body.server);
        if (srv) scriptArgs.push('-S', sq(srv));

        const subtitles = sanitize(body.subtitles);
        if (subtitles) scriptArgs.push('-L', sq(subtitles));

        const threads = parseInt(body.threads);
        scriptArgs.push('-t', String(Number.isNaN(threads) ? 4 : Math.min(Math.max(threads, 1), 16)));

        // All args are now embedded in the bash -c string - no $@ needed
        // ANIWATCH_API_URL is exported directly (WSLENV is unreliable on some setups).
        // WSL_HOST_IP was resolved on the Windows side at startup (vEthernet WSL adapter).
        // Pass it as a literal so WSL needs no network discovery at all.
        // Settings: download folder and language folder separation from currentSettings
        const sepLangsFlag = currentSettings.separateLanguageFolders ? '1' : '0';
        const downloadFolderEscaped = currentSettings.downloadFolder.replace(/'/g, "'\\''");
        
        const wrapperCmd =
            `export ANIWATCH_API_URL='http://${DOWNLOAD_API_HOST}:${API_PORT}'; ` +
            `export ANIWATCH_DL_VIDEO_DIR='${downloadFolderEscaped}'; ` +
            `export ANIWATCH_DL_SEP_LANGS='${sepLangsFlag}'; ` +
            `echo "Download runtime: ${IS_WINDOWS ? 'WSL' : 'native bash'}"; ` +
            `echo "API endpoint: http://${DOWNLOAD_API_HOST}:${API_PORT}"; ` +
            // Warn if running inside Docker Desktop's internal WSL distro
            `if grep -qi "docker desktop" /etc/os-release 2>/dev/null; then ` +
            `  echo ""; ` +
            `  echo "ERROR: You are using the Docker Desktop WSL distro."; ` +
            `  echo "This distro is intended for containers, not downloads."; ` +
            `  echo ""; ` +
            `  echo "Fix - PowerShell as Administrator:"; ` +
            `  echo "  wsl --install -d Ubuntu"; ` +
            `  echo "  wsl --set-default Ubuntu"; ` +
            `  echo "Then restart Windows and try again."; ` +
            `  exit 1; ` +
            `fi; ` +
            // Detect package manager and install missing tools
            // Run as current user - root needs no sudo, others use sudo if available
            `SUDO=''; command -v sudo >/dev/null 2>&1 && [ "$(id -u)" != "0" ] && SUDO='sudo'; ` +
            `MISSING=''; ` +
            `for t in curl jq fzf ffmpeg parallel; do command -v "$t" >/dev/null 2>&1 || MISSING="$MISSING $t"; done; ` +
            `if [ -n "$MISSING" ]; then ` +
            `  echo "Missing tools:$MISSING - installing..."; ` +
            `  if command -v apt-get >/dev/null 2>&1; then ` +
            `    $SUDO apt-get update -qq && $SUDO apt-get install -y $MISSING 2>&1; ` +
            `  elif command -v apk >/dev/null 2>&1; then ` +
            `    $SUDO apk add --no-cache $MISSING 2>&1; ` +
            `  elif command -v dnf >/dev/null 2>&1; then ` +
            `    $SUDO dnf install -y $MISSING 2>&1; ` +
            `  elif command -v brew >/dev/null 2>&1; then ` +
            `    brew install $MISSING 2>&1; ` +
            `  elif command -v pacman >/dev/null 2>&1; then ` +
            `    $SUDO pacman -Sy --noconfirm $MISSING 2>&1; ` +
            `  else ` +
            `    echo "No known package manager found."; ` +
            `    echo "Please install manually:$MISSING"; ` +
            `    exit 1; ` +
            `  fi; ` +
            `fi; ` +
            `cat > ${wslScriptPath} && chmod +x ${wslScriptPath} && ` +
            `bash ${wslScriptPath} ${scriptArgs.join(' ')}; ` +
            `EC=$?; rm -f ${wslScriptPath}; exit $EC`;

        // Enqueue the job and start immediately if no other job is running.
        const job = {
            id,
            title: animeId || animeName,
            episodes: sanitize(body.episodes) || '*',
            wrapperCmd,
            status: 'waiting',
            process: null,
            clients: new Set(),
            output: [],
            exitCode: null,
        };
        jobs.set(id, job);
        jobQueue.push(id);
        log('INFO', 'Queue thread', `Job queued: ${id} (${job.title}) pos=${jobQueue.indexOf(id) + 1}`);
        processQueue();
        json(res, 200, { id, position: jobQueue.indexOf(id) + 1, status: job.status });
        return;
    }

    // -- GET /api/download/stream/:id -> SSE stream --------------------------
    if (req.method === 'GET' && pathname.startsWith('/api/download/stream/')) {
        const id = pathname.slice('/api/download/stream/'.length);
        const entry = jobs.get(id);
        if (!entry) {
            log('WARN', 'SSE thread', `Stream request for unknown job: ${id}`);
            res.writeHead(404);
            res.end('Download not found');
            return;
        }

        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        });
        res.flushHeaders();

        // Replay buffered output so far
        for (const chunk of entry.output) {
            res.write(`data: ${JSON.stringify(chunk)}\n\n`);
        }

        if (entry.status === 'done' || entry.status === 'error') {
            debug('SSE thread', `Immediate done for job ${id} with code ${entry.exitCode}`);
            res.write(`event: done\ndata: ${entry.exitCode}\n\n`);
            res.end();
            return;
        }

        entry.clients.add(res);
        debug('SSE thread', `Client connected for job ${id}. Clients=${entry.clients.size}`);
        req.on('close', () => entry.clients.delete(res));
        return;
    }

    // -- POST /api/download/cancel/:id -> kill/dequeue job -------------------
    if (req.method === 'POST' && pathname.startsWith('/api/download/cancel/')) {
        const id = pathname.slice('/api/download/cancel/'.length);
        const job = jobs.get(id);
        if (job && job.status === 'running') {
            log('WARN', 'Queue thread', `Cancelling running job: ${id}`);
            job.process?.kill();
            json(res, 200, { ok: true });
        } else if (job && job.status === 'waiting') {
            const qi = jobQueue.indexOf(id);
            if (qi >= 0) jobQueue.splice(qi, 1);
            jobs.delete(id);
            log('INFO', 'Queue thread', `Removed waiting job: ${id}`);
            json(res, 200, { ok: true });
        } else {
            log('WARN', 'Queue thread', `Cancel requested for unknown job: ${id}`);
            json(res, 404, { error: 'not found' });
        }
        return;
    }

    // -- GET /api/queue -> job queue status ----------------------------------
    if (req.method === 'GET' && pathname === '/api/queue') {
        debug('Queue thread', 'Queue status requested');
        const list = jobQueue.map((jid, i) => {
            const j = jobs.get(jid);
            if (!j) return null;
            return { id: j.id, title: j.title, episodes: j.episodes, status: j.status, position: i + 1 };
        }).filter(Boolean);
        json(res, 200, { queue: list });
        return;
    }

    // -- POST /api/queue/remove/:id -> remove/cancel any job -----------------
    if (req.method === 'POST' && pathname.startsWith('/api/queue/remove/')) {
        const id = pathname.slice('/api/queue/remove/'.length);
        const job = jobs.get(id);
        if (!job) {
            debug('Queue thread', `remove ignored, job missing: ${id}`);
            json(res, 200, { ok: true });
            return;
        }
        if (job.status === 'running') {
            log('WARN', 'Queue thread', `Remove running job: ${id}`);
            job.process?.kill(); // close handler calls processQueue()
        } else {
            const qi = jobQueue.indexOf(id);
            if (qi >= 0) jobQueue.splice(qi, 1);
            jobs.delete(id);
            log('INFO', 'Queue thread', `Remove waiting job: ${id}`);
        }
        json(res, 200, { ok: true });
        return;
    }

    log('WARN', 'HTTP thread', `Unknown route: ${req.method} ${pathname}`);
    res.writeHead(404);
    res.end('Not found');
});

server.listen(UI_PORT, '127.0.0.1', () => {
    log('INFO', 'Render thread', 'AniWatch Downloader UI started');
    log('INFO', 'Render thread', `Open: http://localhost:${UI_PORT}`);
    log('INFO', 'Render thread', `API Proxy: http://localhost:${API_PORT}`);
});

