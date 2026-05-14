[Setup]
AppName=Talent Acquisition Agent
AppVersion=0.1.dev0
DefaultDirName={pf}\Talent Acquisition Agent
DefaultGroupName=Talent Acquisition Agent
OutputBaseFilename=JobAgentInstaller
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "..\dist\api\api-service.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\dist\search\search-service.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\dist\web_dist\*"; DestDir: "{app}\web_dist"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "nssm.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion

[Run]
Filename: "{app}\bin\nssm.exe"; Parameters: "install JobAgent-API ""{app}\bin\api-service.exe"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "set JobAgent-API AppDirectory ""{app}"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "start JobAgent-API"; Flags: runhidden

Filename: "{app}\bin\nssm.exe"; Parameters: "install JobAgent-Search ""{app}\bin\search-service.exe"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "set JobAgent-Search AppDirectory ""{app}"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "start JobAgent-Search"; Flags: runhidden

[UninstallRun]
Filename: "{app}\bin\nssm.exe"; Parameters: "stop JobAgent-API"; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "remove JobAgent-API confirm"; Flags: runhidden

Filename: "{app}\bin\nssm.exe"; Parameters: "stop JobAgent-Search"; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "remove JobAgent-Search confirm"; Flags: runhidden
