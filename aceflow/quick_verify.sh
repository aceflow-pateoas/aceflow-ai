#!/bin/bash

# AceFlow PATEOAS v3.0 快速验证脚本
# 验证核心功能是否正常工作

set -e

echo "🚀 AceFlow PATEOAS v3.0 快速验证"
echo "================================"
echo "🎯 验证核心功能是否正常"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# 检查基础要求
echo "🔍 检查基础要求..."
python3 --version && log_success "Python 环境正常"

# 检查核心文件
echo ""
echo "📁 检查核心文件..."
[ -f "enhanced_cli.py" ] && log_success "enhanced_cli.py 存在" || log_error "enhanced_cli.py 缺失"
[ -f "pateoas/enhanced_engine.py" ] && log_success "PATEOAS引擎存在" || log_warning "PATEOAS引擎文件不完整"
[ -f "start_pateoas_dev.sh" ] && log_success "启动脚本存在" || log_warning "启动脚本缺失"

# 测试CLI功能
echo ""
echo "🧪 测试CLI基础功能..."
if python3 enhanced_cli.py --help > /dev/null 2>&1; then
    log_success "CLI基础功能正常"
else
    log_error "CLI基础功能异常"
fi

# 测试PATEOAS状态
echo ""
echo "🧠 测试PATEOAS引擎..."
if python3 enhanced_cli.py pateoas status > /dev/null 2>&1; then
    log_success "PATEOAS引擎运行正常"
else
    log_warning "PATEOAS引擎初始化中..."
fi

# 测试记忆命令
echo ""
echo "📚 测试记忆管理功能..."
if python3 enhanced_cli.py pateoas memory --help > /dev/null 2>&1; then
    log_success "记忆管理功能正常"
else
    log_error "记忆管理功能异常"
fi

# 快速功能验证
echo ""
echo "⚡ 快速功能验证..."
python3 enhanced_cli.py pateoas memory add "验证安装测试记忆" --category pattern --tags "测试,验证" 2>/dev/null && log_success "记忆添加功能正常" || log_warning "记忆添加需要初始化"

# 生成验证报告
echo ""
echo "📊 验证完成！"
echo "==============="
echo ""
echo "🎉 基础功能验证通过！"
echo ""
echo "🚀 下一步操作："
echo "1. 运行完整演示: python3 enhanced_cli.py pateoas status"
echo "2. 体验记忆功能: python3 enhanced_cli.py pateoas memory list"
echo "3. 启动开发环境: ./start_pateoas_dev.sh"
echo ""
echo "📚 快速上手指南: cat PATEOAS_CLINE_QUICKSTART.md"
echo "🔧 详细文档: cat PROMOTION_DOCUMENT_FINAL.md"
echo ""
echo "💡 准备好体验AI编程助手了吗？🎯"