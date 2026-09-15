# Playlist YouTube Studio

Application Windows de bureau en français pour télécharger une playlist YouTube en **MP3** ou **MP4**. Les téléchargements restent sur l’ordinateur de l’utilisateur.

## Fonctionnalités

- URL de playlist YouTube publique ou accessible ;
- export audio MP3 192 kb/s ;
- export vidéo MP4 avec meilleure qualité, 1080p, 720p ou 480p ;
- choix du dossier de destination ;
- reprise des téléchargements interrompus ;
- progression et journal d’activité ;
- installateur Windows avec raccourcis Menu Démarrer et Bureau ;
- FFmpeg inclus dans le processus de build pour les conversions audio/vidéo.

## Compilation sous Windows

1. Installer Python 3.11+ et **Inno Setup 6**.
2. Ouvrir PowerShell dans ce dossier.
3. Exécuter :

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build\build_windows.ps1
```

L’installeur est créé dans `dist\PlaylistYouTubeStudio-Setup.exe`.

## Utilisation

Lancer l’application, coller le lien d’une playlist, choisir MP3 ou MP4, sélectionner la qualité et le dossier, puis cliquer sur **Démarrer le téléchargement**.

## Usage responsable

L’utilisateur est responsable du respect des conditions d’utilisation de YouTube, des droits d’auteur et des autorisations nécessaires. Utilisez l’application uniquement pour des contenus que vous avez le droit de télécharger. L’application ne contourne pas les contenus protégés par DRM et ne fournit pas de mécanisme de contournement d’accès.

## Architecture

Interface Tkinter + moteur `yt-dlp` exécuté dans un thread séparé. FFmpeg est utilisé par `yt-dlp` pour l’extraction MP3 et le muxage MP4. Le projet est fourni sous forme de code source et de scripts de build reproductibles ; la compilation de l’exécutable Windows doit être réalisée sur Windows.
