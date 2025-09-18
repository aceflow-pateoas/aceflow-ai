#!/bin/bash
# AceFlow MCP Server Deployment Script
# 自动化部署脚本，支持多种部署方式

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# 默认配置
DEFAULT_ENV="production"
DEFAULT_COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"
DEFAULT_IMAGE_NAME="aceflow/mcp-server:2.1.0"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助信息
show_help() {
    cat << EOF
AceFlow MCP Server部署脚本

用法: $0 [命令] [选项]

命令:
  start           启动服务
  stop            停止服务
  restart         重启服务
  status          查看服务状态
  logs            查看服务日志
  update          更新服务
  backup          备份数据
  restore         恢复数据
  health          健康检查

选项:
  -e, --env ENV            部署环境 (dev/staging/production, 默认: production)
  -f, --file FILE          Docker Compose文件路径
  -i, --image IMAGE        镜像名称 (默认: $DEFAULT_IMAGE_NAME)
  -p, --profiles PROFILES  启用的配置文件 (nginx,redis,monitoring)
  -c, --config CONFIG      配置文件目录
  -d, --detach            后台运行
  --build                 构建镜像后部署
  --pull                  拉取最新镜像
  --force                 强制操作
  -h, --help              显示帮助信息

示例:
  $0 start                                    # 基本部署
  $0 start -p nginx,redis                     # 包含nginx和redis
  $0 start -e staging --build                # staging环境并构建
  $0 update --pull                           # 拉取最新镜像并更新
  $0 logs -f                                 # 实时查看日志

EOF
}

# 解析命令行参数
parse_args() {
    COMMAND=""
    ENV="$DEFAULT_ENV"
    COMPOSE_FILE="$DEFAULT_COMPOSE_FILE"
    IMAGE_NAME="$DEFAULT_IMAGE_NAME"
    PROFILES=""
    CONFIG_DIR=""
    DETACH=true
    BUILD=false
    PULL=false
    FORCE=false
    LOG_FOLLOW=false

    # 解析命令
    if [[ $# -gt 0 ]] && [[ $1 != -* ]]; then
        COMMAND="$1"
        shift
    fi

    # 解析选项
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -i|--image)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -p|--profiles)
                PROFILES="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_DIR="$2"
                shift 2
                ;;
            -d|--detach)
                DETACH=true
                shift
                ;;
            --build)
                BUILD=true
                shift
                ;;
            --pull)
                PULL=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            -f)
                LOG_FOLLOW=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                exit 1
                ;;
        esac
    done

    # 验证命令
    if [[ ! "$COMMAND" =~ ^(start|stop|restart|status|logs|update|backup|restore|health)$ ]]; then
        print_error "无效命令: $COMMAND"
        show_help
        exit 1
    fi
}

# 检查前置条件
check_prerequisites() {
    print_info "检查前置条件..."

    # 检查Docker和Docker Compose
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose未安装"
        exit 1
    fi

    # 检查文件
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose文件不存在: $COMPOSE_FILE"
        exit 1
    fi

    print_success "前置条件检查通过"
}

# 设置环境变量
setup_environment() {
    print_info "设置环境变量..."

    # 基础环境变量
    export ACEFLOW_ENV="$ENV"
    export ACEFLOW_IMAGE="$IMAGE_NAME"
    
    # 根据环境设置不同配置
    case $ENV in
        development|dev)
            export ACEFLOW_DEBUG=true
            export ACEFLOW_LOG_LEVEL=DEBUG
            ;;
        staging)
            export ACEFLOW_DEBUG=false
            export ACEFLOW_LOG_LEVEL=INFO
            ;;
        production|prod)
            export ACEFLOW_DEBUG=false
            export ACEFLOW_LOG_LEVEL=WARNING
            ;;
    esac

    # 配置目录
    if [ -n "$CONFIG_DIR" ]; then
        if [ -d "$CONFIG_DIR" ]; then
            export ACEFLOW_CONFIG_DIR="$CONFIG_DIR"
        else
            print_warning "配置目录不存在: $CONFIG_DIR"
        fi
    fi

    print_info "环境: $ENV"
    print_info "镜像: $IMAGE_NAME"
    print_info "配置文件: $COMPOSE_FILE"
}

# 构建Docker Compose命令
build_compose_command() {
    local action="$1"
    shift
    
    COMPOSE_CMD="docker-compose -f $COMPOSE_FILE"
    
    # 添加profile
    if [ -n "$PROFILES" ]; then
        IFS=',' read -ra PROFILE_ARRAY <<< "$PROFILES"
        for profile in "${PROFILE_ARRAY[@]}"; do
            COMPOSE_CMD="$COMPOSE_CMD --profile $profile"
        done
    fi
    
    # 添加action和额外参数
    COMPOSE_CMD="$COMPOSE_CMD $action $*"
    
    echo "$COMPOSE_CMD"
}

# 启动服务
start_service() {
    print_info "启动AceFlow MCP服务器..."

    # 构建镜像
    if [ "$BUILD" = true ]; then
        print_info "构建Docker镜像..."
        "$SCRIPT_DIR/build-docker.sh" --name "$IMAGE_NAME"
    fi

    # 拉取镜像
    if [ "$PULL" = true ]; then
        print_info "拉取最新镜像..."
        PULL_CMD=$(build_compose_command "pull")
        eval "$PULL_CMD"
    fi

    # 启动服务
    UP_ARGS=""
    if [ "$DETACH" = true ]; then
        UP_ARGS="$UP_ARGS -d"
    fi

    UP_CMD=$(build_compose_command "up" $UP_ARGS)
    print_info "执行命令: $UP_CMD"
    eval "$UP_CMD"

    print_success "服务启动成功!"
}

# 停止服务
stop_service() {
    print_info "停止AceFlow MCP服务器..."

    STOP_CMD=$(build_compose_command "down")
    if [ "$FORCE" = true ]; then
        STOP_CMD="$STOP_CMD --remove-orphans -v"
    fi

    eval "$STOP_CMD"
    print_success "服务已停止"
}

# 重启服务
restart_service() {
    print_info "重启AceFlow MCP服务器..."
    stop_service
    start_service
}

# 查看服务状态
show_status() {
    print_info "查看服务状态..."
    
    STATUS_CMD=$(build_compose_command "ps")
    eval "$STATUS_CMD"
    
    # 显示端口映射
    print_info "端口映射:"
    PORTS_CMD=$(build_compose_command "port" "aceflow-mcp-server" "8000")
    eval "$PORTS_CMD" 2>/dev/null || print_warning "无法获取端口信息"
}

# 查看日志
show_logs() {
    print_info "查看服务日志..."
    
    LOG_ARGS=""
    if [ "$LOG_FOLLOW" = true ]; then
        LOG_ARGS="$LOG_ARGS -f"
    fi
    
    LOGS_CMD=$(build_compose_command "logs" $LOG_ARGS)
    eval "$LOGS_CMD"
}

# 更新服务
update_service() {
    print_info "更新AceFlow MCP服务器..."
    
    # 拉取最新镜像
    if [ "$PULL" = true ]; then
        print_info "拉取最新镜像..."
        PULL_CMD=$(build_compose_command "pull")
        eval "$PULL_CMD"
    fi
    
    # 重新创建容器
    UP_CMD=$(build_compose_command "up" "-d" "--force-recreate")
    eval "$UP_CMD"
    
    print_success "服务更新完成!"
}

# 备份数据
backup_data() {
    print_info "备份数据..."
    
    BACKUP_DIR="/tmp/aceflow-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据卷
    docker run --rm \
        -v aceflow-workspace:/backup-source:ro \
        -v aceflow-logs:/backup-logs:ro \
        -v "$BACKUP_DIR:/backup-dest" \
        alpine:latest \
        sh -c 'tar czf /backup-dest/workspace.tar.gz -C /backup-source . && tar czf /backup-dest/logs.tar.gz -C /backup-logs .'
    
    print_success "数据备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    local backup_dir="$1"
    
    if [ -z "$backup_dir" ] || [ ! -d "$backup_dir" ]; then
        print_error "请指定有效的备份目录"
        exit 1
    fi
    
    print_info "恢复数据从: $backup_dir"
    
    # 停止服务
    stop_service
    
    # 恢复数据卷
    docker run --rm \
        -v aceflow-workspace:/restore-workspace \
        -v aceflow-logs:/restore-logs \
        -v "$backup_dir:/backup-source:ro" \
        alpine:latest \
        sh -c 'cd /restore-workspace && tar xzf /backup-source/workspace.tar.gz && cd /restore-logs && tar xzf /backup-source/logs.tar.gz'
    
    print_success "数据恢复完成"
}

# 健康检查
health_check() {
    print_info "执行健康检查..."
    
    # 检查容器状态
    HEALTH_CMD=$(build_compose_command "ps" "-q" "aceflow-mcp-server")
    CONTAINER_ID=$(eval "$HEALTH_CMD")
    
    if [ -z "$CONTAINER_ID" ]; then
        print_error "服务未运行"
        return 1
    fi
    
    # 检查健康状态
    HEALTH_STATUS=$(docker inspect "$CONTAINER_ID" --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
    print_info "健康状态: $HEALTH_STATUS"
    
    # 检查HTTP端点
    if command -v curl &> /dev/null; then
        if curl -s -f "http://localhost:8000/health" > /dev/null; then
            print_success "HTTP健康检查通过"
        else
            print_error "HTTP健康检查失败"
            return 1
        fi
    fi
    
    print_success "健康检查通过"
}

# 主函数
main() {
    print_info "🚀 AceFlow MCP Server部署工具"
    
    # 解析参数
    parse_args "$@"
    
    # 检查前置条件
    check_prerequisites
    
    # 设置环境
    setup_environment
    
    # 执行命令
    case $COMMAND in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        update)
            update_service
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$1"
            ;;
        health)
            health_check
            ;;
    esac
    
    print_success "操作完成!"
}

# 执行主函数
main "$@"