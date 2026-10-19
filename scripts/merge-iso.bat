@echo off
REM Merge Origo full-ISO parts into a single .iso (Windows).
REM Place this file next to origo-v0.1-full-amd64.part00, .part01, ...
setlocal enabledelayedexpansion
cd /d "%~dp0"

set OUT=origo-v0.1-full-amd64.iso
if exist "%OUT%" del "%OUT%"
set FIRST=1
for %%f in (origo-v0.1-full-amd64.part*) do (
  if "!FIRST!"=="1" (
    copy /b "%%f" "%OUT%" >nul
    set FIRST=0
  ) else (
    copy /b "%OUT%"+"%%f" "%OUT%" >nul
  )
  echo added %%f
)
if "!FIRST!"=="1" (
  echo No parts found. Put origo-v0.1-full-amd64.part00 / .part01 next to this script.
  pause
  exit /b 1
)
echo Done: %OUT%
pause
