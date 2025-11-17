# 设计方案阶段 (Design Specification)

**阶段目标**: 输出详细的设计文档和技术方案

---

## 检查清单 (Checklist)

请确保完成以下所有项目：

### 必须完成 (Required)

- [ ] **架构设计已完成**
  系统架构图、模块划分、层次结构清晰

- [ ] **接口设计已细化**
  所有API接口的详细定义（包括边界情况处理）

- [ ] **数据库设计已确认**
  表结构、索引、约束、迁移脚本（如需要）

- [ ] **错误处理方案已设计**
  异常类型、错误码、日志策略

- [ ] **安全方案已考虑**
  认证、授权、数据加密、输入验证

### 可选项 (Optional)

- [ ] 性能优化方案（缓存策略、查询优化）
- [ ] 监控和告警方案
- [ ] 部署方案和配置管理
- [ ] 回滚方案

---

## 输出物 (Deliverables)

1. **详细设计文档** (Detailed Design Document)
   - 系统架构图（组件图、部署图）
   - 序列图（关键流程）
   - 类图或模块依赖图

2. **API详细规范** (Detailed API Specification)
   - OpenAPI/Swagger 文档
   - 示例请求/响应
   - 错误处理说明

3. **数据库Schema** (Database Schema)
   - DDL脚本或Migration文件
   - 索引设计文档
   - 数据字典

4. **技术决策记录** (Technical Decision Records)
   - 关键技术选型的理由
   - 权衡分析（Tradeoffs）

---

## 完成标准 (Completion Criteria)

✅ 架构设计经过评审
✅ 所有API接口定义完整且无歧义
✅ 数据库设计符合范式要求
✅ 安全和错误处理方案合理

---

## 设计评审要点 (Design Review Checklist)

在完成本阶段前，考虑以下问题：

- **可扩展性**: 设计是否支持未来扩展？
- **可维护性**: 代码结构是否清晰易懂？
- **性能**: 是否有明显的性能瓶颈？
- **安全**: 是否存在安全漏洞？
- **一致性**: 是否与现有系统风格一致？

---

## 项目上下文 (Project Context)

{{project_memory}}

---

## 下一步 (Next Steps)

完成本阶段后，调用 `complete_stage(stage_id="design")` 进入**编码实现**阶段。
