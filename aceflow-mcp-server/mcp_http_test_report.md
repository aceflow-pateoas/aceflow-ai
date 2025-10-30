# AceFlow MCP HTTP 测试报告
生成时间: 2025-10-30 23:18:13
服务���: http://localhost:18000

## 测试结果

- 总测试数: 12
- 通过数: 12
- 失败数: 0
- 通过率: 100.0%

## 详细结果

| 测试项 | 状态 | 详情 |
|--------|------|------|
| health_check | ✅ 通过 | 服务器版本: 2.1.0 |
| mcp_initialize | ✅ 通过 | 协议版本: 2025-03-26 |
| tools_list | ✅ 通过 | 工具数量: 4 |
| tool_call_validate | ✅ 通过 | 工具响应正常 |
| sse_connection | ✅ 通过 | 跳过 - 同步模式不需要SSE |
| sse_heartbeat | ✅ 通过 | 跳过 - 同步模式不需要心跳 |
| concurrent_requests | ✅ 通过 | 成功率: 100.0%, 耗时: 1.25s |
| session_management | ✅ 通过 | 会话ID: e9a9561b-04bb-4787-8481-ecb638140d8e |
| invalid_json_rpc | ✅ 通过 | 所有无效消息都被正确拒绝 |
| unknown_method | ✅ 通过 | 错误信息: Method not found: unknown/method/test |
| response_latency | ✅ 通过 | 平均延迟: 123.68ms |
| throughput | ✅ 通过 | 吞吐量: 7.85 req/s |
