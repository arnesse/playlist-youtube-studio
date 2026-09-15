$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "[1/4] Préparation de l'environnement Python..."
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "[2/4] Récupération de FFmpeg (build Windows partagé)..."
$bin = Join-Path $Root "app\bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$ffmpegZip = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"
Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $ffmpegZip
$extract = Join-Path $env:TEMP "ffmpeg-playlist-extract"
if (Test-Path $extract) { Remove-Item -Recurse -Force $extract }
Expand-Archive -Path $ffmpegZip -DestinationPath $extract -Force
$ffmpegExe = Get-ChildItem -Path $extract -Filter ffmpeg.exe -Recurse | Select-Object -First 1
Copy-Item $ffmpegExe.FullName (Join-Path $bin "ffmpeg.exe") -Force

Write-Host "[3/4] Construction de l'exécutable..."
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed --name PlaylistYouTubeStudio --add-binary "app\bin\ffmpeg.exe;bin" app\main.py

Write-Host "[4/4] Génération de l'installeur Inno Setup..."
$iscc = $null
foreach ($candidate in @("$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe")) {
  if (Test-Path $candidate) { $iscc = $candidate; break }
}
if (-not $iscc) {
  Write-Warning "Inno Setup 6 n'est pas installé. L'exécutable est disponible dans dist\PlaylistYouTubeStudio."
  exit 0
}
& $iscc (Join-Path $Root "installer\PlaylistYouTubeStudio.iss")
Write-Host "Terminé. Installeur : dist\PlaylistYouTubeStudio-Setup.exe"
