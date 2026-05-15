@echo off
title Wanderlust Travel App

:: Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.10 or later from https://www.python.org/downloads/
    echo Make sure to tick "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Install any dependencies (safe to run even if none needed)
pip install -r requirements.txt --quiet

:: Launch the app
python wanderlust_app.py
