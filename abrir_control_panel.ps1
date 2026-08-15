$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 8501
$url = "http://localhost:$port"
$python = Join-Path $root "env\Scripts\python.exe"
$stdout = Join-Path $root "streamlit_control_plane.out.log"
$stderr = Join-Path $root "streamlit_control_plane.err.log"

if (-not (Test-Path -LiteralPath $python)) {
    throw "No se encontro el Python del entorno virtual: $python"
}

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue

if (-not $listener) {
    Start-Process `
        -FilePath $python `
        -ArgumentList @("-m", "streamlit", "run", "control_plane.py", "--server.port", "$port", "--server.headless", "true") `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr

    Start-Sleep -Seconds 5
}

$programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
$edgeCandidates = @(
    (Join-Path $programFilesX86 "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe")
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$edge = $edgeCandidates | Select-Object -First 1

if ($edge) {
    Start-Process -FilePath $edge -ArgumentList @("--app=$url", "--window-size=1320,860")
} else {
    Start-Process $url
}

