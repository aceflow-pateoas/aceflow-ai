#!/bin/bash
# AceFlow MCP Server Build Script

set -e

echo "🚀 Building AceFlow MCP Unified Server..."

# 清理旧的构建文件
echo "🧹 Cleaning up old build files..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# 安装构建依赖
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# 构建包
echo "🔨 Building package..."
python -m build

# 检查包
echo "🔍 Checking package..."
python -m twine check dist/*

echo "✅ Build completed successfully!"
echo "📦 Package files:"
ls -la dist/

echo ""
echo "🚀 To publish to PyPI:"
echo "   python -m twine upload dist/*"
echo ""
echo "🧪 To test locally:"
echo "   pip install dist/*.whl"