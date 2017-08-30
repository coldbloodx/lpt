@echo off
start /min cmd
echo Initializing, please wait.
FOR /F "tokens=*" %%A IN ('wmic csproduct get uuid /Format:list ^| FIND "="') DO SET %%A
echo REGEDIT4 >> duiduuid.reg
echo. >> duiduuid.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\TCPIP6\Parameters] >> duiduuid.reg
echo "Dhcpv6DUID"=hex:00,04,%uuid:~0,2%,%uuid:~2,2%,%uuid:~4,2%,%uuid:~6,2%,%uuid:~9,2%,%uuid:~11,2%,%uuid:~14,2%,%uuid:~16,2%,%uuid:~19,2%,%uuid:~21,2%,%uuid:~24,2%,%uuid:~26,2%,%uuid:~28,2%,%uuid:~30,2%,%uuid:~32,2%,%uuid:~34,2% >> duiduuid.reg
echo. >> duiduuid.reg
regedit /s duiduuid.reg
for /f "delims=" %%a in ('wmic cdrom get drive ^| find ":"') do set optdrive=%%a
if not defined optdrive GOTO :netboot
set optdrive=%optdrive: =%
if not exist %optdrive%\dvdboot.cmd GOTO :netboot
call %optdrive%\dvdboot.cmd
goto :end
:netboot
wpeinit
for /f %%A IN ('getnextserver.exe') DO SET master=%%A
echo Waiting for LPT server %master% to become reachable (check WinPE network drivers if this does not proceeed)
:noping
ping -n 1 %master% 2> NUL | find "TTL=" > NUL || goto :noping
echo Waiting for successful mount of \\%master%\install (if this hangs, check that samba is running)
:nomount
net use z: \\%master%\share || goto :nomount
echo Successfully mounted \\%master%\share, moving on to execute remote script
rem for /f "delims=: tokens=2" %%c in ('ipconfig /all ^|find "Physical Address. . ."') do for /f "tokens=1" %%d in ('echo %%c') do for /f "delims=- tokens=1,2,3,4,5,6" %%m in ('echo %%d') do if "%%m.%%n" NEQ  "169.254" set NODEMAC=%%m-%%n-%%o-%%p-%%r-%%s
for /f "delims=: tokens=2" %%c in ('ipconfig /all ^|find "Physical Address. . ."') do set NODEMAC=%%c 

echo node mac: %NODEMAC%

md x:\laworks
copy /y z:\tools\wget.exe x:\laworks\
x:\laworks\wget.exe "http://%master%/cgi-bin/nodeinfo.cgi.py?mac=%NODEMAC%&status=creatingfs"

rem if exist  z:\autoinstall\%NODEMAC%.cmd copy z:\autoinstall\%NODEMAC%.cmd x:\laworks\
rem for /f "tokens=* delims= " %%i in ("%NODEMAC%") do set "NODEMAC=%%i"

rem remove spaces before/behind the mac address
rem
for /f "tokens=*" %%i in ("%NODEMAC%") do set NODEMAC=%%~nxi

copy /y z:\autoinstall\"%NODEMAC%.cmd" x:\laworks\autoscript.cmd
echo mac: "%NODEMAC%"

call x:\laworks\autoscript.cmd

x:\laworks\wget.exe "http://%master%/cgi-bin/nodeinfo.cgi.py?mac=%NODEMAC%&status=firstboot"
wpeutil reboot

:end
