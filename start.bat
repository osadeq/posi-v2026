@echo off
chcp 65001 >nul
title eS@deq - Plateforme de Positionnement

REM Ajouter GTK3 au PATH (local au script)
set "PATH=C:\Program Files\GTK3-Runtime Win64\bin;%PATH%"

echo ================================================
echo   eS@deq - Plateforme de Positionnement
echo ================================================
echo.
echo Lancement de l'application...
echo.

cd /d "%~dp0"

python app.py

echo.
echo L'application a ete fermee.
pause
