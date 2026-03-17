
@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  Anime Launcher
::  Select which tool to launch
:: ============================================================

set "SCRIPT_DIR=%~dp0"
set "API_DIR=%SCRIPT_DIR%aniwatch-api"
set "DL_SERVER=%SCRIPT_DIR%download-server.mjs"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"
set "ANIWORLD_EXE=%VENV_DIR%\Scripts\aniworld.exe"
set "ANIWORLD_VERSION=4.1.1"
set "ANIWORLD_PKG=aniworld==%ANIWORLD_VERSION%"
set "LOG_FILE=%SCRIPT_DIR%latest.log"
set "LOG_DISABLED="
set "INSTALL_UI="
set "SILENT_CONSOLE=1"

call :timestamp
powershell -NoProfile -Command "try { Set-Content -Path $env:LOG_FILE -Value ('[' + $env:TS + '] [Launcher thread/INFO]: New session started.') -Encoding UTF8; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    set "LOG_DISABLED=1"
)
call :log "INFO" "Launcher thread" "Log file reset: %LOG_FILE%"
call :log "DEBUG" "Launcher thread" "SCRIPT_DIR=%SCRIPT_DIR%"
call :log "DEBUG" "Launcher thread" "API_DIR=%API_DIR%"
call :log "DEBUG" "Launcher thread" "DL_SERVER=%DL_SERVER%"

:menu
echo.
echo  ==========================================
echo    Anime Downloader Launcher
echo  ==========================================
echo.
echo    1)  AniWorld Downloader (Ger Dub, Ger Sub)   [http://localhost:8080]
echo    2)  AniWatch Downloader (Eng Dub, Eng Sub)   [http://localhost:4001]
echo    3)  Start both
echo    4)  Install/Repair (all downloaders)
echo    5)  Exit
echo.
set /p "CHOICE=  Selection [1-5]: "
for /f "tokens=* delims= " %%A in ("!CHOICE!") do set "CHOICE=%%A"
set "CHOICE=!CHOICE: =!"
echo.
call :log "INFO" "Launcher thread" "Menu selection received: !CHOICE!"

if "!CHOICE:~0,1!"=="1" goto :start_aniworld
if "!CHOICE:~0,1!"=="2" goto :start_aniwatch
if "!CHOICE:~0,1!"=="3" goto :start_both
if "!CHOICE:~0,1!"=="4" goto :install_all
if "!CHOICE:~0,1!"=="5" goto :end
call :log "ERROR" "Launcher thread" "Invalid selection: !CHOICE!"
goto :menu

:: ?????? AniWorld only ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
:start_aniworld
call :log "INFO" "Launcher thread" "Starting flow: AniWorld only"
call :ensure_aniworld_ready
if errorlevel 1 goto :end
call :log "INFO" "AniWorld thread" "Starting AniWorld web UI on port 8080"
start "AniWorld Downloader" cmd /k ""%VENV_PY%" -m aniworld --web-ui --web-port 8080"
timeout /t 3 /nobreak >nul
call :log "INFO" "Launcher thread" "Open browser: http://localhost:8080"
start "" "http://localhost:8080"
goto :end

:: ?????? AniWatch only ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
:start_aniwatch
call :log "INFO" "Launcher thread" "Starting flow: AniWatch only"
call :ensure_node
if errorlevel 1 goto :end
call :ensure_api
if errorlevel 1 goto :end
call :start_dl_server
if errorlevel 1 goto :end
timeout /t 2 /nobreak >nul
call :log "INFO" "Launcher thread" "Open browser: http://localhost:4001"
start "" "http://localhost:4001"
goto :end

:: ?????? Both ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
:start_both
call :log "INFO" "Launcher thread" "Starting flow: both downloaders"
call :ensure_node
if errorlevel 1 goto :end
call :ensure_aniworld_ready
if errorlevel 1 goto :end
call :log "INFO" "AniWorld thread" "Starting AniWorld web UI on port 8080"
start "AniWorld Downloader" cmd /k ""%VENV_PY%" -m aniworld --web-ui --web-port 8080"
call :ensure_api
if errorlevel 1 goto :end
call :start_dl_server
if errorlevel 1 goto :end
timeout /t 2 /nobreak >nul
call :log "INFO" "Launcher thread" "Open both web UIs"
start "" "http://localhost:8080"
timeout /t 1 /nobreak >nul
start "" "http://localhost:4001"
goto :end

:: ?????? Install/Repair all required components ??????????????????????????????????????????????????????
:install_all
set "INSTALL_UI=1"
call :log "INFO" "Installer thread" "Starting install/repair"
call :render_progress 0 "Initialize installer"
call :render_progress 3 "Check/install platform components"
call :auto_install_platform
if errorlevel 1 (
    call :render_progress 100 "Aborted - see latest.log" done
    set "INSTALL_UI="
    timeout /t 2 /nobreak >nul
    goto :menu
)
call :render_progress 30 "Check AniWorld environment"
call :install_aniworld
if errorlevel 1 (
    call :render_progress 100 "Aborted - see latest.log" done
    set "INSTALL_UI="
    timeout /t 2 /nobreak >nul
    goto :menu
)
call :render_progress 65 "AniWorld ready"
call :render_progress 72 "Install AniWatch API"
call :install_aniwatch_api
if errorlevel 1 (
    call :render_progress 100 "Aborted - see latest.log" done
    set "INSTALL_UI="
    timeout /t 2 /nobreak >nul
    goto :menu
)
call :render_progress 92 "AniWatch API ready"
call :render_progress 97 "Check final WSL configuration"
call :check_wsl
if errorlevel 1 (
    call :render_progress 100 "Aborted - see latest.log" done
    set "INSTALL_UI="
    timeout /t 2 /nobreak >nul
    goto :menu
)
call :render_progress 100 "Done" done
call :log "INFO" "Installer thread" "Install/repair completed"
call :log "INFO" "Installer thread" "Then choose option 1, 2, or 3"
set "INSTALL_UI="
timeout /t 1 /nobreak >nul
goto :menu

:: ?????? Subroutine: full automatic platform bootstrap ?????????????????????????????????
:auto_install_platform
call :render_progress 6 "Check Node.js"
call :ensure_node
if errorlevel 1 (
    call :render_progress 10 "Install Node.js LTS automatically"
    call :install_node_auto
    if errorlevel 1 exit /b 1
)
call :render_progress 18 "Node.js checked"

call :render_progress 20 "Check WSL + Ubuntu"
call :ensure_wsl_ubuntu
if errorlevel 1 (
    call :render_progress 24 "Install WSL + Ubuntu automatically"
    call :install_wsl_ubuntu_auto
    if errorlevel 1 exit /b 1
)
call :render_progress 28 "WSL + Ubuntu checked"
exit /b 0

:: ?????? Subroutine: auto install Node.js with winget ?????????????????????????????????
:install_node_auto
call :log "INFO" "Installer thread" "Node.js missing. Starting automatic install via winget"
where winget >nul 2>&1
if errorlevel 1 (
    call :log "WARN" "Installer thread" "winget not found. Using MSI fallback"
    call :install_node_msi_fallback
    exit /b %errorlevel%
)
set "RUN_CMD=winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
set "RUN_TIMEOUT=1800"
set "RUN_THREAD=Installer thread"
call :run_with_timeout
if errorlevel 1 (
    call :log "WARN" "Installer thread" "Node.js install via winget failed. Using MSI fallback"
    call :install_node_msi_fallback
    exit /b %errorlevel%
)
set "PATH=%ProgramFiles%\nodejs;%PATH%"
call :ensure_node
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Node.js is not available after installation"
    exit /b 1
)
call :log "INFO" "Installer thread" "Node.js automatic installation completed"
exit /b 0

:: ?????? Subroutine: Node.js MSI fallback installer ???????????????????????????????????????
:install_node_msi_fallback
call :render_progress 12 "Download Node.js LTS installer"
call :log "INFO" "Installer thread" "Downloading Node.js LTS MSI"
set "NODE_MSI=%TEMP%\aniwatch-node-lts.msi"
powershell -NoProfile -Command "$arch = if($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } elseif($env:PROCESSOR_ARCHITECTURE -eq 'x86') { 'x86' } else { 'x64' }; $index = Invoke-RestMethod 'https://nodejs.org/dist/index.json'; $lts = $index | Where-Object { $_.lts } | Select-Object -First 1; if(-not $lts){ exit 2 }; $version = $lts.version; $url = ('https://nodejs.org/dist/{0}/node-{0}-{1}.msi' -f $version, $arch); Invoke-WebRequest -Uri $url -OutFile $env:NODE_MSI -UseBasicParsing; exit 0" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Node.js MSI download failed"
    exit /b 1
)
call :render_progress 15 "Install Node.js LTS"
call :log "INFO" "Installer thread" "Install Node.js LTS per MSI"
set "ELEV_CMD=msiexec /qn /norestart /i ""%NODE_MSI%"""
set "ELEV_TIMEOUT=1800"
set "ELEV_THREAD=Installer thread"
call :run_elevated_cmd
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Node.js MSI installation failed"
    del "%NODE_MSI%" >nul 2>&1
    exit /b 1
)
del "%NODE_MSI%" >nul 2>&1
set "PATH=%ProgramFiles%\nodejs;%PATH%"
call :ensure_node
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Node.js is not available after MSI installation"
    exit /b 1
)
call :log "INFO" "Installer thread" "Node.js MSI installation completed"
exit /b 0

:: ?????? Subroutine: verify WSL + Ubuntu distro ??????????????????????????????????????????????????????
:ensure_wsl_ubuntu
where wsl >nul 2>&1
if errorlevel 1 (
    call :log "WARN" "Installer thread" "wsl.exe not found"
    exit /b 1
)
set "HAS_UBUNTU="
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss" /s /v DistributionName > "%TEMP%\aniwatch_lxss_check.tmp" 2>nul
if not errorlevel 1 (
    findstr /I /C:"REG_SZ    Ubuntu" "%TEMP%\aniwatch_lxss_check.tmp" >nul 2>&1 && set "HAS_UBUNTU=1"
)
del "%TEMP%\aniwatch_lxss_check.tmp" >nul 2>&1
if not defined HAS_UBUNTU (
    call :log "WARN" "Installer thread" "Ubuntu distribution not found"
    exit /b 1
)
call :log "INFO" "Installer thread" "WSL + Ubuntu are available"
exit /b 0

:: ?????? Subroutine: auto install WSL + Ubuntu ?????????????????????????????????????????????????????????
:install_wsl_ubuntu_auto
call :log "INFO" "Installer thread" "Starting automatic installation of WSL + Ubuntu"
call :render_progress 22 "Enable WSL features"
call :enable_wsl_features_auto
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Could not enable WSL features"
    exit /b 1
)
call :render_progress 25 "Install Ubuntu distribution"
call :is_admin
if errorlevel 1 (
    call :log "INFO" "Installer thread" "Admin rights required - starting UAC elevation"
    set "ELEV_CMD=wsl --install -d Ubuntu --no-launch"
    set "ELEV_TIMEOUT=1800"
    set "ELEV_THREAD=Installer thread"
    call :run_elevated_cmd
) else (
    set "RUN_CMD=wsl --install -d Ubuntu --no-launch"
    set "RUN_TIMEOUT=1800"
    set "RUN_THREAD=Installer thread"
    call :run_with_timeout
)
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "WSL/Ubuntu installation failed"
    exit /b 1
)

call :ensure_wsl_ubuntu
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Ubuntu not available yet (a reboot may be required)"
    call :log "WARN" "Installer thread" "If needed: restart Windows and run option 4 again"
    exit /b 1
)
call :log "INFO" "Installer thread" "WSL + Ubuntu automatic installation completed"
exit /b 0

:: ?????? Subroutine: enable Windows WSL features automatically ??????
:enable_wsl_features_auto
call :log "INFO" "Installer thread" "Enabling Windows features for WSL"
call :is_admin
if errorlevel 1 (
    set "ELEV_CMD=dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart"
    set "ELEV_TIMEOUT=900"
    set "ELEV_THREAD=Installer thread"
    call :run_elevated_cmd
    if errorlevel 1 exit /b 1
    set "ELEV_CMD=dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart"
    set "ELEV_TIMEOUT=900"
    set "ELEV_THREAD=Installer thread"
    call :run_elevated_cmd
    if errorlevel 1 exit /b 1
) else (
    set "RUN_CMD=dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart"
    set "RUN_TIMEOUT=900"
    set "RUN_THREAD=Installer thread"
    call :run_with_timeout
    if errorlevel 1 exit /b 1
    set "RUN_CMD=dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart"
    set "RUN_TIMEOUT=900"
    set "RUN_THREAD=Installer thread"
    call :run_with_timeout
    if errorlevel 1 exit /b 1
)
call :log "INFO" "Installer thread" "Windows features for WSL are enabled"
exit /b 0

:: ?????? Subroutine: check admin rights ??????????????????????????????????????????????????????????????????????????????
:is_admin
net session >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:: ?????? Subroutine: required Windows tools ?????????????????????????????????????????????????????????????????????
:ensure_node
call :log "DEBUG" "Installer thread" "Checking Node.js and npm"
where node >nul 2>&1
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "Node.js was not found"
    call :log "WARN" "Installer thread" "Install Node.js LTS: https://nodejs.org/"
    exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
    call :log "ERROR" "Installer thread" "npm was not found"
    call :log "WARN" "Installer thread" "Install Node.js including npm: https://nodejs.org/"
    exit /b 1
)
call :log "INFO" "Installer thread" "Node.js and npm are available"
exit /b 0

:: ?????? Subroutine: install/repair AniWorld CLI in .venv ????????????????????????
:install_aniworld
if defined INSTALL_UI call :render_progress 34 "Find Python interpreter"
call :log "INFO" "AniWorld thread" "Check AniWorld environment"
set "PY_BOOTSTRAP="
:: aniworld requires windows-curses which has no Python 3.14 build ??? prefer <=3.13
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PY_BOOTSTRAP (
        py -%%V --version >nul 2>&1
        if not errorlevel 1 set "PY_BOOTSTRAP=py -%%V"
    )
)
if not defined PY_BOOTSTRAP (
    :: Only Python 3.14+ is available ??? auto-install Python 3.13 via winget
    where winget >nul 2>&1
    if not errorlevel 1 (
        call :log "INFO" "AniWorld thread" "No Python <=3.13 found. Installing Python 3.13 via winget"
        if defined INSTALL_UI call :render_progress 36 "Install Python 3.13"
        set "RUN_CMD=winget install -e --id Python.Python.3.13 --accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
        set "RUN_TIMEOUT=1800"
        set "RUN_THREAD=AniWorld thread"
        call :run_with_timeout
        py -3.13 --version >nul 2>&1
        if not errorlevel 1 set "PY_BOOTSTRAP=py -3.13"
    )
)
if not defined PY_BOOTSTRAP (
    :: Last resort: use whatever py/python is available (may be 3.14)
    where py >nul 2>&1
    if not errorlevel 1 set "PY_BOOTSTRAP=py -3"
    if not defined PY_BOOTSTRAP (
        where python >nul 2>&1
        if not errorlevel 1 set "PY_BOOTSTRAP=python"
    )
)
if not defined PY_BOOTSTRAP (
    call :log "ERROR" "AniWorld thread" "No Python interpreter found (py/python)"
    call :log_error_code "AniWorld thread" "PYTHON_NOT_FOUND" "No compatible Python interpreter available"
    call :log "WARN" "AniWorld thread" "Install Python 3 and run the .bat again"
    exit /b 1
)
call :log "DEBUG" "AniWorld thread" "Python bootstrap command: !PY_BOOTSTRAP!"

if defined INSTALL_UI call :render_progress 40 "Check .venv"
if exist "%VENV_PY%" (
    "%VENV_PY%" --version >nul 2>&1
    if errorlevel 1 (
        call :log "WARN" "AniWorld thread" "Broken .venv detected. Recreating"
        rmdir /s /q "%VENV_DIR%"
    ) else (
        :: Recreate venv if it was built with Python 3.14+ (incompatible with windows-curses/aniworld)
        for /f "tokens=2 delims= " %%V in ('"%VENV_PY%" --version 2^>^&1') do set "VENV_PYVER=%%V"
        for /f "tokens=1,2 delims=." %%A in ("!VENV_PYVER!") do (
            if "%%A" == "3" if %%B GEQ 14 (
                call :log "WARN" "AniWorld thread" "venv uses Python !VENV_PYVER! (>=3.14, incompatible). Recreating"
                rmdir /s /q "%VENV_DIR%"
            )
        )
    )
)

if not exist "%VENV_PY%" (
    if defined INSTALL_UI call :render_progress 46 "Create Python venv"
    call :log "INFO" "AniWorld thread" "Create Python venv in .venv"
    %PY_BOOTSTRAP% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "ERROR" "AniWorld thread" "Could not create .venv"
        call :log_error_code "AniWorld thread" "PYTHON_VENV_CREATE_FAILED" "venv creation failed"
        exit /b 1
    )
)

if defined INSTALL_UI call :render_progress 52 "Upgrade pip"
call :log "INFO" "AniWorld thread" "Installing/updating AniWorld CLI"
call :log "INFO" "AniWorld thread" "Upgrading pip (may take a few minutes)"
set "RUN_CMD=""%VENV_PY%"" -m pip install --disable-pip-version-check --no-input --progress-bar off --timeout 60 --retries 2 --upgrade pip"
set "RUN_TIMEOUT=600"
set "RUN_THREAD=AniWorld thread"
call :run_with_timeout
if errorlevel 1 (
    call :log "ERROR" "AniWorld thread" "pip upgrade failed"
    call :log_error_code "AniWorld thread" "PIP_UPGRADE_FAILED" "pip could not be updated"
    exit /b 1
)
if defined INSTALL_UI call :render_progress 58 "Install aniworld package"
call :log "INFO" "AniWorld thread" "Installing/updating package !ANIWORLD_PKG! (Timeout 7min)"
set "RUN_CMD=""%VENV_PY%"" -m pip install --disable-pip-version-check --no-input --progress-bar off --timeout 60 --retries 2 --prefer-binary --upgrade !ANIWORLD_PKG!"
set "RUN_TIMEOUT=420"
set "RUN_THREAD=AniWorld thread"
call :run_with_timeout
if errorlevel 1 (
    call :log "ERROR" "AniWorld thread" "Installation of package '!ANIWORLD_PKG!' failed"
    call :log_error_code "AniWorld thread" "ANIWORLD_INSTALL_FAILED" "aniworld package installation failed"
    exit /b 1
)
if defined INSTALL_UI call :render_progress 63 "Test aniworld CLI"
call :log "DEBUG" "AniWorld thread" "Checking aniworld package installation via pip show"
set "RUN_CMD=""%VENV_PY%"" -m pip show aniworld"
set "RUN_TIMEOUT=60"
set "RUN_THREAD=AniWorld thread"
call :run_with_timeout
if errorlevel 1 (
    call :log "ERROR" "AniWorld thread" "AniWorld package verification failed"
    call :log_error_code "AniWorld thread" "ANIWORLD_VERIFY_FAILED" "pip show aniworld failed"
    exit /b 1
)
call :log "INFO" "AniWorld thread" "AniWorld environment ready"
exit /b 0

:: ?????? Subroutine: ensure AniWorld is runnable ???????????????????????????????????????????????????
:ensure_aniworld_ready
if not exist "%VENV_PY%" (
    call :log "INFO" "AniWorld thread" "Python venv not found"
    call :log "INFO" "AniWorld thread" "Starting automatic repair"
    call :install_aniworld
    exit /b %errorlevel%
)
set "RUN_CMD=""%VENV_PY%"" -m pip show aniworld"
set "RUN_TIMEOUT=60"
set "RUN_THREAD=AniWorld thread"
call :run_with_timeout
if not errorlevel 1 exit /b 0
call :log "WARN" "AniWorld thread" "AniWorld package not verified, repairing"
call :log "INFO" "AniWorld thread" "Starting automatic repair"
call :install_aniworld
exit /b %errorlevel%

:: ?????? Subroutine: install dependencies + build aniwatch-api ?????????
:install_aniwatch_api
if defined INSTALL_UI call :render_progress 76 "npm install (aniwatch-api)"
call :log "INFO" "AniWatch API thread" "Installing dependencies (npm install)"
pushd "%API_DIR%"
set "NPM_INSTALL_CMD=npm install"
if not exist ".husky\install.mjs" (
    call :log "WARN" "AniWatch API thread" "Husky install script missing (.husky\\install.mjs). Skipping lifecycle scripts"
    set "NPM_INSTALL_CMD=npm install --ignore-scripts"
)
call !NPM_INSTALL_CMD! >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "WARN" "AniWatch API thread" "npm install failed, trying without lifecycle scripts"
    call npm install --ignore-scripts >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "WARN" "AniWatch API thread" "npm install still failing. Trying clean install with npm@10"
        if exist node_modules rmdir /s /q node_modules >> "%LOG_FILE%" 2>&1
        if exist package-lock.json del /f /q package-lock.json >> "%LOG_FILE%" 2>&1
        set "RUN_CMD=npx -y npm@10 install --ignore-scripts --no-audit --no-fund --package-lock=false"
        set "RUN_TIMEOUT=1800"
        set "RUN_THREAD=AniWatch API thread"
        call :run_with_timeout
        if errorlevel 1 (
            call :log "WARN" "AniWatch API thread" "npm@10 install failed. Trying npm cache clean + final install"
            set "RUN_CMD=npx -y npm@10 cache clean --force"
            set "RUN_TIMEOUT=300"
            set "RUN_THREAD=AniWatch API thread"
            call :run_with_timeout
            if exist node_modules rmdir /s /q node_modules >> "%LOG_FILE%" 2>&1
            if exist package-lock.json del /f /q package-lock.json >> "%LOG_FILE%" 2>&1
            set "RUN_CMD=npx -y npm@10 install --ignore-scripts --no-audit --no-fund --package-lock=false"
            set "RUN_TIMEOUT=1800"
            set "RUN_THREAD=AniWatch API thread"
            call :run_with_timeout
            if errorlevel 1 (
                popd
                call :log "ERROR" "AniWatch API thread" "npm install in aniwatch-api failed"
                call :log_error_code "AniWatch API thread" "API_NPM_INSTALL_FAILED" "All npm install recovery stages failed"
                exit /b 1
            )
        )
    )
)
if defined INSTALL_UI call :render_progress 86 "npm run build (aniwatch-api)"
call :log "INFO" "AniWatch API thread" "Build API (npm run build)"
call npm run build >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    popd
    call :log "ERROR" "AniWatch API thread" "npm run build in aniwatch-api failed"
    call :log_error_code "AniWatch API thread" "API_NPM_BUILD_FAILED" "TypeScript build failed"
    exit /b 1
)
popd
call :log "INFO" "AniWatch API thread" "AniWatch API is prepared"
exit /b 0

:: ?????? Subroutine: check WSL availability ?????????????????????????????????????????????????????????????????????
:check_wsl
call :log "DEBUG" "Installer thread" "Checking WSL availability"
call :ensure_wsl_ubuntu
if errorlevel 1 exit /b 1
exit /b 0

:: ?????? Subroutine: prepare api runtime artifacts ????????????????????????????????????????????????
:prepare_api_runtime
call :log "DEBUG" "AniWatch API thread" "Checking runtime artifacts for API"
if not exist "%API_DIR%\node_modules" (
    call :log "INFO" "AniWatch API thread" "node_modules missing. Starting npm install"
    pushd "%API_DIR%"
    set "NPM_INSTALL_CMD=npm install"
    if not exist ".husky\install.mjs" (
        call :log "WARN" "AniWatch API thread" "Husky install script missing (.husky\\install.mjs). Skipping lifecycle scripts"
        set "NPM_INSTALL_CMD=npm install --ignore-scripts"
    )
    call !NPM_INSTALL_CMD! >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "WARN" "AniWatch API thread" "npm install failed, trying without lifecycle scripts"
        call npm install --ignore-scripts >> "%LOG_FILE%" 2>&1
        if errorlevel 1 (
            call :log "WARN" "AniWatch API thread" "npm install still failing. Trying clean install with npm@10"
            if exist node_modules rmdir /s /q node_modules >> "%LOG_FILE%" 2>&1
            if exist package-lock.json del /f /q package-lock.json >> "%LOG_FILE%" 2>&1
            set "RUN_CMD=npx -y npm@10 install --ignore-scripts --no-audit --no-fund --package-lock=false"
            set "RUN_TIMEOUT=1800"
            set "RUN_THREAD=AniWatch API thread"
            call :run_with_timeout
            if errorlevel 1 (
                call :log "WARN" "AniWatch API thread" "npm@10 install failed. Trying npm cache clean + final install"
                set "RUN_CMD=npx -y npm@10 cache clean --force"
                set "RUN_TIMEOUT=300"
                set "RUN_THREAD=AniWatch API thread"
                call :run_with_timeout
                if exist node_modules rmdir /s /q node_modules >> "%LOG_FILE%" 2>&1
                if exist package-lock.json del /f /q package-lock.json >> "%LOG_FILE%" 2>&1
                set "RUN_CMD=npx -y npm@10 install --ignore-scripts --no-audit --no-fund --package-lock=false"
                set "RUN_TIMEOUT=1800"
                set "RUN_THREAD=AniWatch API thread"
                call :run_with_timeout
                if errorlevel 1 (
                    popd
                    call :log "ERROR" "AniWatch API thread" "npm install in aniwatch-api failed"
                    call :log_error_code "AniWatch API thread" "API_NPM_INSTALL_FAILED" "All npm install recovery stages failed"
                    exit /b 1
                )
            )
        )
    )
    popd
)
if not exist "%API_DIR%\dist\src\server.js" (
    call :log "INFO" "AniWatch API thread" "dist\\src\\server.js missing. Starting npm run build"
    pushd "%API_DIR%"
    call npm run build >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        popd
        call :log "ERROR" "AniWatch API thread" "npm run build in aniwatch-api failed"
        call :log_error_code "AniWatch API thread" "API_NPM_BUILD_FAILED" "TypeScript build failed"
        exit /b 1
    )
    popd
)
call :log "DEBUG" "AniWatch API thread" "Runtime artifacts are present"
exit /b 0

:: ?????? Subroutine: make sure aniwatch-api is running ?????????????????????????????????
:ensure_api
call :log "INFO" "AniWatch API thread" "Checking whether API is running on port 4000"
call :prepare_api_runtime
if errorlevel 1 exit /b 1
powershell -NoProfile -Command "try{$t=New-Object Net.Sockets.TcpClient('127.0.0.1',4000);$t.Close();exit 0}catch{exit 1}" >nul 2>&1
if not errorlevel 1 (
    call :log "INFO" "AniWatch API thread" "AniWatch API is already running on port 4000"
    exit /b 0
)
call :log "INFO" "AniWatch API thread" "Starting AniWatch API on port 4000"
start "AniWatch API" /D "%API_DIR%" /min cmd /k "npm run start"
call :log "DEBUG" "AniWatch API thread" "Waiting for API port check"
set /a _TRIES=0
:_api_wait
timeout /t 1 /nobreak >nul
set /a _TRIES+=1
if !_TRIES! LEQ 5 call :log "DEBUG" "AniWatch API thread" "API wait attempt !_TRIES!/30"
powershell -NoProfile -Command "try{$t=New-Object Net.Sockets.TcpClient('127.0.0.1',4000);$t.Close();exit 0}catch{exit 1}" >nul 2>&1
if not errorlevel 1 (
    call :log "INFO" "AniWatch API thread" "AniWatch API ready at http://localhost:4000"
    exit /b 0
)
if !_TRIES! GEQ 30 (
    call :log "ERROR" "AniWatch API thread" "AniWatch API did not start within 30 seconds"
    exit /b 1
)
goto :_api_wait

:: ?????? Subroutine: start the download / UI server ??????????????????????????????????????????
:start_dl_server
call :log "INFO" "AniWatch UI thread" "Checking download server prerequisites"
where node >nul 2>&1
if errorlevel 1 (
    call :log "ERROR" "AniWatch UI thread" "Node.js was not found"
    exit /b 1
)
powershell -NoProfile -Command "try{$t=New-Object Net.Sockets.TcpClient('127.0.0.1',4001);$t.Close();exit 0}catch{exit 1}" >nul 2>&1
if not errorlevel 1 (
    call :log "INFO" "AniWatch UI thread" "AniWatch UI server is already running on port 4001"
    exit /b 0
)
call :log "INFO" "AniWatch UI thread" "Starting download server on port 4001"
start "AniWatch UI" /D "%SCRIPT_DIR%" /min cmd /k "node download-server.mjs"
call :log "DEBUG" "AniWatch UI thread" "Download server started"
exit /b 0

:: ?????? Logging helper: HH:MM:SS timestamp ??????????????????????????????????????????????????????????????????
:timestamp
set "TS=%time: =0%"
set "TS=%TS:~0,8%"
exit /b 0

:: ?????? Logging helper: [time] [thread/LEVEL]: message ??????????????????????????????
:log
set "LEVEL=%~1"
set "THREAD=%~2"
set "MSG=%~3"
call :timestamp
set "LOG_LINE=[!TS!] [!THREAD!/!LEVEL!]: !MSG!"
if not defined SILENT_CONSOLE if /I not "!LEVEL!"=="DEBUG" if not defined INSTALL_UI echo [!TS!] [!THREAD!/!LEVEL!]: !MSG!
if not defined LOG_DISABLED (
    powershell -NoProfile -Command "try { Add-Content -Path $env:LOG_FILE -Value $env:LOG_LINE -Encoding UTF8; exit 0 } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 set "LOG_DISABLED=1"
)
exit /b 0

:: ?????? Logging helper: structured error code ??????????????????????????????????????????????????????
:log_error_code
set "EC_THREAD=%~1"
set "EC_CODE=%~2"
set "EC_MSG=%~3"
if defined EC_MSG (
    call :log "ERROR" "!EC_THREAD!" "ERROR_CODE=!EC_CODE! - !EC_MSG!"
) else (
    call :log "ERROR" "!EC_THREAD!" "ERROR_CODE=!EC_CODE!"
)
exit /b 0

:: ?????? Command helper with timeout and log redirection ???????????????????????????
:run_with_timeout
call :log "DEBUG" "!RUN_THREAD!" "run_with_timeout: !RUN_CMD!"
if defined LOG_DISABLED (
    powershell -NoProfile -Command "$cmd=$env:RUN_CMD; $timeout=[int]$env:RUN_TIMEOUT; $p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -WindowStyle Hidden -PassThru; if($p.WaitForExit($timeout*1000)){ exit $p.ExitCode } else { try{$p.Kill()}catch{}; exit 124 }" >nul 2>&1
) else (
    powershell -NoProfile -Command "$cmd=$env:RUN_CMD; $timeout=[int]$env:RUN_TIMEOUT; $p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -WindowStyle Hidden -PassThru; if($p.WaitForExit($timeout*1000)){ exit $p.ExitCode } else { try{$p.Kill()}catch{}; exit 124 }" >> "%LOG_FILE%" 2>&1
)
if errorlevel 124 (
    call :log "ERROR" "!RUN_THREAD!" "Timeout after !RUN_TIMEOUT! seconds"
    call :log_error_code "!RUN_THREAD!" "RUN_TIMEOUT" "run_with_timeout reached the time limit"
    exit /b 124
)
exit /b %errorlevel%

:: ?????? Elevated command helper (UAC + timeout) ????????????????????????????????????????????????
:run_elevated_cmd
call :log "DEBUG" "!ELEV_THREAD!" "run_elevated_cmd: !ELEV_CMD!"
if defined LOG_DISABLED (
    powershell -NoProfile -Command "$cmd=$env:ELEV_CMD; $timeout=[int]$env:ELEV_TIMEOUT; $p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -Verb RunAs -PassThru; if($p.WaitForExit($timeout*1000)){ exit $p.ExitCode } else { try{$p.Kill()}catch{}; exit 124 }" >nul 2>&1
) else (
    powershell -NoProfile -Command "$cmd=$env:ELEV_CMD; $timeout=[int]$env:ELEV_TIMEOUT; $p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -Verb RunAs -PassThru; if($p.WaitForExit($timeout*1000)){ exit $p.ExitCode } else { try{$p.Kill()}catch{}; exit 124 }" >> "%LOG_FILE%" 2>&1
)
if errorlevel 124 (
    call :log "ERROR" "!ELEV_THREAD!" "Timeout after !ELEV_TIMEOUT! seconds (elevated command)"
    call :log_error_code "!ELEV_THREAD!" "ELEV_TIMEOUT" "run_elevated_cmd reached the time limit"
    exit /b 124
)
exit /b %errorlevel%

:: ?????? Progress helper for installer option ????????????????????????????????????????????????????????????
:render_progress
set "PCT=%~1"
set "TXT=%~2"
set "BAR="
set "PCT_PAD=  !PCT!"
set /a FILLED=PCT*54/100
for /l %%I in (1,1,54) do (
    if %%I LEQ !FILLED! (
        set "BAR=!BAR!#"
    ) else (
        set "BAR=!BAR! "
    )
)
cls
echo  ============================================================
echo   Installation / repair in progress...
echo  ============================================================
echo.
echo   +------------------------------------------------------+
echo   ^|!BAR!^| !PCT_PAD:~-3!%%
echo   +------------------------------------------------------+
echo.
echo   Current:
echo   !TXT!
echo.
echo   Details in latest.log
if /I "%~3"=="done" echo.
call :log "INFO" "Installer thread" "Progress !PCT!%% - !TXT!"
exit /b 0

:end
call :log "INFO" "Launcher thread" "Launcher session ended"
endlocal

