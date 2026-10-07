@echo off
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
set "JAVA_HOME=C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot"
set "HADOOP_HOME=D:\MajorPRoject\hadoop"
set "PATH=%HADOOP_HOME%\bin;%JAVA_HOME%\bin;%PATH%"

echo Starting Retail Customer Intelligence Dashboard...
D:\MajorPRoject\.venv\Scripts\streamlit.exe run app/streamlit_app.py
pause
