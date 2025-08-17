@echo off
REM AceFlow MCP Server Build Script for Windows

echo 🚀 Building AceFlow MCP Unified Server...

REM 清理旧的构建文件
echo 🧹 Cleaning up old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM 安装构建依赖
echo 📦 Installing build dependencies...
pip install --upgrade build twine

REM 构建包
echo 🔨 Building package...
python -m build

REM 检查包
echo 🔍 Checking package...
python -m twine check dist/*

echo ✅ Build completed successfully!
echo 📦 Package files:
dir dist

echo.
echo 🚀 To publish to PyPI:
echo    python -m twine upload dist/*
echo.
echo 🧪 To test locally:
echo    pip install dist/*.whl