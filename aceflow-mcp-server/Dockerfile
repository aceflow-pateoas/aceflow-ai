# AceFlow MCP Server Dockerfile
# 用于内网私有部署的容器镜像

FROM python:3.11-slim

# 元数据
LABEL maintainer="AceFlow Team <team@aceflow.dev>"
LABEL version="2.2.0"
LABEL description="AceFlow MCP Server for private deployment with internal LLMs"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml README.md CHANGELOG.md ./
COPY aceflow_mcp_server/ ./aceflow_mcp_server/
COPY tests/ ./tests/

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# 创建工作目录
RUN mkdir -p /workspace

# 设置环境变量
ENV ACEFLOW_HOST=0.0.0.0 \
    ACEFLOW_PORT=8000 \
    ACEFLOW_TRANSPORT=streamable-http \
    ACEFLOW_LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${ACEFLOW_PORT}/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "aceflow_mcp_server.mcp_http_server"]
