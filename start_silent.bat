@echo off
chcp 65001 >nul
title eS@deq - Serveur

REM Ajouter GTK3 au PATH (local au script)
set "PATH=C:\Program Files\GTK3-Runtime Win64\bin;%PATH%"

echo ================================================
echo   eS@deq - Demarrage automatique
echo ================================================

cd /d "%~dp0"

REM Lancer le serveur
start "eS@deq" python app.py

echo Serveur demarre sur http://localhost:5000
echo Appuyez sur une touche pour arreter le serveur...
pause

REM Arreter le serveur
taskkill /F /IM python.exe 2>nul
echo Serveur arrete.
