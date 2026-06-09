@echo off
REM 双击或在 CMD 中运行，自动配置 Ollama + Llama3
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-ollama.ps1"
pause
