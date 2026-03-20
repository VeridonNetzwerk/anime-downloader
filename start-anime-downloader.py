#!/usr/bin/env python3

from __future__ import annotations

import atexit
import ctypes
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
API_DIR = ROOT_DIR / 'aniwatch-api'
VENV_DIR = ROOT_DIR / '.venv'
LOG_FILE = ROOT_DIR / 'latest.log'

ANIWORLD_VERSION = '4.1.1'

ANIWORLD_PORT = 8080
ANIWATCH_API_PORT = 4000
ANIWATCH_UI_PORT = 4001

OS_NAME = platform.system().lower()
IS_WINDOWS = OS_NAME == 'windows'
IS_LINUX = OS_NAME == 'linux'
IS_MACOS = OS_NAME == 'darwin'

PROCESS_REGISTRY: list[subprocess.Popen[bytes]] = []
INSTALL_UI_ENABLED = False


def timestamp() -> str:
    return time.strftime('%H:%M:%S')


def log(level: str, thread: str, message: str, *, echo: bool = True) -> None:
    line = f'[{timestamp()}] [{thread}/{level}]: {message}'
    try:
        with LOG_FILE.open('a', encoding='utf-8') as handle:
            handle.write(line + '\n')
    except OSError:
        pass
    if echo and (not INSTALL_UI_ENABLED or level not in ('DEBUG',)):
        print(line)


def log_error_code(thread: str, code: str, message: str = '') -> None:
    if message:
        log('ERROR', thread, f'ERROR_CODE={code} - {message}')
    else:
        log('ERROR', thread, f'ERROR_CODE={code}')


def reset_log() -> None:
    try:
        with LOG_FILE.open('w', encoding='utf-8') as handle:
            handle.write(f'[{timestamp()}] [Launcher thread/INFO]: New session started.\n')
    except OSError:
        pass


def print_header() -> None:
    print('\n==========================================')
    print('  Anime Downloader Launcher (Python)')
    print('==========================================\n')


def print_menu() -> None:
    print('  1) AniWorld Downloader (Ger Dub, Ger Sub)   [http://localhost:8080]')
    print('  2) AniWatch Downloader (Eng Dub, Eng Sub)   [http://localhost:4001]')
    print('  3) Start both')
    print('  4) Install/Repair (all downloaders)')
    print('  5) Exit\n')


def render_progress(percent: int, text: str) -> None:
    if not INSTALL_UI_ENABLED:
        return
    filled = int((percent * 54) / 100)
    bar = ('#' * filled).ljust(54)
    print('\033[2J\033[H', end='')
    print(' ============================================================')
    print('  Installation / repair in progress...')
    print(' ============================================================')
    print()
    print('  +------------------------------------------------------+')
    print(f'  |{bar}| {percent:3d}%')
    print('  +------------------------------------------------------+')
    print()
    print('  Current:')
    print(f'  {text}')
    print()
    print('  Details in latest.log')
    log('INFO', 'Installer thread', f'Progress {percent}% - {text}', echo=False)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def node_command() -> str:
    return 'node.exe' if IS_WINDOWS else 'node'


def npm_command() -> str:
    return 'npm.cmd' if IS_WINDOWS else 'npm'


def venv_python_path() -> Path:
    if IS_WINDOWS:
        return VENV_DIR / 'Scripts' / 'python.exe'
    return VENV_DIR / 'bin' / 'python'


def is_port_open(port: int, host: str = '127.0.0.1') -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def run_command(
    command: list[str] | str,
    *,
    cwd: Path | None = None,
    timeout: int = 0,
    thread: str = 'Launcher thread',
    elevated: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    shell = isinstance(command, str)
    log('DEBUG', thread, f'run_command: {command}')

    if elevated and IS_WINDOWS:
        if shell:
            elevated_cmd = command
        else:
            elevated_cmd = subprocess.list2cmdline(command)
        return run_windows_elevated(elevated_cmd, timeout=timeout, thread=thread)

    kwargs = {
        'cwd': str(cwd or ROOT_DIR),
        'shell': shell,
    }
    if timeout > 0:
        kwargs['timeout'] = timeout

    result = subprocess.run(command, **kwargs)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def run_windows_elevated(command: str, *, timeout: int, thread: str) -> subprocess.CompletedProcess[bytes]:
    timer = max(timeout, 30)
    # If already running as administrator, skip the -Verb RunAs indirection
    if is_admin_windows():
        log('DEBUG', thread, f'run_elevated (already admin): {command}')
        result = subprocess.run(['cmd.exe', '/c', command])
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command)
        return result
    ps_command = (
        "$cmd = $env:CMD_TO_RUN; "
        "$timeout = [int]$env:CMD_TIMEOUT; "
        "$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -Verb RunAs -PassThru; "
        "if($p.WaitForExit($timeout * 1000)){ exit $p.ExitCode } else { try { $p.Kill() } catch {}; exit 124 }"
    )
    env = os.environ.copy()
    env['CMD_TO_RUN'] = command
    env['CMD_TIMEOUT'] = str(timer)
    log('DEBUG', thread, f'run_windows_elevated: {command}')
    result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_command], env=env)
    if result.returncode == 124:
        log_error_code(thread, 'ELEV_TIMEOUT', 'elevated command timed out')
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def pick_windows_python_bootstrap() -> list[str] | None:
    for ver in ('3.13', '3.12', '3.11', '3.10'):
        cmd = ['py', f'-{ver}', '--version']
        try:
            if subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                return ['py', f'-{ver}']
        except OSError:
            pass

    if command_exists('winget'):
        log('INFO', 'AniWorld thread', 'No Python <=3.13 found. Installing Python 3.13 via winget')
        render_progress(36, 'Install Python 3.13')
        try:
            run_command(
                [
                    'winget',
                    'install',
                    '-e',
                    '--id',
                    'Python.Python.3.13',
                    '--accept-package-agreements',
                    '--accept-source-agreements',
                    '--silent',
                    '--disable-interactivity',
                ],
                timeout=1800,
                thread='AniWorld thread',
            )
        except subprocess.CalledProcessError:
            pass
        try:
            if subprocess.run(['py', '-3.13', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                return ['py', '-3.13']
        except OSError:
            pass

    if command_exists('py'):
        return ['py', '-3']
    if command_exists('python'):
        return ['python']
    return None


def ensure_non_windows_python_venv_support(bootstrap: list[str]) -> None:
    if IS_WINDOWS:
        return

    probe = subprocess.run(
        bootstrap + ['-m', 'ensurepip', '--version'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if probe.returncode == 0:
        return

    if IS_LINUX and command_exists('apt-get'):
        render_progress(40, 'Install Python venv support')
        run_command(['sudo', 'apt-get', 'update'], timeout=900, thread='AniWorld thread', check=False)

        version_pkg = f'python{sys.version_info.major}.{sys.version_info.minor}-venv'
        run_command(['sudo', 'apt-get', 'install', '-y', version_pkg], timeout=900, thread='AniWorld thread', check=False)
        run_command(['sudo', 'apt-get', 'install', '-y', 'python3-venv'], timeout=900, thread='AniWorld thread', check=False)

        retry = subprocess.run(
            bootstrap + ['-m', 'ensurepip', '--version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if retry.returncode == 0:
            log('INFO', 'AniWorld thread', 'Installed Python venv support successfully')
            return

        raise RuntimeError(
            f'Python venv support is missing. Install {version_pkg} or python3-venv and retry.'
        )

    if IS_LINUX:
        log('WARN', 'AniWorld thread', 'ensurepip is unavailable on this Linux system. Install the distro-specific Python venv package.')
        raise RuntimeError('Python venv support is missing. Install the distro-specific python venv package and retry.')


def create_venv_with_bootstrap() -> None:
    if venv_python_path().exists():
        return

    bootstrap = [sys.executable]
    if IS_WINDOWS:
        # Prefer the currently running interpreter when it is compatible.
        if not (sys.version_info.major == 3 and sys.version_info.minor <= 13):
            picked = pick_windows_python_bootstrap()
            if not picked:
                log_error_code('AniWorld thread', 'PYTHON_NOT_FOUND', 'No compatible Python interpreter available')
                raise RuntimeError('No Python interpreter found. Install Python 3.13.x and retry.')
            bootstrap = picked
    else:
        ensure_non_windows_python_venv_support(bootstrap)

    log('INFO', 'AniWorld thread', f'Creating Python venv in {VENV_DIR}')
    run_command(bootstrap + ['-m', 'venv', str(VENV_DIR)], timeout=600, thread='AniWorld thread')


def remove_incompatible_venv_if_needed() -> None:
    if not venv_python_path().exists():
        return
    if not IS_WINDOWS:
        return
    result = subprocess.run([str(venv_python_path()), '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        log('WARN', 'AniWorld thread', 'Broken venv detected and removed')
        return
    version_text = result.stdout.strip() or result.stderr.strip()
    parts = version_text.replace('Python', '').strip().split('.')
    if len(parts) >= 2:
        try:
            major = int(parts[0])
            minor = int(parts[1])
        except ValueError:
            return
        if major == 3 and minor >= 14:
            shutil.rmtree(VENV_DIR, ignore_errors=True)
            log('WARN', 'AniWorld thread', f'Venv uses Python {major}.{minor} (>=3.14). Recreating.')


def ensure_aniworld() -> None:
    render_progress(34, 'Find Python interpreter')
    remove_incompatible_venv_if_needed()
    render_progress(46, 'Create Python venv')
    create_venv_with_bootstrap()

    vpy = str(venv_python_path())
    if not Path(vpy).exists():
        log_error_code('AniWorld thread', 'PYTHON_VENV_CREATE_FAILED', 'venv creation failed')
        raise RuntimeError('Could not create Python virtual environment.')

    render_progress(52, 'Upgrade pip')
    run_command(
        [
            vpy,
            '-m',
            'pip',
            'install',
            '--disable-pip-version-check',
            '--no-input',
            '--progress-bar',
            'off',
            '--timeout',
            '60',
            '--retries',
            '2',
            '--upgrade',
            'pip',
        ],
        timeout=600,
        thread='AniWorld thread',
    )

    render_progress(58, f'Install aniworld {ANIWORLD_VERSION}')
    run_command(
        [
            vpy,
            '-m',
            'pip',
            'install',
            '--disable-pip-version-check',
            '--no-input',
            '--progress-bar',
            'off',
            '--timeout',
            '60',
            '--retries',
            '2',
            '--prefer-binary',
            '--upgrade',
            f'aniworld=={ANIWORLD_VERSION}',
        ],
        timeout=420,
        thread='AniWorld thread',
    )

    render_progress(63, 'Test aniworld package')
    run_command([vpy, '-m', 'pip', 'show', 'aniworld'], timeout=60, thread='AniWorld thread')
    patch_aniworld_network_config(vpy)


def patch_aniworld_network_config(vpy: str) -> None:
    """Patch aniworld networking defaults for Windows VM compatibility.

    - Remove hardcoded DoH resolver (dns.google)
        - Keep niquests Session import unchanged to preserve constructor behavior.
    """
    if not IS_WINDOWS:
        return
    cfg_path = Path(vpy).resolve().parent.parent / 'Lib' / 'site-packages' / 'aniworld' / 'config.py'
    if not cfg_path.exists():
        return
    try:
        text = cfg_path.read_text(encoding='utf-8')
    except OSError:
        return
    patched = text
    patched = patched.replace('    resolver=["doh+google://"],\n', '')
    if patched == text:
        return
    try:
        cfg_path.write_text(patched, encoding='utf-8')
        log('WARN', 'AniWorld thread', 'Patched aniworld config: disabled DoH resolver.')
    except OSError:
        pass
    log('INFO', 'AniWorld thread', 'AniWorld environment ready')


def ensure_node_present() -> None:
    if command_exists(node_command()) and command_exists(npm_command()):
        log('INFO', 'Installer thread', 'Node.js and npm are available')
        return

    if IS_WINDOWS:
        install_node_windows()
        return

    log_error_code('Installer thread', 'NODE_MISSING', 'Node.js not found')
    raise RuntimeError('Node.js is missing. Run option 4 or install Node.js 24.x LTS manually.')


def refresh_node_path() -> None:
    """Add standard Node.js install directories to PATH so shutil.which finds them."""
    candidates = [
        r'C:\Program Files\nodejs',
        r'C:\Program Files (x86)\nodejs',
        os.path.expandvars(r'%APPDATA%\nvm\default'),
    ]

    try:
        ps = subprocess.run(
            [
                'powershell', '-NoProfile', '-Command',
                '[Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + '
                '[Environment]::GetEnvironmentVariable("PATH","User")',
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if ps.returncode == 0 and ps.stdout.strip():
            system_path = ps.stdout.strip()
            current_parts = os.environ.get('PATH', '').split(os.pathsep)
            extra_parts = [p for p in system_path.split(';') if p and p not in current_parts]
            if extra_parts:
                os.environ['PATH'] = os.pathsep.join(current_parts + extra_parts)
    except Exception:
        pass

    localappdata = os.environ.get('LOCALAPPDATA', '')
    if localappdata:
        winget_pkgs = Path(localappdata) / 'Microsoft' / 'WinGet' / 'Packages'
        if winget_pkgs.exists():
            try:
                for pkg_dir in winget_pkgs.iterdir():
                    if 'nodejs' in pkg_dir.name.lower() or 'openjs' in pkg_dir.name.lower():
                        for node_exe in pkg_dir.rglob('node.exe'):
                            candidates.append(str(node_exe.parent))
                            break
            except OSError:
                pass

    current = os.environ.get('PATH', '')
    lower = current.lower()
    additions = [p for p in candidates if Path(p).exists() and p.lower() not in lower]
    if additions:
        os.environ['PATH'] = os.pathsep.join(additions) + os.pathsep + current
        log('DEBUG', 'Installer thread', f'PATH extended with: {additions}')


def refresh_ffmpeg_path() -> None:
    candidates = [
        str((ROOT_DIR / 'tools' / 'ffmpeg' / 'bin').resolve()),
        r'C:\Program Files\ffmpeg\bin',
        r'C:\Program Files (x86)\ffmpeg\bin',
    ]

    # Winget writes new entries to the registry PATH, not to the current process
    # environment. Re-read machine + user PATH from the registry so that a
    # winget-installed FFmpeg is visible without restarting the process.
    try:
        ps = subprocess.run(
            [
                'powershell', '-NoProfile', '-Command',
                '[Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + '
                '[Environment]::GetEnvironmentVariable("PATH","User")',
            ],
            capture_output=True, text=True, timeout=15,
        )
        if ps.returncode == 0 and ps.stdout.strip():
            system_path = ps.stdout.strip()
            current_parts = os.environ.get('PATH', '').split(os.pathsep)
            extra_parts = [p for p in system_path.split(';') if p and p not in current_parts]
            if extra_parts:
                os.environ['PATH'] = os.pathsep.join(current_parts + extra_parts)
    except Exception:
        pass

    # Also probe the WinGet packages directory directly — covers the case where
    # the registry PATH update has not yet been flushed to all processes.
    localappdata = os.environ.get('LOCALAPPDATA', '')
    if localappdata:
        winget_pkgs = Path(localappdata) / 'Microsoft' / 'WinGet' / 'Packages'
        if winget_pkgs.exists():
            try:
                for pkg_dir in winget_pkgs.iterdir():
                    if 'ffmpeg' in pkg_dir.name.lower() or 'gyan' in pkg_dir.name.lower():
                        for ffmpeg_exe in pkg_dir.rglob('ffmpeg.exe'):
                            candidates.append(str(ffmpeg_exe.parent))
                            break
            except OSError:
                pass

    current = os.environ.get('PATH', '')
    lower = current.lower()
    additions = [p for p in candidates if Path(p).exists() and p.lower() not in lower]
    if additions:
        os.environ['PATH'] = os.pathsep.join(additions) + os.pathsep + current
        log('DEBUG', 'Installer thread', f'PATH extended with FFmpeg locations: {additions}')


def install_node_windows() -> None:
    log('INFO', 'Installer thread', 'Node.js missing. Starting automatic installation')
    render_progress(10, 'Install Node.js LTS automatically')

    if command_exists('winget'):
        try:
            run_command(
                [
                    'winget',
                    'install',
                    '-e',
                    '--id',
                    'OpenJS.NodeJS.LTS',
                    '--accept-package-agreements',
                    '--accept-source-agreements',
                    '--silent',
                    '--disable-interactivity',
                ],
                timeout=1800,
                thread='Installer thread',
            )
        except subprocess.CalledProcessError:
            refresh_node_path()
            if command_exists(node_command()) and command_exists(npm_command()):
                log('INFO', 'Installer thread', 'Node.js became available after winget attempt; skipping MSI fallback.')
                return
            log('WARN', 'Installer thread', 'winget install failed. Using MSI fallback.')
            install_node_msi_fallback()
    else:
        log('INFO', 'Installer thread', 'winget not found. Using MSI fallback.')
        install_node_msi_fallback()

    refresh_node_path()

    if not (command_exists(node_command()) and command_exists(npm_command())):
        log_error_code('Installer thread', 'NODE_INSTALL_FAILED', 'Node.js is not available after installation')
        raise RuntimeError('Node.js installation failed.')


def install_node_msi_fallback() -> None:
    render_progress(12, 'Download Node.js LTS installer')
    msi_path = Path(os.environ.get('TEMP', str(ROOT_DIR))) / 'aniwatch-node-lts.msi'
    # Use WebClient for the download — much faster than Invoke-WebRequest on Windows 10
    ps_download = (
        "$arch = if($env:PROCESSOR_ARCHITECTURE -eq 'ARM64'){'arm64'}"
        "elseif($env:PROCESSOR_ARCHITECTURE -eq 'x86'){'x86'}else{'x64'}; "
        "$wc = New-Object System.Net.WebClient; "
        "$json = $wc.DownloadString('https://nodejs.org/dist/index.json') | ConvertFrom-Json; "
        "$lts = $json | Where-Object { $_.lts } | Select-Object -First 1; "
        "if(-not $lts){ exit 2 }; "
        "$v = $lts.version; "
        "$url = ('https://nodejs.org/dist/{0}/node-{0}-{1}.msi' -f $v, $arch); "
        "$wc.DownloadFile($url, $env:NODE_MSI)"
    )
    env = os.environ.copy()
    env['NODE_MSI'] = str(msi_path)
    log('INFO', 'Installer thread', 'Downloading Node.js LTS MSI via WebClient')
    result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_download], env=env, timeout=600)
    if result.returncode != 0:
        raise RuntimeError('Could not download Node.js MSI')

    render_progress(15, 'Install Node.js LTS')
    # Run msiexec elevated only when not already admin
    already_admin = IS_WINDOWS and is_admin_windows()
    run_command(
        [
            'msiexec',
            '/qn',
            '/norestart',
            '/i',
            str(msi_path),
        ],
        timeout=1800,
        thread='Installer thread',
        elevated=not already_admin,
    )
    msi_path.unlink(missing_ok=True)


def install_ffmpeg_windows() -> None:
    render_progress(22, 'Install FFmpeg (Windows)')
    if command_exists('winget'):
        run_command(
            [
                'winget',
                'install',
                '-e',
                '--id',
                'Gyan.FFmpeg',
                '--accept-package-agreements',
                '--accept-source-agreements',
                '--silent',
                '--disable-interactivity',
            ],
            timeout=1800,
            thread='Installer thread',
            check=False,
        )
        refresh_ffmpeg_path()
        if command_exists('ffmpeg.exe') or command_exists('ffmpeg'):
            return

    # Fallback for systems without winget: install portable FFmpeg into project tools folder.
    render_progress(24, 'Install FFmpeg portable fallback')
    tools_root = ROOT_DIR / 'tools' / 'ffmpeg'
    zip_path = Path(os.environ.get('TEMP', str(ROOT_DIR))) / 'aniwatch-ffmpeg.zip'
    ps_download = (
        "$ProgressPreference='SilentlyContinue'; "
        "$wc = New-Object System.Net.WebClient; "
        "$wc.DownloadFile('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', $env:FFMPEG_ZIP)"
    )
    env = os.environ.copy()
    env['FFMPEG_ZIP'] = str(zip_path)
    result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_download], env=env, timeout=600)
    if result.returncode != 0:
        raise RuntimeError('Could not download FFmpeg portable package.')

    extracted = tools_root / '_extract'
    shutil.rmtree(extracted, ignore_errors=True)
    extracted.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(str(zip_path), str(extracted))
    zip_path.unlink(missing_ok=True)

    found = next(extracted.rglob('ffmpeg.exe'), None)
    if not found:
        raise RuntimeError('FFmpeg portable package did not contain ffmpeg.exe')

    target_bin = tools_root / 'bin'
    shutil.rmtree(target_bin, ignore_errors=True)
    target_bin.mkdir(parents=True, exist_ok=True)
    for item in found.parent.iterdir():
        dest = target_bin / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    shutil.rmtree(extracted, ignore_errors=True)

    refresh_ffmpeg_path()
    if not (command_exists('ffmpeg.exe') or command_exists('ffmpeg')):
        raise RuntimeError('FFmpeg installation failed (winget and portable fallback).')


def is_admin_windows() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def install_unix_tools_non_windows() -> None:
    if IS_LINUX:
        if command_exists('apt-get'):
            run_command(['sudo', 'apt-get', 'update'], timeout=900, thread='Installer thread')
            run_command(
                ['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm', 'ffmpeg', 'python3-venv'],
                timeout=1800,
                thread='Installer thread',
            )
            run_command(
                ['sudo', 'apt-get', 'install', '-y', f'python{sys.version_info.major}.{sys.version_info.minor}-venv'],
                timeout=900,
                thread='Installer thread',
                check=False,
            )
            run_command(
                ['sudo', 'apt-get', 'install', '-y', 'curl', 'jq', 'parallel', 'fzf'],
                timeout=900,
                thread='Installer thread',
                check=False,
            )
            return
        if command_exists('dnf'):
            run_command(
                ['sudo', 'dnf', 'install', '-y', 'nodejs', 'npm', 'ffmpeg'],
                timeout=1800,
                thread='Installer thread',
            )
            run_command(
                ['sudo', 'dnf', 'install', '-y', 'curl', 'jq', 'parallel', 'fzf'],
                timeout=900,
                thread='Installer thread',
                check=False,
            )
            return
        if command_exists('pacman'):
            run_command(
                ['sudo', 'pacman', '-Sy', '--noconfirm', 'nodejs', 'npm', 'ffmpeg'],
                timeout=1800,
                thread='Installer thread',
            )
            run_command(
                ['sudo', 'pacman', '-Sy', '--noconfirm', 'curl', 'jq', 'parallel', 'fzf'],
                timeout=900,
                thread='Installer thread',
                check=False,
            )
            return
        if command_exists('zypper'):
            run_command(
                ['sudo', 'zypper', '--non-interactive', 'install', 'nodejs', 'npm', 'ffmpeg'],
                timeout=1800,
                thread='Installer thread',
            )
            run_command(
                ['sudo', 'zypper', '--non-interactive', 'install', 'curl', 'jq', 'parallel', 'fzf'],
                timeout=900,
                thread='Installer thread',
                check=False,
            )
            return
        raise RuntimeError('Unsupported Linux package manager. Install dependencies manually and rerun option 4.')

    if IS_MACOS:
        if not command_exists('brew'):
            raise RuntimeError('Homebrew is required on macOS for option 4. Install Homebrew and rerun.')
        run_command(['brew', 'install', 'node', 'ffmpeg'], timeout=1800, thread='Installer thread')
        run_command(['brew', 'install', 'curl', 'jq', 'parallel', 'fzf'], timeout=900, thread='Installer thread', check=False)
        return

    raise RuntimeError(f'Unsupported operating system: {platform.system()}')


def install_or_build_aniwatch_api() -> None:
    render_progress(76, 'npm install (aniwatch-api)')
    thread = 'AniWatch API thread'

    install_commands = [
        [npm_command(), 'install'],
        [npm_command(), 'install', '--ignore-scripts'],
        ['npx', '-y', 'npm@10', 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--package-lock=false'],
    ]

    success = False
    for index, cmd in enumerate(install_commands):
        try:
            run_command(cmd, cwd=API_DIR, timeout=1800, thread=thread)
            success = True
            break
        except subprocess.CalledProcessError:
            if index == 1:
                run_command(['npx', '-y', 'npm@10', 'cache', 'clean', '--force'], cwd=API_DIR, timeout=300, thread=thread, check=False)
            node_modules = API_DIR / 'node_modules'
            lockfile = API_DIR / 'package-lock.json'
            if node_modules.exists():
                shutil.rmtree(node_modules, ignore_errors=True)
            if lockfile.exists():
                lockfile.unlink(missing_ok=True)

    if not success:
        log_error_code(thread, 'API_NPM_INSTALL_FAILED', 'All npm install recovery stages failed')
        raise RuntimeError('AniWatch API npm install failed.')

    render_progress(86, 'npm run build (aniwatch-api)')
    run_command([npm_command(), 'run', 'build'], cwd=API_DIR, timeout=900, thread=thread)


def ensure_api_runtime_artifacts() -> None:
    server_js = API_DIR / 'dist' / 'src' / 'server.js'
    node_modules = API_DIR / 'node_modules'
    if node_modules.exists() and server_js.exists():
        return
    install_or_build_aniwatch_api()


def ensure_api_running() -> None:
    ensure_api_runtime_artifacts()
    if is_port_open(ANIWATCH_API_PORT):
        log('INFO', 'AniWatch API thread', 'AniWatch API is already running on port 4000')
        return
    log('INFO', 'AniWatch API thread', 'Starting AniWatch API on port 4000')
    start_process([npm_command(), 'run', 'start'], cwd=API_DIR, title='AniWatch API')
    for _ in range(30):
        time.sleep(1)
        if is_port_open(ANIWATCH_API_PORT):
            log('INFO', 'AniWatch API thread', 'AniWatch API ready at http://localhost:4000')
            return
    raise RuntimeError('AniWatch API did not start within 30 seconds')


def ensure_download_server_running() -> None:
    if is_port_open(ANIWATCH_UI_PORT):
        log('INFO', 'AniWatch UI thread', 'AniWatch UI server is already running on port 4001')
        return
    log('INFO', 'AniWatch UI thread', 'Starting download server on port 4001')
    start_process([node_command(), 'download-server.mjs'], cwd=ROOT_DIR, title='AniWatch UI server')


def ensure_runtime_shell_dependencies() -> None:
    if IS_WINDOWS:
        refresh_ffmpeg_path()
        if not (command_exists('ffmpeg.exe') or command_exists('ffmpeg')):
            install_ffmpeg_windows()
        if not (command_exists('ffmpeg.exe') or command_exists('ffmpeg')):
            raise RuntimeError('ffmpeg is missing on Windows. Install/repair (option 4) failed.')
        return

    if not command_exists('ffmpeg'):
        raise RuntimeError('ffmpeg is missing. Run option 4 first.')


def auto_install_platform() -> None:
    render_progress(6, 'Check/install platform packages')
    if IS_WINDOWS:
        if not (command_exists(node_command()) and command_exists(npm_command())):
            install_node_windows()

        render_progress(20, 'Check native download runtime')
        refresh_ffmpeg_path()
        if not (command_exists('ffmpeg.exe') or command_exists('ffmpeg')):
            install_ffmpeg_windows()
        return

    # On non-Windows systems, package installation also covers ffmpeg/runtime.
    install_unix_tools_non_windows()


def install_repair() -> None:
    global INSTALL_UI_ENABLED
    INSTALL_UI_ENABLED = True
    log('INFO', 'Installer thread', f'Starting install/repair for OS={platform.system()}')

    try:
        render_progress(0, 'Initialize installer')
        render_progress(3, 'Check/install platform components')
        auto_install_platform()

        render_progress(30, 'Check AniWorld environment')
        ensure_aniworld()

        render_progress(72, 'Install AniWatch API')
        install_or_build_aniwatch_api()

        render_progress(97, 'Check final runtime configuration')
        ensure_runtime_shell_dependencies()

        render_progress(100, 'Done')
        log('INFO', 'Installer thread', 'Install/repair completed successfully')
    finally:
        INSTALL_UI_ENABLED = False


def start_process(
    command: list[str],
    cwd: Path,
    title: str,
    env: dict | None = None,
) -> subprocess.Popen[bytes]:
    log('INFO', 'Launcher thread', f'Starting process: {title} -> {command}')
    proc = subprocess.Popen(command, cwd=str(cwd), env=env)
    PROCESS_REGISTRY.append(proc)
    return proc


def get_certifi_bundle() -> str | None:
    """Return path to certifi's CA bundle from the venv, or None if unavailable."""
    vpy = venv_python_path()
    if not vpy.exists():
        return None
    result = subprocess.run(
        [str(vpy), '-c', 'import certifi; print(certifi.where())'],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def terminate_processes() -> None:
    for proc in reversed(PROCESS_REGISTRY):
        if proc.poll() is not None:
            continue
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
    PROCESS_REGISTRY.clear()


def open_url(url: str) -> None:
    try:
        webbrowser.open(url)
    except Exception:
        pass


def wait_for_shutdown(urls: list[str]) -> None:
    print('\nServices started:')
    for url in urls:
        print(f'  - {url}')
    print('\nPress Ctrl+C to stop all started processes.\n')
    try:
        while True:
            dead = [proc for proc in PROCESS_REGISTRY if proc.poll() is not None]
            if dead:
                codes = ', '.join(str(proc.returncode) for proc in dead)
                raise RuntimeError(f'One or more services stopped unexpectedly. Exit code(s): {codes}')
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping services...')
    finally:
        terminate_processes()


def ensure_aniworld_ready() -> None:
    vpy = venv_python_path()
    if not vpy.exists():
        log('INFO', 'AniWorld thread', 'Python venv missing. Starting automatic repair.')
        ensure_aniworld()
        return
    check = subprocess.run([str(vpy), '-m', 'pip', 'show', 'aniworld'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode != 0:
        log('WARN', 'AniWorld thread', 'AniWorld package not verified, repairing.')
        ensure_aniworld()
        return
    patch_aniworld_network_config(str(vpy))


def start_aniworld() -> None:
    ensure_aniworld_ready()
    env = os.environ.copy()
    # On Windows VMs the system cert store may be incomplete; use certifi bundle instead.
    cert_bundle = get_certifi_bundle()
    if cert_bundle:
        env['SSL_CERT_FILE'] = cert_bundle
        env['REQUESTS_CA_BUNDLE'] = cert_bundle
        log('INFO', 'AniWorld thread', f'Using certifi CA bundle: {cert_bundle}')
    start_process(
        [str(venv_python_path()), '-m', 'aniworld', '--web-ui', '--web-port', str(ANIWORLD_PORT)],
        ROOT_DIR,
        'AniWorld',
        env=env,
    )
    time.sleep(2)
    wait_for_shutdown([f'http://localhost:{ANIWORLD_PORT}'])


def start_aniwatch() -> None:
    ensure_node_present()
    ensure_runtime_shell_dependencies()
    ensure_api_running()
    ensure_download_server_running()
    time.sleep(2)
    open_url(f'http://localhost:{ANIWATCH_UI_PORT}')
    wait_for_shutdown([f'http://localhost:{ANIWATCH_UI_PORT}'])


def start_both() -> None:
    ensure_aniworld_ready()
    ensure_node_present()
    ensure_runtime_shell_dependencies()

    env = os.environ.copy()
    cert_bundle = get_certifi_bundle()
    if cert_bundle:
        env['SSL_CERT_FILE'] = cert_bundle
        env['REQUESTS_CA_BUNDLE'] = cert_bundle
    start_process(
        [str(venv_python_path()), '-m', 'aniworld', '--web-ui', '--web-port', str(ANIWORLD_PORT)],
        ROOT_DIR,
        'AniWorld',
        env=env,
    )
    ensure_api_running()
    ensure_download_server_running()
    time.sleep(2)

    open_url(f'http://localhost:{ANIWATCH_UI_PORT}')
    wait_for_shutdown([f'http://localhost:{ANIWORLD_PORT}', f'http://localhost:{ANIWATCH_UI_PORT}'])


def handle_signal(signum: int, _frame: object) -> None:
    log('INFO', 'Launcher thread', f'Received signal {signum}. Shutting down...')
    terminate_processes()
    raise SystemExit(0)


def validate_platform_support() -> None:
    if not (IS_WINDOWS or IS_LINUX or IS_MACOS):
        raise RuntimeError(
            'Unsupported OS. Supported systems are Windows 10/11, Linux, and macOS.'
        )


def main() -> int:
    validate_platform_support()
    reset_log()
    log('INFO', 'Launcher thread', f'Platform detected: {platform.system()} {platform.release()}')
    log('INFO', 'Launcher thread', f'Python version: {platform.python_version()}')

    atexit.register(terminate_processes)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print_header()

    while True:
        print_menu()
        choice = input('Selection [1-5]: ').strip()
        print()
        log('INFO', 'Launcher thread', f'Menu selection received: {choice}')
        try:
            if choice == '1':
                start_aniworld()
            elif choice == '2':
                start_aniwatch()
            elif choice == '3':
                start_both()
            elif choice == '4':
                install_repair()
            elif choice == '5':
                log('INFO', 'Launcher thread', 'Launcher session ended')
                return 0
            else:
                log('ERROR', 'Launcher thread', f'Invalid selection: {choice}')
                print('Invalid selection.\n')
        except subprocess.CalledProcessError as exc:
            log('ERROR', 'Launcher thread', f'Command failed with exit code {exc.returncode}')
            print(f'[error] Command failed with exit code {exc.returncode}.')
        except RuntimeError as exc:
            log('ERROR', 'Launcher thread', str(exc))
            print(f'[error] {exc}')
        except Exception as exc:
            log('ERROR', 'Launcher thread', f'Unexpected error: {exc}')
            print(f'[error] Unexpected error: {exc}')
        print()


if __name__ == '__main__':
    raise SystemExit(main())
