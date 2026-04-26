; SYSMON Inno Setup Script
; Build with Inno Setup 6: https://jrsoftware.org/isinfo.php
; Run build.bat first to produce dist\SYSMON.exe

#define MyAppName      "SYSMON"
#define MyAppVersion   "1.0"
#define MyAppPublisher "stanc"
#define MyAppURL       ""
#define MyAppExeName   "SYSMON.exe"

[Setup]
AppId={{B3F2A1C4-8D9E-4F2A-B1C3-D4E5F6A7B8C9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=SYSMON_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Request admin privileges (required for sensor access)
PrivilegesRequired=admin
; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupentry"; Description: "Start SYSMON with Windows"; GroupDescription: "Startup"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "{#MyAppName}"; \
  ValueData: """{app}\{#MyAppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startupentry

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; \
  Flags: nowait postinstall skipifsilent
