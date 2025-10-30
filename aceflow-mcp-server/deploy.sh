#!/bin/bash
# AceFlow MCP Server 快速部署脚本
# 用于内网环境一键部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
AceFlow MCP Server 部署脚本

用法:
    $0 [命令] [选项]

命令:
    docker          使用 Docker 部署
    compose         使用 Docker Compose 部署
    pyinstaller     打包为可执行文件
    venv            创建虚拟环境部署
    test            运行测试验证
    clean           清理部署环境
    help            显示此帮助信息

选项:
    --port PORT     指定服务端口 (默认: 8000)
    --host HOST     指定监听地址 (默认: 0.0.0.0)
    --build         构建镜像 (Docker/Compose)
    --export        导出镜像用于内网传输 (Docker)

示例:
    $0 docker --build --export          # 构建并导出Docker镜像
    $0 compose                          # 使用Docker Compose启动
    $0 pyinstaller                      # 打包为可执行文件
    $0 test                             # 运行测试
EOF
}

# Docker 部署
deploy_docker() {
    print_info "开始 Docker 部署..."

    # 检查 Docker
    check_command docker

    local BUILD=false
    local EXPORT=false
    local PORT=8000
    local HOST="0.0.0.0"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                BUILD=true
                shift
                ;;
            --export)
                EXPORT=true
                shift
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --host)
                HOST="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    # 构建镜像
    if [ "$BUILD" = true ]; then
        print_info "构建 Docker 镜像..."
        docker build -t aceflow-mcp-server:2.2.0 -f Dockerfile .
        print_success "镜像构建完成"
    fi

    # 导出镜像
    if [ "$EXPORT" = true ]; then
        print_info "导出 Docker 镜像..."
        docker save aceflow-mcp-server:2.2.0 -o aceflow-mcp-server-2.2.0.tar
        print_success "镜像已导出到: aceflow-mcp-server-2.2.0.tar"
        print_info "镜像大小: $(du -h aceflow-mcp-server-2.2.0.tar | cut -f1)"
    fi

    # 停止旧容器
    if docker ps -a | grep -q aceflow-mcp; then
        print_info "停止旧容器..."
        docker stop aceflow-mcp 2>/dev/null || true
        docker rm aceflow-mcp 2>/dev/null || true
    fi

    # 启动容器
    print_info "启动容器..."
    docker run -d \
        --name aceflow-mcp \
        -p ${PORT}:8000 \
        -v $(pwd)/workspace:/workspace \
        -e ACEFLOW_HOST=${HOST} \
        -e ACEFLOW_PORT=8000 \
        --restart unless-stopped \
        aceflow-mcp-server:2.2.0

    print_success "容器启动成功"

    # 等待服务就绪
    print_info "等待服务启动..."
    sleep 5

    # 健康检查
    if curl -s http://localhost:${PORT}/health > /dev/null; then
        print_success "服务运行正常"
        print_info "访问地址: http://localhost:${PORT}"
        print_info "健康检查: http://localhost:${PORT}/health"
        print_info "MCP 端点: http://localhost:${PORT}/mcp"
    else
        print_error "服务启动失败，请检查日志: docker logs aceflow-mcp"
        exit 1
    fi
}

# Docker Compose 部署
deploy_compose() {
    print_info "开始 Docker Compose 部署..."

    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi

    local BUILD=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                BUILD="--build"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    # 创建必要的目录
    mkdir -p workspace logs

    # 启动服务
    print_info "启动服务..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d $BUILD
    else
        docker compose up -d $BUILD
    fi

    print_success "服务启动成功"

    # 显示服务状态
    print_info "服务状态:"
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi

    # 健康检查
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "服务运行正常"
        print_info "访问地址: http://localhost:8000"
    else
        print_warning "服务可能未完全启动，请检查: docker-compose logs"
    fi
}

# PyInstaller 打包
deploy_pyinstaller() {
    print_info "开始 PyInstaller 打包..."

    # 检查 Python
    check_command python3

    # 安装 PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_info "安装 PyInstaller..."
        pip install pyinstaller
    fi

    # 创建打包配置
    print_info "创建打包配置..."
    cat > aceflow-mcp-server.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['aceflow_mcp_server/mcp_http_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('aceflow_mcp_server', 'aceflow_mcp_server'),
    ],
    hiddenimports=[
        'aceflow_mcp_server.tools',
        'aceflow_mcp_server.config',
        'aceflow_mcp_server.mcp_output_adapter',
        'aceflow_mcp_server.tool_prompts',
        'uvicorn',
        'fastapi',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aceflow-mcp-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

    # 执行打包
    print_info "执行打包..."
    pyinstaller aceflow-mcp-server.spec

    if [ -f dist/aceflow-mcp-server ]; then
        print_success "打包完成"
        print_info "可执行文件: dist/aceflow-mcp-server"
        print_info "文件大小: $(du -h dist/aceflow-mcp-server | cut -f1)"
        print_info "运行方式: ./dist/aceflow-mcp-server"
    else
        print_error "打包失败"
        exit 1
    fi
}

# 虚拟环境部署
deploy_venv() {
    print_info "开始虚拟环境部署..."

    # 检查 Python
    check_command python3

    # 创建虚拟环境
    if [ ! -d "aceflow-venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv aceflow-venv
    fi

    # 激活虚拟环境
    source aceflow-venv/bin/activate

    # 安装依赖
    print_info "安装依赖..."
    pip install --upgrade pip
    pip install -e .

    print_success "虚拟环境部署完成"
    print_info "激活命令: source aceflow-venv/bin/activate"
    print_info "启动服务: python -m aceflow_mcp_server.mcp_http_server"

    # 可选：打包虚拟环境
    read -p "是否打包虚拟环境用于内网传输？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "打包虚拟环境..."
        tar -czf aceflow-mcp-bundle.tar.gz \
            aceflow-venv/ \
            aceflow_mcp_server/ \
            pyproject.toml \
            README.md \
            CHANGELOG.md
        print_success "打包完成: aceflow-mcp-bundle.tar.gz"
        print_info "包大小: $(du -h aceflow-mcp-bundle.tar.gz | cut -f1)"
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试..."

    # 确保环境变量设置
    export ACEFLOW_PORT=18000

    # 运行测试
    if [ -f "run_tests.py" ]; then
        python3 run_tests.py
    else
        print_error "测试脚本不存在"
        exit 1
    fi
}

# 清理环境
clean_env() {
    print_info "清理部署环境..."

    # 停止 Docker 容器
    if docker ps -a | grep -q aceflow-mcp; then
        print_info "停止 Docker 容器..."
        docker stop aceflow-mcp 2>/dev/null || true
        docker rm aceflow-mcp 2>/dev/null || true
    fi

    # 清理 Docker Compose
    if [ -f "docker-compose.yml" ]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose down -v 2>/dev/null || true
        else
            docker compose down -v 2>/dev/null || true
        fi
    fi

    # 清理构建文件
    rm -rf build/ dist/ *.spec __pycache__/ *.pyc

    # 可选：清理虚拟环境
    read -p "是否删除虚拟环境？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf aceflow-venv/
        print_info "虚拟环境已删除"
    fi

    print_success "清理完成"
}

# 主函数
main() {
    echo "=========================================="
    echo "  AceFlow MCP Server 部署脚本 v2.2.0"
    echo "=========================================="
    echo

    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    # 解析命令
    COMMAND=$1
    shift

    case $COMMAND in
        docker)
            deploy_docker "$@"
            ;;
        compose)
            deploy_compose "$@"
            ;;
        pyinstaller)
            deploy_pyinstaller "$@"
            ;;
        venv)
            deploy_venv "$@"
            ;;
        test)
            run_tests "$@"
            ;;
        clean)
            clean_env "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $COMMAND"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
