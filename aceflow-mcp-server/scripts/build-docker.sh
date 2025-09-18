#!/bin/bash
# AceFlow MCP Server Docker Build Script
# 构建Docker镜像的自动化脚本

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# 默认配置
DEFAULT_IMAGE_NAME="aceflow/mcp-server"
DEFAULT_VERSION="2.1.0"
DEFAULT_PLATFORM="linux/amd64,linux/arm64"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
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

# 显示帮助信息
show_help() {
    cat << EOF
AceFlow MCP Server Docker构建脚本

用法: $0 [选项]

选项:
  -n, --name NAME          镜像名称 (默认: $DEFAULT_IMAGE_NAME)
  -v, --version VERSION    版本标签 (默认: $DEFAULT_VERSION)
  -p, --platform PLATFORM 目标平台 (默认: $DEFAULT_PLATFORM)
  -t, --tags TAGS         额外标签 (逗号分隔)
  --push                   构建后推送到Registry
  --no-cache              不使用缓存构建
  --multi-arch            多架构构建
  --dev                   开发模式构建 (包含调试工具)
  -h, --help              显示此帮助信息

示例:
  $0                                    # 基本构建
  $0 --push                             # 构建并推送
  $0 --multi-arch --push                # 多架构构建并推送
  $0 --dev -v dev-latest               # 开发版本构建
  $0 -n myregistry/aceflow -v 1.0.0    # 自定义名称和版本

EOF
}

# 解析命令行参数
parse_args() {
    IMAGE_NAME="$DEFAULT_IMAGE_NAME"
    VERSION="$DEFAULT_VERSION"
    PLATFORM="$DEFAULT_PLATFORM"
    PUSH=false
    NO_CACHE=false
    MULTI_ARCH=false
    DEV_MODE=false
    EXTRA_TAGS=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -t|--tags)
                EXTRA_TAGS="$2"
                shift 2
                ;;
            --push)
                PUSH=true
                shift
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --multi-arch)
                MULTI_ARCH=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查前置条件
check_prerequisites() {
    print_info "检查前置条件..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装或不在PATH中"
        exit 1
    fi

    # 检查Docker版本
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    print_info "Docker版本: $DOCKER_VERSION"

    # 检查Docker Buildx（用于多架构构建）
    if [ "$MULTI_ARCH" = true ]; then
        if ! docker buildx version &> /dev/null; then
            print_error "Docker Buildx未安装，多架构构建需要Buildx支持"
            exit 1
        fi
        print_info "Docker Buildx已安装"
    fi

    # 检查项目文件
    if [ ! -f "$DOCKER_DIR/Dockerfile" ]; then
        print_error "Dockerfile不存在: $DOCKER_DIR/Dockerfile"
        exit 1
    fi

    if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
        print_error "pyproject.toml不存在: $PROJECT_ROOT/pyproject.toml"
        exit 1
    fi

    print_success "前置条件检查通过"
}

# 构建标签列表
build_tags() {
    TAGS=("$IMAGE_NAME:$VERSION")
    
    # 添加latest标签（如果不是开发版本）
    if [ "$DEV_MODE" = false ] && [ "$VERSION" != "dev-latest" ]; then
        TAGS+=("$IMAGE_NAME:latest")
    fi
    
    # 添加额外标签
    if [ -n "$EXTRA_TAGS" ]; then
        IFS=',' read -ra ADDR <<< "$EXTRA_TAGS"
        for tag in "${ADDR[@]}"; do
            TAGS+=("$IMAGE_NAME:$tag")
        done
    fi
    
    print_info "构建标签: ${TAGS[*]}"
}

# 构建Docker镜像
build_image() {
    print_info "开始构建Docker镜像..."

    # 构建参数
    BUILD_ARGS=(
        "--file" "$DOCKER_DIR/Dockerfile"
        "--build-arg" "VERSION=$VERSION"
    )

    # 开发模式
    if [ "$DEV_MODE" = true ]; then
        BUILD_ARGS+=("--target" "development")
        print_info "使用开发模式构建"
    fi

    # 无缓存构建
    if [ "$NO_CACHE" = true ]; then
        BUILD_ARGS+=("--no-cache")
        print_info "不使用缓存构建"
    fi

    # 添加标签
    for tag in "${TAGS[@]}"; do
        BUILD_ARGS+=("--tag" "$tag")
    done

    # 多架构构建
    if [ "$MULTI_ARCH" = true ]; then
        print_info "多架构构建: $PLATFORM"
        
        # 创建并使用buildx构建器
        BUILDER_NAME="aceflow-builder"
        docker buildx create --name "$BUILDER_NAME" --use --bootstrap 2>/dev/null || true
        
        BUILD_ARGS+=("--platform" "$PLATFORM")
        
        # 如果需要推送，添加推送参数
        if [ "$PUSH" = true ]; then
            BUILD_ARGS+=("--push")
        else
            BUILD_ARGS+=("--load")
        fi
        
        # 执行buildx构建
        docker buildx build "${BUILD_ARGS[@]}" "$PROJECT_ROOT"
        
    else
        # 单架构构建
        docker build "${BUILD_ARGS[@]}" "$PROJECT_ROOT"
        
        # 推送镜像
        if [ "$PUSH" = true ]; then
            for tag in "${TAGS[@]}"; do
                print_info "推送镜像: $tag"
                docker push "$tag"
            done
        fi
    fi
}

# 验证构建结果
verify_build() {
    print_info "验证构建结果..."

    # 检查镜像是否存在
    for tag in "${TAGS[@]}"; do
        if docker image inspect "$tag" &> /dev/null; then
            print_success "镜像构建成功: $tag"
            
            # 显示镜像信息
            SIZE=$(docker image inspect "$tag" --format='{{.Size}}' | numfmt --to=iec)
            CREATED=$(docker image inspect "$tag" --format='{{.Created}}' | cut -d'T' -f1)
            print_info "  - 大小: $SIZE"
            print_info "  - 创建时间: $CREATED"
        else
            print_error "镜像构建失败: $tag"
            return 1
        fi
    done
}

# 清理函数
cleanup() {
    if [ "$MULTI_ARCH" = true ]; then
        # 清理buildx构建器
        docker buildx rm "aceflow-builder" 2>/dev/null || true
    fi
}

# 主函数
main() {
    print_info "🚀 AceFlow MCP Server Docker构建开始"
    
    # 解析参数
    parse_args "$@"
    
    # 显示构建配置
    print_info "构建配置:"
    print_info "  - 镜像名称: $IMAGE_NAME"
    print_info "  - 版本: $VERSION"
    print_info "  - 平台: $PLATFORM"
    print_info "  - 推送: $PUSH"
    print_info "  - 多架构: $MULTI_ARCH"
    print_info "  - 开发模式: $DEV_MODE"
    
    # 设置清理陷阱
    trap cleanup EXIT
    
    # 执行构建步骤
    check_prerequisites
    build_tags
    build_image
    verify_build
    
    print_success "🎉 Docker镜像构建完成!"
    
    # 显示使用方法
    print_info "使用方法:"
    print_info "  docker run -p 8000:8000 ${TAGS[0]}"
    print_info "  docker-compose -f docker/docker-compose.yml up -d"
}

# 执行主函数
main "$@"