@echo off
cd /d C:\credsoft

set PYTHON="C:\Program Files\Python310\python.exe"

echo [%date% %time%] preflight start >> C:\credsoft\logs\preflight.log
%PYTHON% manage.py run_preflight >> C:\credsoft\logs\preflight.log 2>&1
echo [%date% %time%] preflight end (exit %errorlevel%) >> C:\credsoft\logs\preflight.log