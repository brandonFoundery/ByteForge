@echo off
echo.
echo ========================================
echo   UI Style Image Protection Tool
echo ========================================
echo.
echo This tool helps protect your custom reference images
echo from being overwritten by the LLM generation system.
echo.
echo Options:
echo   1. Backup current images
echo   2. Restore from backup
echo   3. List available backups
echo   4. Exit
echo.

:menu
set /p choice="Select option (1-4): "

if "%choice%"=="1" goto backup
if "%choice%"=="2" goto restore
if "%choice%"=="3" goto list
if "%choice%"=="4" goto exit
echo Invalid choice. Please select 1-4.
goto menu

:backup
echo.
echo Backing up current images...
python backup_custom_images.py backup
echo.
pause
goto menu

:restore
echo.
echo Available backups:
python backup_custom_images.py list
echo.
set /p backup_name="Enter backup name (or 'latest' for most recent): "
python backup_custom_images.py restore %backup_name%
echo.
pause
goto menu

:list
echo.
python backup_custom_images.py list
echo.
pause
goto menu

:exit
echo.
echo Goodbye!
pause
