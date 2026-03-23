@echo off
chcp 65001 >nul
title Installation GTK3 pour WeasyPrint

echo ================================================
echo   Installation de GTK3 pour WeasyPrint
echo ================================================
echo.

REM Creer un dossier d'installation
set "INSTALL_DIR=%USERPROFILE%\gtk3"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Telechargement de GTK3...
echo.

REM Telecharger les DLLs GTK3 depuis wingtk ou autre source
set "GTK_PACKAGE_URL=https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Archive/releases/download/2021-05-17/gtk3-runtime-20210517-1.zip"

echo URL: %GTK_PACKAGE_URL%
echo.

REM Telecharger avec PowerShell
powershell -Command "Invoke-WebRequest -Uri '%GTK_PACKAGE_URL%' -OutFile '%INSTALL_DIR%\gtk3.zip'"

if exist "%INSTALL_DIR%\gtk3.zip" (
    echo Extraction...
    powershell -Command "Expand-Archive -Path '%INSTALL_DIR%\gtk3.zip' -DestinationPath '%INSTALL_DIR%' -Force"

    echo.
    echo ================================================
    echo   Configuration de l'environnement
    echo ================================================
    echo.

    REM Ajouter au PATH
    setx PATH "%PATH%;%INSTALL_DIR%\bin" /M >nul

    echo GTK3 installe dans: %INSTALL_DIR%
    echo.
    echo ATTENTION: Vous devez redemarrer votre terminal
    echo pour que les changements PATH prennent effet.
    echo.
    echo Ensuite, redemarrez l'application eS@deq.
    echo.
) else (
    echo ERREUR: Le telechargement a echoue.
    echo.
    echo Veuillez installer manuellement GTK3 depuis:
    echo https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Archive
    echo.
)

echo Appuyez sur une touche pour quitter...
pause >nul
