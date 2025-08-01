#!/bin/bash

# AceFlow v3.0 全局安装脚本
# 实施方案3: 全局安装初始化脚本，项目级拷贝工作脚本

set -e

# 脚本信息
SCRIPT_NAME="global-install.sh"
VERSION="3.0.0"
ACEFLOW_HOME="$(dirname $(dirname $(realpath $0)))"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}
╔══════════════════════════════════════╗
║       AceFlow v3.0 全局安装          ║
║        方案3: 混合部署模式           ║ 
╚══════════════════════════════════════╝${NC}"
}

# 帮助信息
show_help() {
    cat << EOF
AceFlow v3.0 全局安装脚本 - 方案3实施

用法: $SCRIPT_NAME [选项]

选项:
  --user-install       安装到用户PATH (推荐)
  --system-install     安装到系统PATH (需要sudo)
  --uninstall          卸载已安装的脚本
  --check              检查安装状态
  -h, --help           显示此帮助信息
  -v, --version        显示版本信息

方案3说明:
  全局脚本: aceflow-init.sh (项目初始化)
  项目脚本: aceflow-stage.sh, aceflow-validate.sh, aceflow-templates.sh
  
安装位置:
  用户安装: ~/.local/bin/ (无需sudo)
  系统安装: /usr/local/bin/ (需要sudo)

示例:
  $SCRIPT_NAME --user-install
  $SCRIPT_NAME --check
  $SCRIPT_NAME --uninstall

EOF
}

# 检查安装状态
check_installation() {
    log_info "检查AceFlow安装状态..."
    
    local global_script="aceflow-init.sh"
    local installed_path=""
    
    if command -v "$global_script" &> /dev/null; then
        installed_path=$(which "$global_script")
        log_success "✅ 全局脚本已安装: $installed_path"
        
        # 检查版本
        local installed_version=$("$global_script" --version 2>/dev/null | grep -o "v[0-9.]*" || echo "unknown")
        echo "   版本: $installed_version"
    else
        log_warning "❌ 全局脚本未安装"
    fi
    
    # 检查项目级脚本（在当前目录）
    local project_scripts=("aceflow-stage.sh" "aceflow-validate.sh" "aceflow-templates.sh")
    local found_count=0
    
    log_info "检查当前目录的项目级脚本..."
    for script in "${project_scripts[@]}"; do
        if [ -f "./$script" ]; then
            log_success "✅ 项目脚本存在: $script"
            ((found_count++))
        else
            log_warning "❌ 项目脚本缺失: $script"
        fi
    done
    
    echo ""
    if command -v "$global_script" &> /dev/null; then
        echo -e "${GREEN}全局安装状态: 已安装${NC}"
    else
        echo -e "${RED}全局安装状态: 未安装${NC}"
    fi
    
    echo -e "${BLUE}项目脚本状态: $found_count/3 已安装${NC}"
}

# 用户级安装
user_install() {
    log_info "开始用户级安装..."
    
    local user_bin="$HOME/.local/bin"
    
    # 创建用户bin目录
    mkdir -p "$user_bin"
    
    # 安装全局脚本
    local global_script="aceflow-init.sh"
    log_info "安装全局脚本: $global_script"
    
    cp "$ACEFLOW_HOME/$global_script" "$user_bin/"
    chmod +x "$user_bin/$global_script"
    
    # 检查PATH
    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
        log_warning "⚠️  $user_bin 不在PATH中"
        echo "请将以下行添加到 ~/.bashrc 或 ~/.zshrc:"
        echo "export PATH=\"\$PATH:\$HOME/.local/bin\""
        echo ""
        echo "然后运行: source ~/.bashrc (或 source ~/.zshrc)"
    fi
    
    log_success "✅ 用户级安装完成"
    echo "   安装位置: $user_bin/$global_script"
}

# 系统级安装
system_install() {
    log_info "开始系统级安装..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "系统级安装需要sudo权限"
        echo "请使用: sudo $0 --system-install"
        exit 1
    fi
    
    local system_bin="/usr/local/bin"
    
    # 安装全局脚本
    local global_script="aceflow-init.sh"
    log_info "安装全局脚本: $global_script"
    
    cp "$ACEFLOW_HOME/$global_script" "$system_bin/"
    chmod +x "$system_bin/$global_script"
    
    log_success "✅ 系统级安装完成"
    echo "   安装位置: $system_bin/$global_script"
}

# 卸载
uninstall() {
    log_info "开始卸载AceFlow..."
    
    local global_script="aceflow-init.sh"
    local removed_count=0
    
    # 卸载用户级
    local user_bin="$HOME/.local/bin"
    if [ -f "$user_bin/$global_script" ]; then
        rm -f "$user_bin/$global_script"
        log_success "✅ 已删除用户级脚本: $user_bin/$global_script"
        ((removed_count++))
    fi
    
    # 卸载系统级（需要权限）
    local system_bin="/usr/local/bin"
    if [ -f "$system_bin/$global_script" ]; then
        if [ "$EUID" -eq 0 ]; then
            rm -f "$system_bin/$global_script"
            log_success "✅ 已删除系统级脚本: $system_bin/$global_script"
            ((removed_count++))
        else
            log_warning "⚠️  需要sudo权限删除系统级脚本: $system_bin/$global_script"
            echo "请运行: sudo rm -f $system_bin/$global_script"
        fi
    fi
    
    if [ $removed_count -eq 0 ]; then
        log_warning "❌ 未找到已安装的脚本"
    else
        log_success "✅ 卸载完成，共删除 $removed_count 个脚本"
    fi
}

# 主函数
main() {
    local action=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --user-install)
                action="user_install"
                shift
                ;;
            --system-install)
                action="system_install"
                shift
                ;;
            --uninstall)
                action="uninstall"
                shift
                ;;
            --check)
                action="check"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "AceFlow Global Install v$VERSION"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示标题
    log_header
    
    # 执行操作
    case $action in
        "user_install")
            user_install
            ;;
        "system_install")
            system_install
            ;;
        "uninstall")
            uninstall
            ;;
        "check"|"")
            check_installation
            ;;
        *)
            log_error "无效操作"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"