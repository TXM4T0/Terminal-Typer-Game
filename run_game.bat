@echo off
title TERMINAL TYPER: BATTLE PROTOCOL
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
mode con: cols=80 lines=30
python main.py
pause
