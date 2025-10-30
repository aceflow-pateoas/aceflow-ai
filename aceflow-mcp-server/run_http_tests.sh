#!/bin/bash
# AceFlow MCP HTTP 测试运行脚本

set -e

echo "🚀 AceFlow MCP HTTP 完整测试流程"
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查依赖
echo -e "${YELLOW}📋 检查依赖...${NC}"
cd /home/chenjing/AI/aceflow-ai/aceflow-mcp-server

if ! python -c "import httpx" 2>/dev/null; then
    echo -e "${YELLOW}安装 httpx...${NC}"
    pip install httpx
fi

# 启动 HTTP 服务器
echo -e "${YELLOW}🌐 启动 MCP HTTP 服务器...${NC}"
python -m aceflow_mcp_server.mcp_http_server &
SERVER_PID=$!

echo "服务器进程 PID: $SERVER_PID"

# 等待服务器启动
echo -e "${YELLOW}⏳ 等待服务器启动...${NC}"
sleep 3

# 健康检查
echo -e "${YELLOW}🔍 健康检查...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务器已就绪${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 服务器启动超时${NC}"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    echo "等待服务器启动... ($i/10)"
    sleep 2
done

# 运行测试
echo -e "${YELLOW}🧪 运行完整测试套件...${NC}"
python tests/test_mcp_http_complete.py --url http://localhost:8000 --report

TEST_EXIT_CODE=$?

# 停止服务器
echo -e "${YELLOW}🛑 停止服务器...${NC}"
kill $SERVER_PID 2>/dev/null || true

# 等待进程结束
sleep 1

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=================================="
    echo -e "🎉 所有测试通过!"
    echo -e "==================================${NC}"
else
    echo -e "${RED}=================================="
    echo -e "💥 部分测试失败"
    echo -e "==================================${NC}"
fi

exit $TEST_EXIT_CODE
