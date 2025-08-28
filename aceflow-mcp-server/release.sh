#!/usr/bin/env bash

# AceFlow MCP Server 发布脚本
# 用于自动化构建和发布到 PyPI

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AceFlow MCP Server v2.0 发布流程${NC}"
echo "============================================"

# 1. 环境检查
echo -e "\n${YELLOW}📋 步骤 1: 环境检查${NC}"
echo "检查必要的工具..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 未安装${NC}"
    exit 1
fi
echo "✅ pip3: $(pip3 --version)"

# 安装/检查构建工具
echo "安装构建工具..."
pip3 install --upgrade build twine setuptools wheel

# 2. 清理旧构建文件
echo -e "\n${YELLOW}🧹 步骤 2: 清理旧文件${NC}"
echo "清理 dist/ 和 build/ 目录..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/
echo "✅ 清理完成"

# 3. 运行测试
echo -e "\n${YELLOW}🧪 步骤 3: 运行测试${NC}"
echo "运行系统集成测试..."

python3 -c "
# 快速集成测试
try:
    from aceflow_mcp_server.unified_tools import SimplifiedUnifiedTools
    from aceflow_mcp_server.data_manager import DataManager
    
    print('测试工具导入...', end=' ')
    tools = SimplifiedUnifiedTools()
    print('✅')
    
    print('测试数据管理...', end=' ')
    dm = DataManager()
    print('✅')
    
    print('测试基础功能...', end=' ')
    result = tools.aceflow_stage(action='status')
    assert result['success'] == True
    print('✅')
    
    print('✅ 所有测试通过')
    
except Exception as e:
    print(f'❌ 测试失败: {e}')
    exit(1)
"

# 4. 构建包
echo -e "\n${YELLOW}📦 步骤 4: 构建包${NC}"
echo "构建 wheel 和 source distribution..."
python3 -m build
echo "✅ 构建完成"

# 5. 检查包内容
echo -e "\n${YELLOW}🔍 步骤 5: 包内容检查${NC}"
echo "检查构建的包..."

# 列出生成的文件
echo "生成的文件:"
ls -la dist/

# 检查包内容
echo -e "\n检查包内容:"
twine check dist/*
echo "✅ 包检查通过"

# 6. 测试安装
echo -e "\n${YELLOW}🔧 步骤 6: 测试安装${NC}"
echo "在虚拟环境中测试安装..."

# 创建临时虚拟环境测试
TEMP_VENV=$(mktemp -d)/test_venv
python3 -m venv $TEMP_VENV
source $TEMP_VENV/bin/activate

echo "安装构建的包..."
pip install dist/*.whl

echo "测试导入..."
python -c "
import aceflow_mcp_server
from aceflow_mcp_server.unified_tools import SimplifiedUnifiedTools
print('✅ 包安装和导入测试通过')
"

# 清理测试环境
deactivate
rm -rf $(dirname $TEMP_VENV)

# 7. 发布选项
echo -e "\n${YELLOW}🚀 步骤 7: 发布选项${NC}"
echo "选择发布目标:"
echo "1) Test PyPI (推荐先测试)"
echo "2) 正式 PyPI"
echo "3) 跳过发布"

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo -e "\n${BLUE}📤 发布到 Test PyPI...${NC}"
        echo "请确保已配置 Test PyPI 令牌"
        twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        echo -e "\n${GREEN}✅ 发布到 Test PyPI 完成!${NC}"
        echo -e "测试安装命令: ${YELLOW}pip install -i https://test.pypi.org/simple/ aceflow-mcp-server${NC}"
        ;;
    2)
        echo -e "\n${BLUE}📤 发布到正式 PyPI...${NC}"
        read -p "确认发布到正式 PyPI? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo "请确保已配置 PyPI 令牌"
            twine upload dist/*
            echo -e "\n${GREEN}🎉 发布到 PyPI 完成!${NC}"
            echo -e "安装命令: ${YELLOW}pip install aceflow-mcp-server${NC}"
        else
            echo "取消发布"
        fi
        ;;
    3)
        echo "跳过发布"
        ;;
    *)
        echo "无效选择"
        ;;
esac

# 8. 发布后验证
if [[ $choice == "1" || $choice == "2" ]]; then
    echo -e "\n${YELLOW}✅ 步骤 8: 发布后验证${NC}"
    echo "等待 30 秒后进行验证..."
    sleep 30
    
    if [[ $choice == "1" ]]; then
        INSTALL_CMD="pip install -i https://test.pypi.org/simple/ aceflow-mcp-server==2.0.0"
    else
        INSTALL_CMD="pip install aceflow-mcp-server==2.0.0"
    fi
    
    echo "创建验证环境..."
    VERIFY_VENV=$(mktemp -d)/verify_venv
    python3 -m venv $VERIFY_VENV
    source $VERIFY_VENV/bin/activate
    
    echo "从 PyPI 安装..."
    eval $INSTALL_CMD
    
    echo "验证安装..."
    python -c "
from aceflow_mcp_server.unified_tools import SimplifiedUnifiedTools
tools = SimplifiedUnifiedTools()
result = tools.aceflow_stage(action='status')
print('✅ PyPI 包验证成功')
print(f'版本: {result.get(\"version\", \"N/A\")}')
"
    
    deactivate
    rm -rf $(dirname $VERIFY_VENV)
fi

echo -e "\n${GREEN}🎉 AceFlow MCP Server v2.0 发布流程完成!${NC}"
echo "============================================"

if [[ $choice == "2" ]]; then
    echo -e "\n${BLUE}📚 用户安装指南:${NC}"
    echo "用户现在可以通过以下方式安装:"
    echo -e "${YELLOW}pip install aceflow-mcp-server${NC}"
    echo ""
    echo "Cursor 集成配置:"
    echo '{
  "mcpServers": {
    "aceflow": {
      "command": "python",
      "args": ["-m", "aceflow_mcp_server.mcp_stdio_server"],
      "cwd": "/path/to/project"
    }
  }
}'
fi

echo -e "\n${GREEN}感谢使用 AceFlow MCP Server! 🚀${NC}"