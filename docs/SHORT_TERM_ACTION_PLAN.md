# ACEFLOW-AI 短期行动计划

**规划周期**: 未来 2-4 周
**制定日期**: 2025-01-26
**当前版本**: v2.2.0 (Beta)
**原则**: 务实、聚焦、解决问题

---

## 🎯 当前核心问题

### 已识别的问题

1. **HTTP 服务器无法正常启动** 🔥
   - 配置 host=0.0.0.0 但实际绑定到 127.0.0.1
   - 导致测试套件无法运行
   - 阻塞功能验证

2. **测试环境不完善**
   - 实际的端到端测试未能运行
   - 只完成了代码审查验证
   - 需要真实测试数据

3. **功能完整性待验证**
   - HTTP 传输虽然代码完整，但未经实际测试
   - 断线重连逻辑未实现 (TODO 标记)
   - 性能指标未测量

---

## 📋 短期行动计划 (优先级排序)

---

## 优先级 P0 (本周必须完成)

### 1. 修复 HTTP 服务器配置问题 🔥

**问题描述**:
- `config.py` 设置 `host="0.0.0.0"`
- 但服务器实际启动在 `127.0.0.1:8000`
- 报错: "address already in use"

**分析**:
可能的原因:
- `get_config()` 没有正确返回配置
- `MCPHTTPServer.__init__` 配置传递有问题
- `uvicorn.run()` 参数被覆盖

**行动步骤**:
```
1. [ ] 调试 get_config() 返回值
2. [ ] 检查 ServerConfig 初始化
3. [ ] 验证 uvicorn.run() 参数传递
4. [ ] 添加启动日志确认配置
5. [ ] 测试服务器能在 0.0.0.0 启动
6. [ ] 验证可以从外部访问
```

**预计时间**: 2-4 小时
**负责人**: 后端开发
**完成标准**:
- 服务器正常启动在 0.0.0.0:8000
- curl localhost:8000/health 返回 200
- curl 127.0.0.1:8000/health 返回 200

---

### 2. 运行并通过完整测试套件

**当前状态**:
- 测试套件已编写 (`tests/test_mcp_http_complete.py`)
- 包含 12 个测试场景
- 但由于服务器问题未能运行

**行动步骤**:
```
1. [ ] 修复服务器启动问题 (依赖任务1)
2. [ ] 运行测试套件
3. [ ] 记录测试结果
4. [ ] 修复发现的问题
5. [ ] 确保 100% 测试通过
6. [ ] 生成实际测试报告
```

**预计时间**: 4-6 小时 (包含问题修复)
**负责人**: 测试/开发
**完成标准**:
- 12/12 测试通过
- 生成实际测试数据报告
- 无阻塞性问题

---

### 3. 补充 HTTP 关键功能

**待实现功能**:

#### 3.1 断线重连消息重放
**代码位置**: `mcp_http_server.py:349-352`

```python
# 当前 TODO
if last_event_id:
    logger.debug(f"处理断线重连，Last-Event-ID: {last_event_id}")
    # TODO: 实现消息重放逻辑
```

**实现方案**:
```python
# 在会话中添加消息历史队列
self.active_sessions[session_id] = {
    ...
    "message_history": deque(maxlen=100),  # 最多保留100条
}

# 消息入队时同时保存到历史
await session["message_queue"].put(event)
session["message_history"].append(event)

# 重放逻辑
if last_event_id:
    last_id = int(last_event_id)
    for event in session["message_history"]:
        if int(event["id"]) > last_id:
            yield format_sse_event(event)
```

**行动步骤**:
```
1. [ ] 添加消息历史队列
2. [ ] 实现消息保存逻辑
3. [ ] 实现重放逻辑
4. [ ] 编写单元测试
5. [ ] 手动测试断线重连
```

**预计时间**: 3-4 小时
**完成标准**:
- 断开重连后能收到丢失的消息
- 测试验证通过

---

#### 3.2 基础认证 (可选)
**需求**: API Key 认证

**实现方案**:
```python
# 添加中间件
@self.app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != self.config.api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )
    return await call_next(request)
```

**行动步骤**:
```
1. [ ] 添加 API Key 配置
2. [ ] 实现认证中间件
3. [ ] 更新文档说明
4. [ ] 编写测试用例
```

**预计时间**: 2-3 小时
**优先级**: 可延后到 P1

---

## 优先级 P1 (下周完成)

### 4. 发布 v2.2.0 正式版

**前置条件**:
- ✅ HTTP 服务器正常工作
- ✅ 测试套件全部通过
- ✅ 关键功能补充完成

**发布清单**:
```
1. [ ] 更新 pyproject.toml 版本号为 2.2.0
2. [ ] 更新 CHANGELOG.md
3. [ ] 更新 README.md (如需要)
4. [ ] Git commit 并打 tag v2.2.0
5. [ ] 构建包: python -m build
6. [ ] 上传 PyPI: twine upload dist/*
7. [ ] 验证安装: pip install aceflow-mcp-server==2.2.0
8. [ ] 创建 GitHub Release
9. [ ] 更新文档站点 (如有)
```

**发布说明要点**:
- HTTP 传输正式可用
- MCP 2025 协议完整支持
- 生产环境就绪
- 包含测试报告链接

**预计时间**: 2-3 小时
**完成标准**:
- PyPI 上可下载 v2.2.0
- GitHub Release 页面完整

---

### 5. 完善文档

**需要完善的文档**:

#### 5.1 HTTP 部署指南
**文件**: 更新 `aceflow-mcp-server/HTTP_DEPLOYMENT_GUIDE.md`

**内容**:
```markdown
- 快速开始
- 配置说明
- 故障排除
- 性能调优
- 实际案例
```

#### 5.2 API 参考文档
**文件**: 新建 `aceflow-mcp-server/docs/API_REFERENCE.md`

**内容**:
```markdown
- 健康检查 API
- MCP 端点规范
- 工具列表与参数
- 错误码说明
- 示例请求/响应
```

#### 5.3 故障排除指南
**文件**: 新建 `aceflow-mcp-server/docs/TROUBLESHOOTING.md`

**内容**:
```markdown
- 常见问题 FAQ
- 启动失败排查
- 连接问题解决
- 性能问题诊断
- 日志分析方法
```

**预计时间**: 4-6 小时
**完成标准**:
- 文档完整清晰
- 包含实际示例
- 新用户可快速上手

---

### 6. 修复已知 Bug 和问题

**已知问题清单**:

#### 6.1 模块导入警告
```
RuntimeWarning: 'aceflow_mcp_server.mcp_http_server' found in sys.modules
```
**解决方案**: 检查模块导入结构，避免循环导入

#### 6.2 依赖警告
```
DEPRECATION: Loading egg at ... is deprecated
```
**解决方案**: 重新打包 aceflow_pateoas

#### 6.3 配置传递问题
- host 配置不生效
- 需要确保配置正确传递到所有组件

**预计时间**: 3-4 小时

---

## 优先级 P2 (可选优化)

### 7. 性能测试与优化

**测试内容**:
```
1. [ ] 单请求延迟测试
2. [ ] 并发性能测试 (10/50/100 并发)
3. [ ] 长连接稳定性测试
4. [ ] 内存泄漏检查
```

**优化方向**:
- 响应延迟优化
- 内存使用优化
- 连接池管理

**预计时间**: 4-6 小时

---

### 8. Docker 镜像优化

**当前问题**:
- 镜像可能较大
- 构建速度可能慢

**优化措施**:
```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder
...

FROM python:3.11-slim
COPY --from=builder ...
```

**预计时间**: 2-3 小时

---

## 📅 时间线

### 本周 (1月27日 - 2月2日)

| 日期 | 任务 | 预计耗时 |
|------|------|---------|
| **周一** | 修复 HTTP 配置问题 | 2-4h |
| **周二** | 运行测试套件 + Bug 修复 | 4-6h |
| **周三** | 补充断线重连功能 | 3-4h |
| **周四** | 完善文档 | 4-6h |
| **周五** | 准备发布 v2.2.0 | 2-3h |

**总计**: 15-23 小时 (约 2-3 个工作日)

---

### 下周 (2月3日 - 2月9日)

| 任务 | 优先级 | 预计耗时 |
|------|--------|---------|
| 发布 v2.2.0 | P1 | 2-3h |
| 性能测试 | P2 | 4-6h |
| Docker 优化 | P2 | 2-3h |
| 认证功能 | P2 | 2-3h |

---

## ✅ 成功标准

### 两周后的目标状态

**必达目标** (P0 + P1):
- ✅ HTTP 服务器稳定运行
- ✅ 12/12 测试通过
- ✅ 断线重连功能完成
- ✅ v2.2.0 正式版发布到 PyPI
- ✅ 文档完善 (部署指南、API 文档、故障排除)
- ✅ 无阻塞性 Bug

**期望目标** (P2):
- ⭐ 性能测试完成并优化
- ⭐ Docker 镜像优化
- ⭐ 基础认证功能

**指标**:
- 测试通过率: 100%
- 文档完整度: > 90%
- 已知 Bug 数: 0 (阻塞性)
- PyPI 可用性: 100%

---

## 🚨 风险与应对

### 识别的风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| HTTP 配置问题复杂 | 中 | 高 | 限时 4h，必要时寻求帮助 |
| 测试发现重大 Bug | 中 | 高 | 及时修复，推迟发布 |
| 时间估算不准 | 高 | 中 | 每日同步进度，动态调整 |
| 依赖问题 | 低 | 中 | 提前测试不同环境 |

---

## 📞 每日检查点

### 每日结束时检查

```
[ ] 今天的任务是否完成？
[ ] 是否有新的阻塞问题？
[ ] 明天的任务是否明确？
[ ] 是否需要调整计划？
```

### 每周回顾

```
[ ] 本周目标是否达成？
[ ] 遇到了哪些问题？
[ ] 有什么经验教训？
[ ] 下周计划是否需要调整？
```

---

## 🎯 下一步行动

### 立即开始 (今天)

**任务 1: 修复 HTTP 配置问题**

**具体步骤**:
```bash
# 1. 添加调试日志
cd /home/chenjing/AI/aceflow-ai/aceflow-mcp-server

# 2. 修改 mcp_http_server.py 添加日志
# 在 main() 函数中添加:
#   logger.info(f"配置: {server.config}")
#   logger.info(f"Host: {server.config.host}, Port: {server.config.port}")

# 3. 修改 config.py 确保 host 正确
# 检查 get_config() 返回值

# 4. 测试启动
python -m aceflow_mcp_server.mcp_http_server

# 5. 验证
curl http://localhost:8000/health
curl http://127.0.0.1:8000/health
```

**预计完成**: 今天下午

---

**任务 2: 运行测试套件**

**依赖**: 任务 1 完成

**具体步骤**:
```bash
# 1. 启动服务器 (后台)
python run_tests.py

# 2. 查看结果
cat mcp_http_test_report.md

# 3. 修复失败的测试
# 4. 重新运行直到全部通过
```

**预计完成**: 明天上午

---

## 📝 总结

### 核心原则

1. **务实第一** - 解决实际问题，不做过度设计
2. **质量优先** - 确保功能可用，再谈优化
3. **小步快跑** - 2周一个迭代，快速交付
4. **问题导向** - 聚焦当前痛点，逐个击破

### 关键里程碑

- **本周**: HTTP 功能验证通过
- **下周**: v2.2.0 正式发布
- **两周后**: 进入下一个迭代

### 成功定义

**两周后**，如果我们做到了:
- ✅ HTTP 传输稳定可用
- ✅ v2.2.0 发布到 PyPI
- ✅ 文档完善可用
- ✅ 没有阻塞性问题

那么这个短期计划就是**成功的**。

---

**制定人**: 开发团队
**审批人**: 项目负责人
**制定日期**: 2025-01-26
**执行开始**: 今天

**状态**: 🚀 **立即执行**
