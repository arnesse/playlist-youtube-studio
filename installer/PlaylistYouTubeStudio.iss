#define MyAppName "Playlist YouTube Studio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Playlist YouTube Studio"
#define MyAppExeName "PlaylistYouTubeStudio.exe"

[Setup]
AppId={{7F4E0A56-9E3E-4C7A-93C7-7C76E331A8A1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Playlist YouTube Studio
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=PlaylistYouTubeStudio-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\PlaylistYouTubeStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent
