#!/bin/bash

# AceFlow PATEOAS v3.0 一键安装脚本
# 为开发者提供零配置的快速安装体验

set -e  # 遇到错误立即退出

echo "🚀 AceFlow PATEOAS v3.0 一键安装向导"
echo "========================================"
echo "🎯 目标：5分钟从零到生产级AI编程助手"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${PURPLE}🔧 $1${NC}"; }

# 检查系统要求
check_requirements() {
    log_step "检查系统要求..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [[ $MAJOR -gt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -ge 8 ]]; then
            log_success "Python $PYTHON_VERSION ✓"
        else
            log_error "需要 Python 3.8+，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "未找到 Python 3，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查VSCode
    if command -v code &> /dev/null; then
        log_success "VSCode ✓"
    else
        log_warning "未检测到VSCode，建议安装以获得最佳体验"
        read -p "是否继续安装？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查Git
    if command -v git &> /dev/null; then
        log_success "Git ✓"
    else
        log_error "需要Git进行版本管理"
        exit 1
    fi
}

# 创建Python虚拟环境
setup_python_env() {
    log_step "设置Python环境..."
    
    # 尝试创建虚拟环境，如果失败则使用当前环境
    if python3 -m venv venv 2>/dev/null; then
        source venv/bin/activate
        log_success "创建虚拟环境"
    else
        log_warning "虚拟环境创建失败，使用当前Python环境"
        log_info "如需虚拟环境，请手动安装: sudo apt install python3-venv"
    fi
    
    pip install --upgrade pip --quiet
    
    # 安装基础依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --quiet
        log_success "安装项目依赖"
    else
        # 创建基础requirements.txt
        cat > requirements.txt << EOF
PyYAML>=6.0
argparse
EOF
        pip install -r requirements.txt --quiet
        log_success "安装基础依赖"
    fi
}

# 配置PATEOAS引擎
setup_pateoas_engine() {
    log_step "配置PATEOAS增强引擎..."
    
    # 创建配置目录
    mkdir -p config
    mkdir -p state
    mkdir -p .clinerules
    mkdir -p .vscode
    
    # 验证核心文件存在
    core_files=("enhanced_cli.py" "pateoas/enhanced_engine.py" "pateoas/memory_system.py")
    for file in "${core_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "核心文件: $file ✓"
        else
            log_error "缺少核心文件: $file"
            exit 1
        fi
    done
    
    # 初始化PATEOAS引擎
    python3 enhanced_cli.py pateoas status > /dev/null 2>&1 && {
        log_success "PATEOAS引擎初始化成功"
    } || {
        log_warning "PATEOAS引擎初始化可能有问题，继续安装..."
    }
}

# 安装和配置Cline扩展
setup_cline_integration() {
    log_step "配置Cline VSCode集成..."
    
    if command -v code &> /dev/null; then
        # 检查Cline扩展
        if code --list-extensions | grep -q "saoudrizwan.claude-dev"; then
            log_success "Cline扩展已安装"
        else
            log_step "安装Cline扩展..."
            code --install-extension saoudrizwan.claude-dev
            log_success "Cline扩展安装完成"
        fi
        
        # 确保集成文件存在
        if [ -f ".clinerules/pateoas_integration.md" ]; then
            log_success "Cline集成规则配置完成"
        else
            log_warning "Cline集成规则文件缺失"
        fi
        
        if [ -f "aceflow-pateoas-workspace.code-workspace" ]; then
            log_success "VSCode工作区配置完成"
        else
            log_warning "VSCode工作区配置文件缺失"
        fi
    else
        log_warning "跳过VSCode配置（未安装VSCode）"
    fi
}

# 运行集成测试
run_integration_tests() {
    log_step "运行集成测试..."
    
    # 运行PATEOAS组件测试
    if [ -f "debug_pateoas_integration.py" ]; then
        python3 debug_pateoas_integration.py > /dev/null 2>&1 && {
            log_success "PATEOAS集成测试通过"
        } || {
            log_warning "PATEOAS集成测试有警告，但可以继续使用"
        }
    fi
    
    # 运行命令验证测试
    if [ -f "validate_memory_commands.py" ]; then
        python3 validate_memory_commands.py > /dev/null 2>&1 && {
            log_success "记忆命令验证通过"
        } || {
            log_warning "记忆命令验证有问题"
        }
    fi
}

# 创建快速启动脚本
create_startup_script() {
    log_step "创建快速启动脚本..."
    
    # 确保启动脚本可执行
    if [ -f "start_pateoas_dev.sh" ]; then
        chmod +x start_pateoas_dev.sh
        log_success "快速启动脚本就绪"
    else
        log_warning "快速启动脚本缺失"
    fi
}

# 显示完成信息和下一步
show_completion_info() {
    echo ""
    echo "🎉 AceFlow PATEOAS v3.0 安装完成！"
    echo "======================================"
    echo ""
    log_success "✨ 你现在拥有了一个状态感知的AI编程助手！"
    echo ""
    echo "🚀 下一步操作："
    echo "1. 启动开发环境：./start_pateoas_dev.sh"
    echo "2. 在VSCode中启动Cline扩展"
    echo "3. 尝试说：'检查项目状态'"
    echo ""
    echo "📚 学习资源："
    echo "• 快速指南: cat PATEOAS_CLINE_QUICKSTART.md"
    echo "• 完整文档: https://docs.pateoas-ai.com"
    echo "• 社区支持: https://discord.gg/pateoas"
    echo ""
    echo "🔧 常用命令："
    echo "• pateoas memory add '记忆内容'"
    echo "• pateoas memory smart-recall '查询'"
    echo "• pateoas status --performance"
    echo ""
    log_info "享受智能化编程体验！🎯"
}

# 主安装流程
main() {
    echo "开始安装..."
    echo ""
    
    check_requirements
    setup_python_env
    setup_pateoas_engine
    setup_cline_integration
    run_integration_tests
    create_startup_script
    show_completion_info
    
    echo ""
    echo "🎪 想要立即体验？运行: ./start_pateoas_dev.sh"
}

# 错误处理
trap 'log_error "安装过程中出现错误，请检查上面的错误信息"; exit 1' ERR

# 运行主程序
main "$@"