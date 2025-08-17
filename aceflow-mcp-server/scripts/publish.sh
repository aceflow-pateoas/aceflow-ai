#!/bin/bash
# AceFlow MCP Server Publish Script

set -e

echo "🚀 Publishing AceFlow MCP Unified Server to PyPI..."

# 检查是否有构建文件
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ No build files found. Running build first..."
    ./scripts/build.sh
fi

# 检查环境变量
if [ -z "$TWINE_USERNAME" ] && [ -z "$TWINE_PASSWORD" ]; then
    echo "⚠️ TWINE_USERNAME and TWINE_PASSWORD not set."
    echo "Please set them or use: python -m twine upload dist/*"
    exit 1
fi

# 发布到 PyPI
echo "📤 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Successfully published to PyPI!"
echo "🎉 Package is now available: pip install aceflow-mcp-server"