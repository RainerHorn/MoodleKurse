@echo off
setlocal EnableExtensions

REM ============================================================
REM Setzt terminal.cwd fuer alle Hermes-Agenten/Profile
REM Aufruf:
REM   set-hermes-workdir.bat "C:\Users\Horn\Projekte\Moodle-Kurse"
REM ============================================================

if "%~1"=="" (
    echo.
    echo FEHLER: Kein Arbeitsverzeichnis angegeben.
    echo.
    echo Verwendung:
    echo   %~nx0 "C:\Pfad\zum\Arbeitsverzeichnis"
    echo.
    exit /b 1
)

set "WORKDIR=%~1"

if not exist "%WORKDIR%" (
    echo.
    echo FEHLER: Das Verzeichnis existiert nicht:
    echo   %WORKDIR%
    echo.
    exit /b 2
)

where hermes >nul 2>&1
if errorlevel 1 (
    echo.
    echo FEHLER: Hermes wurde nicht im PATH gefunden.
    echo Bitte pruefen Sie die Hermes-Installation.
    echo.
    exit /b 3
)

echo.
echo ============================================================
echo Hermes Arbeitsverzeichnis setzen
echo ============================================================
echo Ziel:
echo   %WORKDIR%
echo.

for %%P in (
    orchestrator
    didaktik
    fiae
    fisi
    fidp
    vt
    quiz
    visual-designer
    reviewer
    moodle
) do (
    echo [%%P]
    hermes -p %%P config set terminal.cwd "%WORKDIR%"
    if errorlevel 1 (
        echo   FEHLER beim Setzen fuer Profil %%P
    ) else (
        echo   OK
    )
    echo.
)

echo ============================================================
echo Fertig.
echo ============================================================
echo.
echo Beispiel zum Pruefen:
echo   hermes -p orchestrator config show
echo   hermes -p moodle config show
echo.

endlocal
