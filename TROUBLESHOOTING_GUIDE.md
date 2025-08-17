# AceFlow MCP 统一服务器故障排除指南

> 🔧 **快速解决问题** - 常见问题的诊断和解决方案

## 📋 目录

- [快速诊断](#快速诊断)
- [启动问题](#启动问题)
- [配置问题](#配置问题)
- [功能问题](#功能问题)
- [性能问题](#性能问题)
- [网络问题](#网络问题)
- [权限问题](#权限问题)
- [迁移问题](#迁移问题)
- [调试工具](#调试工具)
- [日志分析](#日志分析)
- [获取支持](#获取支持)

## 🚀 快速诊断

### 一键诊断

```bash
# 运行完整系统诊断
aceflow-unified --diagnose

# 快速健康检查
aceflow-unified --health-check

# 检查配置状态
aceflow-unified --validate-config

# 查看系统状态
aceflow-unified --status
```

### 诊断输出示例

```
🔍 AceFlow MCP Server Diagnostic Report
=====================================

✅ Server Status: Running
✅ Configuration: Valid
⚠️  Performance: Degraded (high memory usage)
❌ Network: Connection timeout

📊 Quick Stats:
- Uptime: 2h 34m
- Requests: 1,247
- Errors: 3
- Memory: 245MB / 512MB

🔧 Recommendations:
1. Restart server to clear memory
2. Check network connectivity
3. Review error logs
```

## 🚫 启动问题

### 问题1: 服务器无法启动

#### 症状
```bash
$ aceflow-unified
Error: Failed to start server
```

#### 可能原因
- 端口被占用
- 配置文件错误
- 权限不足
- 依赖缺失

#### 解决方案

```bash
# 1. 检查端口占用
aceflow-unified --check-ports
netstat -tulpn | grep :8080

# 2. 使用不同端口
aceflow-unified --port 8081

# 3. 验证配置
aceflow-unified --validate-config

# 4. 检查权限
aceflow-unified --check-permissions

# 5. 重新安装依赖
uvx --reinstall aceflow-mcp-server@latest
```

### 问题2: 模块初始化失败

#### 症状
```bash
Error: Failed to initialize module 'collaboration'
ModuleNotFoundError: No module named 'collaboration_module'
```

#### 解决方案

```bash
# 1. 检查模块状态
aceflow-unified --module-status

# 2. 重新初始化模块
aceflow-unified --reinit-modules

# 3. 检查模式配置
aceflow-unified --show-config | grep mode

# 4. 强制重新加载
aceflow-unified --force-reload
```

### 问题3: 依赖冲突

#### 症状
```bash
ImportError: cannot import name 'FastMCP' from 'fastmcp'
```

#### 解决方案

```bash
# 1. 检查依赖版本
pip list | grep fastmcp

# 2. 更新依赖
pip install --upgrade fastmcp

# 3. 清理缓存
pip cache purge

# 4. 重新安装
pip uninstall aceflow-mcp-server
pip install aceflow-mcp-server
```

## ⚙️ 配置问题

### 问题1: 配置文件无效

#### 症状
```bash
Error: Invalid configuration file
JSON decode error at line 15
```

#### 解决方案

```bash
# 1. 验证JSON格式
aceflow-unified --validate-config --verbose

# 2. 使用JSON验证工具
python -m json.tool aceflow-config.json

# 3. 重置为默认配置
aceflow-unified --reset-config

# 4. 生成新配置文件
aceflow-unified --generate-config > new-config.json
```

### 问题2: 环境变量不生效

#### 症状
配置的环境变量没有被应用

#### 解决方案

```bash
# 1. 检查环境变量
env | grep ACEFLOW

# 2. 验证变量名
aceflow-unified --list-env-vars

# 3. 检查配置优先级
aceflow-unified --show-config-sources

# 4. 强制重新加载环境变量
aceflow-unified --reload-env
```

### 问题3: 模式切换失败

#### 症状
```bash
Warning: Failed to switch to enhanced mode
Collaboration module not available
```

#### 解决方案

```bash
# 1. 检查模式支持
aceflow-unified --list-modes

# 2. 验证模块可用性
aceflow-unified --check-modules

# 3. 强制启用功能
export ACEFLOW_COLLABORATION_ENABLED=true
export ACEFLOW_INTELLIGENCE_ENABLED=true

# 4. 重新启动服务器
aceflow-unified --restart
```

## 🔧 功能问题

### 问题1: 工具调用失败

#### 症状
```bash
Error: Tool 'aceflow_init' not found
```

#### 解决方案

```bash
# 1. 检查工具注册
aceflow-unified --list-tools

# 2. 验证模块状态
aceflow-unified --module-status

# 3. 重新注册工具
aceflow-unified --register-tools

# 4. 检查工具权限
aceflow-unified --check-tool-permissions
```

### 问题2: 协作功能不可用

#### 症状
协作工具返回"功能未启用"错误

#### 解决方案

```bash
# 1. 检查协作模式
aceflow-unified --show-config | grep collaboration

# 2. 启用协作功能
export ACEFLOW_MODE=enhanced
# 或
aceflow-unified --set-config collaboration.enabled=true

# 3. 重新初始化
aceflow-unified --reinit-modules

# 4. 验证功能
aceflow-unified --test-collaboration
```

### 问题3: 智能功能异常

#### 症状
智能推荐返回空结果或错误

#### 解决方案

```bash
# 1. 检查智能模块状态
aceflow-unified --module-status intelligence

# 2. 验证配置
aceflow-unified --show-config | grep intelligence

# 3. 重置智能模块
aceflow-unified --reset-module intelligence

# 4. 检查依赖
aceflow-unified --check-ai-dependencies
```

## ⚡ 性能问题

### 问题1: 响应缓慢

#### 症状
工具调用响应时间超过10秒

#### 诊断

```bash
# 1. 性能分析
aceflow-unified --profile

# 2. 检查资源使用
aceflow-unified --resource-usage

# 3. 查看性能统计
aceflow-unified --stats --detailed
```

#### 解决方案

```bash
# 1. 启用缓存
export ACEFLOW_CACHE_ENABLED=true

# 2. 调整并发限制
export ACEFLOW_MAX_CONCURRENT_REQUESTS=50

# 3. 增加超时时间
export ACEFLOW_REQUEST_TIMEOUT=60

# 4. 优化配置
aceflow-unified --optimize-config
```

### 问题2: 内存使用过高

#### 症状
服务器内存使用持续增长

#### 解决方案

```bash
# 1. 检查内存泄漏
aceflow-unified --memory-profile

# 2. 清理缓存
aceflow-unified --clear-cache

# 3. 调整缓存设置
export ACEFLOW_CACHE_TTL=300
export ACEFLOW_MAX_CACHE_SIZE=100MB

# 4. 重启服务器
aceflow-unified --restart
```

### 问题3: CPU使用率高

#### 症状
CPU使用率持续超过80%

#### 解决方案

```bash
# 1. 分析CPU使用
aceflow-unified --cpu-profile

# 2. 减少并发请求
export ACEFLOW_MAX_CONCURRENT_REQUESTS=25

# 3. 禁用非必要功能
export ACEFLOW_INTELLIGENCE_ENABLED=false

# 4. 优化算法
aceflow-unified --optimize-algorithms
```

## 🌐 网络问题

### 问题1: 连接超时

#### 症状
```bash
Error: Connection timeout after 30 seconds
```

#### 解决方案

```bash
# 1. 检查网络连接
ping localhost
telnet localhost 8080

# 2. 调整超时设置
export ACEFLOW_CONNECTION_TIMEOUT=60

# 3. 检查防火墙
aceflow-unified --check-firewall

# 4. 使用不同端口
aceflow-unified --port 8081
```

### 问题2: SSL/TLS 错误

#### 症状
```bash
Error: SSL certificate verification failed
```

#### 解决方案

```bash
# 1. 检查证书
aceflow-unified --check-ssl

# 2. 更新证书
aceflow-unified --update-ssl

# 3. 临时禁用SSL验证（仅测试）
export ACEFLOW_SSL_VERIFY=false

# 4. 使用自定义证书
aceflow-unified --ssl-cert /path/to/cert.pem
```

### 问题3: 代理配置问题

#### 症状
通过代理无法访问服务器

#### 解决方案

```bash
# 1. 配置代理
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080

# 2. 绕过代理
export NO_PROXY=localhost,127.0.0.1

# 3. 验证代理设置
aceflow-unified --test-proxy

# 4. 使用直连
aceflow-unified --no-proxy
```

## 🔐 权限问题

### 问题1: 文件权限错误

#### 症状
```bash
PermissionError: [Errno 13] Permission denied: '/path/to/config'
```

#### 解决方案

```bash
# 1. 检查文件权限
ls -la ~/.aceflow/

# 2. 修复权限
chmod 755 ~/.aceflow/
chmod 644 ~/.aceflow/config.json

# 3. 更改所有者
sudo chown -R $USER:$USER ~/.aceflow/

# 4. 使用不同目录
export ACEFLOW_CONFIG_DIR=/tmp/aceflow
```

### 问题2: 端口权限问题

#### 症状
```bash
PermissionError: [Errno 13] Permission denied: bind to port 80
```

#### 解决方案

```bash
# 1. 使用非特权端口
aceflow-unified --port 8080

# 2. 使用sudo（不推荐）
sudo aceflow-unified --port 80

# 3. 配置端口转发
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# 4. 使用setcap
sudo setcap 'cap_net_bind_service=+ep' $(which aceflow-unified)
```

## 🔄 迁移问题

### 问题1: 自动迁移失败

#### 症状
```bash
Error: Migration failed - incompatible configuration format
```

#### 解决方案

```bash
# 1. 手动迁移
aceflow-unified --migrate-config --manual

# 2. 备份并重置
aceflow-unified --backup-config
aceflow-unified --reset-config

# 3. 逐步迁移
aceflow-unified --migrate-step-by-step

# 4. 查看迁移日志
aceflow-unified --migration-log
```

### 问题2: 配置不兼容

#### 症状
旧配置格式无法识别

#### 解决方案

```bash
# 1. 检查配置版本
aceflow-unified --config-version

# 2. 转换配置格式
aceflow-unified --convert-config --from v1.x --to v2.0

# 3. 使用迁移工具
aceflow-unified --migration-wizard

# 4. 手动创建新配置
aceflow-unified --generate-config --based-on-legacy
```

## 🛠️ 调试工具

### 内置调试命令

```bash
# 系统诊断
aceflow-unified --diagnose
aceflow-unified --health-check
aceflow-unified --system-info

# 配置调试
aceflow-unified --show-config
aceflow-unified --validate-config
aceflow-unified --config-diff

# 模块调试
aceflow-unified --module-status
aceflow-unified --test-modules
aceflow-unified --module-dependencies

# 性能调试
aceflow-unified --profile
aceflow-unified --benchmark
aceflow-unified --resource-usage

# 网络调试
aceflow-unified --test-connectivity
aceflow-unified --check-ports
aceflow-unified --network-info
```

### 调试模式

```bash
# 启用详细日志
export ACEFLOW_LOG_LEVEL=DEBUG
export ACEFLOW_DEBUG=true

# 启用性能分析
export ACEFLOW_PROFILE=true

# 启用内存调试
export ACEFLOW_MEMORY_DEBUG=true

# 保存调试信息
aceflow-unified --debug --save-debug-info debug-report.json
```

### 外部调试工具

```bash
# 使用 strace 跟踪系统调用
strace -o trace.log aceflow-unified

# 使用 lsof 检查文件描述符
lsof -p $(pgrep aceflow-unified)

# 使用 netstat 检查网络连接
netstat -tulpn | grep aceflow

# 使用 htop 监控资源使用
htop -p $(pgrep aceflow-unified)
```

## 📊 日志分析

### 日志位置

```bash
# 默认日志位置
~/.aceflow/logs/aceflow.log

# 系统日志
/var/log/aceflow/aceflow.log

# 临时日志
/tmp/aceflow-debug.log

# 自定义日志位置
export ACEFLOW_LOG_FILE=/path/to/custom.log
```

### 日志级别

```bash
# 设置日志级别
export ACEFLOW_LOG_LEVEL=DEBUG    # 最详细
export ACEFLOW_LOG_LEVEL=INFO     # 标准信息
export ACEFLOW_LOG_LEVEL=WARNING  # 仅警告
export ACEFLOW_LOG_LEVEL=ERROR    # 仅错误
```

### 日志分析命令

```bash
# 查看最新日志
aceflow-unified --tail-log

# 搜索错误
aceflow-unified --grep-log "ERROR"

# 分析性能
aceflow-unified --analyze-performance-log

# 生成日志报告
aceflow-unified --log-report
```

### 常见日志模式

#### 启动成功
```
[INFO] aceflow-unified: Server starting...
[INFO] aceflow-unified[config]: Configuration loaded successfully
[INFO] aceflow-unified[core]: Core module initialized
[INFO] aceflow-unified[server]: Server ready on port 8080
```

#### 配置错误
```
[ERROR] aceflow-unified[config]: Invalid configuration: mode 'invalid' not supported
[ERROR] aceflow-unified[config]: Valid modes: basic, standard, enhanced, auto
```

#### 模块错误
```
[ERROR] aceflow-unified[collaboration]: Failed to initialize collaboration module
[ERROR] aceflow-unified[collaboration]: ModuleNotFoundError: collaboration_module
```

#### 性能警告
```
[WARNING] aceflow-unified[performance]: High memory usage: 450MB/512MB
[WARNING] aceflow-unified[performance]: Request queue full: 100/100
```

## 📞 获取支持

### 自助支持

```bash
# 生成支持报告
aceflow-unified --generate-support-report

# 收集系统信息
aceflow-unified --collect-system-info

# 运行诊断测试
aceflow-unified --run-diagnostics

# 导出配置和日志
aceflow-unified --export-debug-package debug-package.zip
```

### 社区支持

- **💬 讨论论坛**: https://community.aceflow.dev
- **📚 文档**: https://docs.aceflow.dev
- **🎥 视频教程**: https://tutorials.aceflow.dev
- **📖 FAQ**: https://faq.aceflow.dev

### 技术支持

- **🐛 问题报告**: https://github.com/aceflow/mcp-server/issues
- **📧 邮件支持**: support@aceflow.dev
- **💬 实时聊天**: https://chat.aceflow.dev
- **📞 电话支持**: +1-800-ACEFLOW（付费用户）

### 报告问题时请提供

1. **系统信息**
   ```bash
   aceflow-unified --system-info
   ```

2. **配置信息**
   ```bash
   aceflow-unified --show-config --sanitized
   ```

3. **错误日志**
   ```bash
   aceflow-unified --tail-log --lines 100
   ```

4. **诊断报告**
   ```bash
   aceflow-unified --diagnose --export
   ```

5. **重现步骤**
   - 详细的操作步骤
   - 预期结果 vs 实际结果
   - 环境信息（OS、Python版本等）

### 紧急支持

对于生产环境的紧急问题：

- **🚨 紧急热线**: +1-800-ACEFLOW-911
- **📧 紧急邮箱**: emergency@aceflow.dev
- **💬 紧急聊天**: https://emergency.aceflow.dev

---

**🔧 还有问题？我们随时准备帮助您解决任何技术难题！**