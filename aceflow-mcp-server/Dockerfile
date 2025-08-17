# AceFlow MCP Unified Server Docker Image
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ACEFLOW_MODE=standard
ENV ACEFLOW_LOG_LEVEL=INFO

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml README.md LICENSE ./
COPY aceflow_mcp_server/ ./aceflow_mcp_server/

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash aceflow
USER aceflow

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD aceflow-unified doctor || exit 1

# 启动命令
CMD ["aceflow-unified", "serve", "--host", "0.0.0.0", "--port", "8080"]