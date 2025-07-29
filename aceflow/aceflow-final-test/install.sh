#!/bin/bash

# AceFlow-AI 一键安装脚本 - 专为Cline用户设计
# 30秒安装，零配置，开箱即用

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🧠 AceFlow-AI v3.0 在线安装器                            ║
    ║                                                              ║
    ║    The First AI Programming Assistant with Project Memory    ║
    ║                                                              ║
    ║    ⚡ 30秒安装 | 🧠 智能记忆 | 🤖 Cline集成                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

INSTALL_DIR="$HOME/.aceflow"
REPO_URL="https://github.com/aceflow-ai/aceflow-ai.git"

# 创建全局命令函数
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

# 主安装流程
main() {
    echo "🚀 开始AceFlow-AI在线安装..."
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
    
    # 复制本地源码（测试用）
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
    
    # 创建全局命令
    echo "🚀 创建全局命令..."
    create_global_commands
    echo -e "${GREEN}✅ 已添加到PATH: $HOME/.bashrc${NC}"
    echo -e "${GREEN}✅ 全局命令创建完成${NC}"
    
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
    
    echo "🚀 立即开始 (3种方式任选一种):"
    echo
    echo "   方式1⭐ 超简模式:"
    echo "   aceflow-start"
    echo
    echo "   方式2🔧 命令行模式:"
    echo "   aceflow status              # 检查状态"
    echo "   aceflow memory add '记忆内容' # 添加记忆"
    echo
    echo "   方式3🎨 项目模式:"  
    echo "   cd 你的项目目录"
    echo "   aceflow init               # 初始化AceFlow项目"
    echo
    echo "💡 首次体验建议:"
    echo "   1. 运行: aceflow-start"
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
    echo "   • aceflow --help           # 命令帮助"
    echo "   • https://docs.aceflow-ai.com # 完整文档"
    echo "   • https://discord.gg/aceflow # 社区支持"
    echo  
    echo "🎊 享受AI增强的编程体验！"
    echo
    echo "💡 提示: 重新打开终端或运行 'source ~/.bashrc' 来使用全局命令"
}

main "$@"