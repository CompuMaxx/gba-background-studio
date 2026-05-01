@echo off
setlocal enabledelayedexpansion
title GBA Background Studio - Wizard & Setup
color 0F

:: ======================================================
:: SECTION 1: PYTHON ENVIRONMENT CHECK
:: ======================================================
echo ======================================================
echo       CHECKING EXECUTION ENVIRONMENT...
echo ======================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit
)

:: Get Python Lib path
for /f "tokens=*" %%a in ('python -c "import sys; print(sys.prefix)"') do set "PY_PATH=%%a"

:: ======================================================
:: SECTION 2: PHYSICAL DEPENDENCY CHECK
:: ======================================================
echo Checking core libraries in: %PY_PATH%

set "MISSING="

if not exist "%PY_PATH%\Lib\site-packages\numpy" set "MISSING=1"
if not exist "%PY_PATH%\Lib\site-packages\PIL" set "MISSING=1"
if not exist "%PY_PATH%\Lib\site-packages\sklearn" set "MISSING=1"
if not exist "%PY_PATH%\Lib\site-packages\cv2" set "MISSING=1"

if defined MISSING (
    echo [INFO] Dependencies not found. Initializing installation...
    echo.
    
    python -m ensurepip --upgrade >nul 2>&1
    python -m pip install --upgrade pip
    
    echo [INFO] Installing requirements.txt...
    python -m pip install -r requirements.txt
    
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Installation failed. 
        echo Please run: pip install -r requirements.txt manually.
        pause
        exit
    )
    echo [OK] Environment successfully configured.
    timeout /t 3 >nul
) else (
    echo [OK] All core libraries detected.
)

:: ======================================================
:: SECTION 3: LANGUAGE SELECTION MENU
:: ======================================================
:MENU
cls
echo ======================================================
echo       GBA BACKGROUND STUDIO - SELECT LANGUAGE
echo ======================================================
echo.
echo  1. English             10. Polski
echo  2. Espanol             11. Tieng Viet
echo  3. Portugues (BR)      12. Bahasa Indonesia
echo  4. Francais            13. Hindi (EN Interface)
echo  5. Deutsch             14. Russian (EN Interface)
echo  6. Italiano            15. Japanese (EN Interface)
echo  7. Portugues           16. Chinese Simp. (EN Interface)
echo  8. Nederlands          17. Chinese Trad. (EN Interface)
echo  9. Turkce              18. Korean (EN Interface)
echo.
echo  0. Exit
echo.
set /p "L=Choice [1-18]: "

if "%L%"=="1"  call "scripts\convert_eng.bat"
if "%L%"=="2"  call "scripts\convert_spa.bat"
if "%L%"=="3"  call "scripts\convert_brp.bat"
if "%L%"=="4"  call "scripts\convert_fra.bat"
if "%L%"=="5"  call "scripts\convert_deu.bat"
if "%L%"=="6"  call "scripts\convert_ita.bat"
if "%L%"=="7"  call "scripts\convert_por.bat"
if "%L%"=="8"  call "scripts\convert_nld.bat"
if "%L%"=="9"  call "scripts\convert_tur.bat"
if "%L%"=="10" call "scripts\convert_pol.bat"
if "%L%"=="11" call "scripts\convert_vie.bat"
if "%L%"=="12" call "scripts\convert_ind.bat"

if "%L%" geq "13" if "%L%" leq "18" call "scripts\convert_eng.bat"

if "%L%"=="0" exit
goto MENU
