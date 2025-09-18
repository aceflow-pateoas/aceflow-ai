# AceFlow MCP Server Docker Container
# 多阶段构建，优化镜像大小和安全性
# 支持HTTP和stdio传输模式

FROM python:3.11-slim as builder

# 设置构建环境
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./
COPY aceflow_mcp_server/ ./aceflow_mcp_server/
COPY LICENSE README.md ./

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install . && \
    pip install fastapi uvicorn[standard] pyyaml

# 运行时阶段
FROM python:3.11-slim as runtime

# 设置运行环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ACEFLOW_TRANSPORT=auto \
    ACEFLOW_HOST=0.0.0.0 \
    ACEFLOW_PORT=8000 \
    ACEFLOW_LOG_LEVEL=INFO

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非root用户
RUN groupadd -r aceflow && useradd -r -g aceflow aceflow

# 从构建阶段复制应用
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# 创建应用目录和日志目录
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R aceflow:aceflow /app

# 切换到非root用户
USER aceflow
WORKDIR /app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${ACEFLOW_PORT:-8000}/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动脚本
COPY docker/docker-entrypoint.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
USER aceflow

# 默认启动命令
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "aceflow_mcp_server.unified_server", "--transport", "auto"]

# 元数据标签
LABEL maintainer="AceFlow Team <team@aceflow.dev>" \
      description="AceFlow MCP Server - AI协作增强版MCP服务器" \
      version="2.1.0" \
      org.opencontainers.image.title="AceFlow MCP Server" \
      org.opencontainers.image.description="AI-协作增强版MCP服务器，支持双向AI-MCP数据交换" \
      org.opencontainers.image.version="2.1.0" \
      org.opencontainers.image.authors="AceFlow Team" \
      org.opencontainers.image.url="https://github.com/aceflow-pateoas/aceflow-ai" \
      org.opencontainers.image.source="https://github.com/aceflow-pateoas/aceflow-ai" \
      org.opencontainers.image.licenses="MIT"