@echo off
chcp 65001 >nul
echo ==========================================
echo   CONFIGURAR IP ESTATICA - SERVIDOR
echo ==========================================
echo.
echo ADVERTENCIA: Ejecuta esto COMO ADMINISTRADOR
echo.

REM === VALORES DE TU RED (ipconfig) ===
set INTERFACE=Ethernet
set IP=192.168.1.50
set MASK=255.255.255.0
set GATEWAY=192.168.1.1
set DNS1=192.168.1.1
set DNS2=8.8.8.8
REM ========================================

echo Interfaz: %INTERFACE%
echo IP fija:  %IP%
echo Mascara:  %MASK%
echo Gateway:  %GATEWAY%
echo DNS:      %DNS1%, %DNS2%
echo.

pause

netsh interface ip set address name="%INTERFACE%" static %IP% %MASK% %GATEWAY% 1
netsh interface ip set dns name="%INTERFACE%" static %DNS1% primary
netsh interface ip add dns name="%INTERFACE%" %DNS2% index=2

echo.
echo IP estatica configurada.
echo Verificando...
ipconfig | findstr /C:"%IP%"
pause