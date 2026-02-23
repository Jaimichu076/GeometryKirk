@echo off
echo Antes de corregir, estoy en: %cd%
pause

cd /d "%~dp0"
echo Despues de corregir, estoy en: %cd%
pause

set PERSONAJE=diddy
cd src
echo Ahora estoy en: %cd%
pause

py GEOMETRY-KIRK.py
pause
