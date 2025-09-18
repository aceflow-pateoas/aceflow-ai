#!/bin/bash
set -e

# AceFlow MCP Server Docker Entrypoint
# 智能启动脚本，支持多种运行模式

echo "🚀 AceFlow MCP Server v2.1.0 启动中..."

# 显示环境信息
echo "📋 环境配置:"
echo "  - ACEFLOW_TRANSPORT: ${ACEFLOW_TRANSPORT:-auto}"
echo "  - ACEFLOW_HOST: ${ACEFLOW_HOST:-0.0.0.0}"
echo "  - ACEFLOW_PORT: ${ACEFLOW_PORT:-8000}"
echo "  - ACEFLOW_LOG_LEVEL: ${ACEFLOW_LOG_LEVEL:-INFO}"
echo "  - ACEFLOW_DEBUG: ${ACEFLOW_DEBUG:-false}"

# 检查工作目录
if [ -n "$ACEFLOW_WORKING_DIRECTORY" ]; then
    echo "  - 工作目录: $ACEFLOW_WORKING_DIRECTORY"
    if [ ! -d "$ACEFLOW_WORKING_DIRECTORY" ]; then
        echo "⚠️ 工作目录不存在，将创建: $ACEFLOW_WORKING_DIRECTORY"
        mkdir -p "$ACEFLOW_WORKING_DIRECTORY" || echo "❌ 无法创建工作目录"
    fi
fi

# 检查配置文件
if [ -n "$ACEFLOW_CONFIG_FILE" ] && [ -f "$ACEFLOW_CONFIG_FILE" ]; then
    echo "  - 配置文件: $ACEFLOW_CONFIG_FILE"
fi

# 权限检查
if [ "$(id -u)" = "0" ]; then
    echo "⚠️ 警告: 以root用户运行，建议使用非root用户"
fi

# 健康检查函数
check_health() {
    local max_attempts=30
    local attempt=1
    
    echo "🔍 等待服务启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if [ "$ACEFLOW_TRANSPORT" = "stdio" ]; then
            # stdio模式无法进行HTTP健康检查
            echo "✅ stdio模式启动完成"
            return 0
        else
            # HTTP模式健康检查
            if curl -s -f "http://localhost:${ACEFLOW_PORT:-8000}/health" > /dev/null 2>&1; then
                echo "✅ HTTP服务健康检查通过"
                return 0
            fi
        fi
        
        echo "⏳ 健康检查 $attempt/$max_attempts 失败，等待重试..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ 健康检查超时失败"
    return 1
}

# 信号处理
cleanup() {
    echo "🛑 收到关闭信号，正在优雅关闭服务..."
    if [ -n "$SERVER_PID" ]; then
        kill -TERM "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    echo "✅ 服务已关闭"
    exit 0
}

# 捕获信号
trap cleanup SIGTERM SIGINT SIGQUIT

# 检测运行模式
detect_mode() {
    if [ "$ACEFLOW_TRANSPORT" = "auto" ]; then
        if [ -n "$KUBERNETES_SERVICE_HOST" ]; then
            echo "🎯 检测到Kubernetes环境，使用streamable-http模式"
            export ACEFLOW_TRANSPORT="streamable-http"
        elif [ -f "/.dockerenv" ]; then
            echo "🎯 检测到Docker环境，使用streamable-http模式"
            export ACEFLOW_TRANSPORT="streamable-http"
        elif [ -t 0 ]; then
            echo "🎯 检测到TTY环境，使用stdio模式"
            export ACEFLOW_TRANSPORT="stdio"
        else
            echo "🎯 默认使用streamable-http模式"
            export ACEFLOW_TRANSPORT="streamable-http"
        fi
    fi
}

# 启动前检测
detect_mode

# 构建启动命令
build_command() {
    local cmd="python -m aceflow_mcp_server.unified_server"
    
    # 传输模式
    cmd="$cmd --transport $ACEFLOW_TRANSPORT"
    
    # HTTP模式参数
    if [ "$ACEFLOW_TRANSPORT" != "stdio" ]; then
        cmd="$cmd --host $ACEFLOW_HOST"
        cmd="$cmd --port $ACEFLOW_PORT"
    fi
    
    # 日志级别
    cmd="$cmd --log-level $ACEFLOW_LOG_LEVEL"
    
    # 调试模式
    if [ "$ACEFLOW_DEBUG" = "true" ]; then
        cmd="$cmd --debug"
    fi
    
    # 工作目录
    if [ -n "$ACEFLOW_WORKING_DIRECTORY" ]; then
        cmd="$cmd --working-directory $ACEFLOW_WORKING_DIRECTORY"
    fi
    
    # 配置文件
    if [ -n "$ACEFLOW_CONFIG_FILE" ] && [ -f "$ACEFLOW_CONFIG_FILE" ]; then
        cmd="$cmd --config $ACEFLOW_CONFIG_FILE"
    fi
    
    echo "$cmd"
}

# 如果传入的是aceflow相关命令，直接执行
if [ "$1" = "python" ] && [[ "$*" == *"aceflow"* ]]; then
    echo "🎯 执行AceFlow命令: $*"
    exec "$@"
fi

# 如果传入其他命令，直接执行
if [ "$1" != "python" ] || [[ "$*" != *"aceflow"* ]]; then
    if [ "$#" -gt 0 ]; then
        echo "🎯 执行自定义命令: $*"
        exec "$@"
    fi
fi

# 启动AceFlow MCP Server
echo "🚀 启动AceFlow MCP服务器..."
COMMAND=$(build_command)
echo "📋 启动命令: $COMMAND"

# 启动服务并获取PID
$COMMAND &
SERVER_PID=$!

# 等待一小段时间让服务启动
sleep 3

# 进行健康检查（后台执行，不阻塞主进程）
if [ "$ACEFLOW_TRANSPORT" != "stdio" ]; then
    check_health &
fi

echo "✅ AceFlow MCP Server 启动完成!"
echo "📊 服务器PID: $SERVER_PID"

# 显示访问信息
if [ "$ACEFLOW_TRANSPORT" != "stdio" ]; then
    echo "🌐 HTTP端点: http://$ACEFLOW_HOST:$ACEFLOW_PORT/mcp"
    echo "🔍 健康检查: http://$ACEFLOW_HOST:$ACEFLOW_PORT/health"
fi

# 等待服务进程
wait $SERVER_PID