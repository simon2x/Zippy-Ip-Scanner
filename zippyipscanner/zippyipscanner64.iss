[Setup]
AppName=Zippy Ip Scanner
AppVersion=1.0.2
DefaultDirName={pf64}\Zippy Ip Scanner
DefaultGroupName=Zippy Ip Scanner
UninstallDisplayIcon={app}\zippyipscanner.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "zippyipscanner.exe"; DestDir: "{app}"; Check: IsWin64;
Source: "splash.png"; DestDir: "{app}"
Source: "images\*.png"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "zippyipscanner.ico"; DestDir: "{app}"
;Source: "icons\*.png"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "MyProg.chm"; DestDir: "{app}"
;Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\Zippy Ip Scanner"; Filename: "{app}\zippyipscanner.exe"; IconFilename: "{app}\icon.ico"

[Tasks] 
;Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked 

[Run]
;Filename: "{app}\INIT.EXE"; Parameters: "/x"
;Filename: "{app}\README.TXT"; Description: "View the README file"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\zippyipscanner.exe"; Description: "Launch Zippy Ip Scanner"; Flags: postinstall nowait skipifsilent unchecked

[UninstallDelete]
Type: files; Name: "{app}\config.json"