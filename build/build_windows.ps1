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
$iscc = Get-ChildItem -Path "C:\Program Files*" -Filter ISCC.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $iscc) {
  throw "Inno Setup 6 est introuvable. Installez-le avant de lancer la compilation."
}
$dist = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $dist | Out-Null
& $iscc.FullName "/O$dist" (Join-Path $Root "installer\PlaylistYouTubeStudio.iss")
if ($LASTEXITCODE -ne 0) {
  throw "Inno Setup a échoué avec le code $LASTEXITCODE."
}
$setup = Join-Path $dist "PlaylistYouTubeStudio-Setup.exe"
if (-not (Test-Path $setup)) {
  throw "L'installeur attendu n'a pas été créé : $setup"
}
Write-Host "Terminé. Installeur : $setup"
