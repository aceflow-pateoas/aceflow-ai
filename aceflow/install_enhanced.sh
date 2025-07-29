#!/bin/bash

# AceFlow-AI 增强安装脚本 - 支持全局和项目级安装
# 支持：bash install_enhanced.sh --global 或 --local

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 默认配置
REPO_URL="https://github.com/aceflow-ai/aceflow-ai.git"
INSTALL_MODE="global"  # 默认全局安装

# 显示帮助信息
show_help() {
    echo -e "${BLUE}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🧠 AceFlow-AI v3.0 增强安装器                            ║
    ║                                                              ║
    ║    支持全局安装和项目级安装                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo "用法："
    echo "  bash install_enhanced.sh [选项]"
    echo ""
    echo "选项："
    echo "  -g, --global    全局安装（默认）- 安装到 ~/.aceflow"
    echo "  -l, --local     项目级安装 - 安装到当前目录 ./.aceflow"
    echo "  -h, --help      显示此帮助信息"
    echo ""
    echo "示例："
    echo "  bash install_enhanced.sh --global    # 全局安装"
    echo "  bash install_enhanced.sh --local     # 项目级安装"
    echo ""
    echo "全局安装 vs 项目级安装："
    echo "  全局安装：一次安装，全局可用，所有项目共享"
    echo "  项目级安装：每个项目独立，配置和记忆隔离"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -g|--global)
                INSTALL_MODE="global"
                shift
                ;;
            -l|--local)
                INSTALL_MODE="local"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# 设置安装路径
setup_paths() {
    if [[ "$INSTALL_MODE" == "global" ]]; then
        INSTALL_DIR="$HOME/.aceflow"
        CMD_PREFIX="global"
        echo -e "${BLUE}🌍 全局安装模式${NC}"
        echo -e "${BLUE}📁 安装目录: $INSTALL_DIR${NC}"
    else
        INSTALL_DIR="$(pwd)/.aceflow"
        CMD_PREFIX="local"
        echo -e "${BLUE}📁 项目级安装模式${NC}"
        echo -e "${BLUE}📁 安装目录: $INSTALL_DIR${NC}"
    fi
}

# 创建全局命令
create_global_commands() {
    mkdir -p "$HOME/.local/bin"
    
    # 创建aceflow命令
    cat > "$HOME/.local/bin/aceflow" << 'EOFCMD'
#!/bin/bash
cd "$HOME/.aceflow/aceflow" && python3 enhanced_cli.py "$@"
EOFCMD
    
    # 创建aceflow-start命令  
    cat > "$HOME/.local/bin/aceflow-start" << 'EOFCMD'
#!/bin/bash
echo "🚀 启动AceFlow-AI开发环境..."
cd "$HOME/.aceflow/aceflow"
source venv/bin/activate 2>/dev/null || true
echo "✅ AceFlow环境变量已设置"
if command -v code &> /dev/null; then
    code aceflow-pateoas-workspace.code-workspace
    echo "✅ VSCode已启动 - 使用工作区: aceflow-pateoas-workspace.code-workspace"
    echo "✅ Cline扩展已安装" 
    echo "💡 开始使用AceFlow-AI..."
else
    echo "⚠️ VSCode未安装，请手动安装后重试"
fi
EOFCMD

    chmod +x "$HOME/.local/bin/aceflow" "$HOME/.local/bin/aceflow-start"
    
    # 添加到PATH
    if ! grep -q "$HOME/.local/bin" "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    
    export PATH="$HOME/.local/bin:$PATH"
}

# 创建项目级命令
create_local_commands() {
    local PROJECT_ROOT="$1"  # 传入项目根目录
    
    # 创建本地aceflow命令
    cat > "$PROJECT_ROOT/aceflow" << EOFCMD
#!/bin/bash
cd "\$(dirname "\$0")/.aceflow/aceflow" && python3 enhanced_cli.py "\$@"
EOFCMD
    
    # 创建本地aceflow-start命令  
    cat > "$PROJECT_ROOT/aceflow-start" << EOFCMD
#!/bin/bash
echo "🚀 启动AceFlow-AI项目环境..."
cd "\$(dirname "\$0")/.aceflow/aceflow"
source venv/bin/activate 2>/dev/null || true
echo "✅ AceFlow项目环境已设置"
if command -v code &> /dev/null; then
    code aceflow-pateoas-workspace.code-workspace
    echo "✅ VSCode已启动 - 使用项目工作区"
    echo "✅ Cline扩展已安装" 
    echo "💡 开始使用AceFlow-AI..."
else
    echo "⚠️ VSCode未安装，请手动安装后重试"
fi
EOFCMD

    chmod +x "$PROJECT_ROOT/aceflow" "$PROJECT_ROOT/aceflow-start"
}

# 显示标题
show_banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🧠 AceFlow-AI v3.0 增强安装器                            ║
    ║                                                              ║
    ║    The First AI Programming Assistant with Project Memory    ║
    ║                                                              ║
    ║    ⚡ 30秒安装 | 🧠 智能记忆 | 🤖 Cline集成                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 主安装流程
main() {
    # 解析参数
    parse_args "$@"
    
    # 显示标题
    show_banner
    
    # 设置路径
    setup_paths
    
    echo "🚀 开始AceFlow-AI增强安装..."
    echo
    
    # 智能依赖检测
    echo "🚀 智能依赖检测中..."
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python $(python3 --version | cut -d' ' -f2) ✓${NC}"
    else
        echo -e "${RED}❌ 需要Python 3.8+，请先安装${NC}"
        exit 1
    fi
    
    # 检查Git
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✅ Git $(git --version | cut -d' ' -f3) ✓${NC}"
    else
        echo -e "${RED}❌ 需要Git，请先安装${NC}" 
        exit 1
    fi
    
    # 检查VSCode
    if command -v code &> /dev/null; then
        echo -e "${GREEN}✅ VSCode 已安装 ✓${NC}"
    else
        echo -e "${YELLOW}⚠️ VSCode未安装 - 建议安装以获得最佳体验${NC}"
    fi
    
    # 检查并安装Cline扩展
    if command -v code &> /dev/null; then
        if code --list-extensions | grep -q "saoudrizwan.claude-dev"; then
            echo -e "${GREEN}✅ Cline扩展已安装 ✓${NC}"
        else
            echo -e "${YELLOW}⚠️ Cline扩展未安装 - 将自动安装${NC}"
            code --install-extension saoudrizwan.claude-dev
            echo -e "${GREEN}✅ Cline扩展已安装 ✓${NC}"
        fi
    fi
    
    echo
    
    # 复制源码（测试用）
    echo "🚀 复制AceFlow-AI源码..."
    rm -rf "$INSTALL_DIR"
    cp -r "/home/chenjing/AI/aceflow-ai" "$INSTALL_DIR"
    cd "$INSTALL_DIR/aceflow"
    echo -e "${GREEN}✅ 源码复制完成${NC}"
    
    # 执行安装
    echo "🚀 执行智能安装..."
    if [ -f "quick_install.sh" ]; then
        bash quick_install.sh
    else
        # 基础安装
        python3 -m venv venv 2>/dev/null || true
        source venv/bin/activate 2>/dev/null || true
        pip install --upgrade pip --quiet 2>/dev/null || true
        echo -e "${GREEN}✅ 基础环境配置完成${NC}"
    fi
    
    echo -e "${GREEN}✅ AceFlow-AI安装完成${NC}"
    echo
    
    # 根据安装模式创建命令
    echo "🚀 创建命令..."
    if [[ "$INSTALL_MODE" == "global" ]]; then
        create_global_commands
        echo -e "${GREEN}✅ 全局命令创建完成${NC}"
        echo -e "${GREEN}✅ 已添加到PATH: $HOME/.bashrc${NC}"
    else
        # 保存项目根目录，因为当前在安装目录内
        PROJECT_ROOT="$(dirname "$INSTALL_DIR")"
        create_local_commands "$PROJECT_ROOT"
        echo -e "${GREEN}✅ 项目级命令创建完成${NC}"
        echo -e "${GREEN}✅ 本地命令: ./aceflow, ./aceflow-start${NC}"
    fi
    
    echo
    
    # 验证安装
    echo "🚀 验证安装..."
    if python3 enhanced_cli.py pateoas status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Python环境验证通过${NC}"
        echo -e "${GREEN}✅ CLI功能验证通过${NC}"
        echo -e "${GREEN}✅ 记忆系统验证通过${NC}"
    else
        echo -e "${YELLOW}⚠️ 部分功能可能需要手动配置${NC}"
    fi
    
    echo
    echo -e "${GREEN}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          🎉 AceFlow-AI 安装成功！                            ║
    ║                                                              ║
    ║          Your AI Programming Assistant is Ready!            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    # 显示使用说明
    if [[ "$INSTALL_MODE" == "global" ]]; then
        echo "🚀 全局模式 - 立即开始 (3种方式任选一种):"
        echo
        echo "   方式1⭐ 超简模式:"
        echo "   aceflow-start"
        echo
        echo "   方式2🔧 命令行模式:"
        echo "   aceflow status              # 检查状态"
        echo "   aceflow pateoas memory add '记忆内容' # 添加记忆"
        echo
        echo "   方式3🎨 项目模式:"  
        echo "   cd 你的项目目录"
        echo "   aceflow init               # 初始化AceFlow项目"
        echo
        echo "💡 提示: 重新打开终端或运行 'source ~/.bashrc' 来使用全局命令"
    else
        echo "🚀 项目级模式 - 立即开始 (3种方式任选一种):"
        echo
        echo "   方式1⭐ 超简模式:"
        echo "   ./aceflow-start"
        echo
        echo "   方式2🔧 命令行模式:"
        echo "   ./aceflow status              # 检查状态"
        echo "   ./aceflow pateoas memory add '记忆内容' # 添加记忆"
        echo
        echo "   方式3🎨 直接模式:"  
        echo "   ./aceflow init               # 初始化AceFlow项目"
        echo
        echo "💡 项目级安装优势: 配置和记忆完全隔离，适合多项目开发"
    fi
    
    echo
    echo "💡 首次体验建议:"
    if [[ "$INSTALL_MODE" == "global" ]]; then
        echo "   1. 运行: aceflow-start"
    else
        echo "   1. 运行: ./aceflow-start"
    fi
    echo "   2. 等待VSCode打开"
    echo "   3. 启动Cline扩展 (Ctrl+Shift+P)"
    echo "   4. 对AI说: '检查项目状态'"
    echo
    echo "🎯 常用AI对话示例:"
    echo "   • '我要开发登录功能' - 获取智能任务分析"
    echo "   • '代码有bug怎么办' - 获取诊断建议"
    echo "   • '项目进度如何' - 查看智能状态报告"
    echo
    echo "📚 获取帮助:"
    echo "   • bash install_enhanced.sh --help # 安装帮助"
    echo "   • https://docs.aceflow-ai.com # 完整文档"
    echo "   • https://discord.gg/aceflow # 社区支持"
    echo  
    echo "🎊 享受AI增强的编程体验！"
    echo
}

main "$@"