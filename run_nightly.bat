@echo off
cd /d C:\credsoft

set PYTHON="C:\Program Files\Python310\python.exe"

echo [%date% %time%] nightly start >> C:\credsoft\logs\nightly.log
%PYTHON% manage.py run_nightly_services >> C:\credsoft\logs\nightly.log 2>&1
echo [%date% %time%] nightly end (exit %errorlevel%) >> C:\credsoft\logs\nightly.log