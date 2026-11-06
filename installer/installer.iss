#define MyAppName "MI BACK UP"
#define MyAppVersion "3.8.0"
#define MyAppExeName "MI_BACK_UP.exe"
[Setup]
AppId={{A1B2C3D4-9876-4321-ABCD-123456789001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\MI BACK UP
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=MI_BACK_UP_SETUP
ArchitecturesInstallIn64BitMode=x64
Compression=lzma
SolidCompression=yes
WizardStyle=modern
[Files]
Source: "..\dist\MI_BACK_UP.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\MI BACK UP"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\MI BACK UP"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en escritorio"; GroupDescription: "Accesos directos:"
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir MI BACK UP"; Flags: postinstall nowait skipifsilent
