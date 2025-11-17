# 需求梳理阶段 (Requirement Analysis)

**阶段目标**: 梳理需求并输出清晰的设计方案

---

## 检查清单 (Checklist)

请确保完成以下所有项目：

### 必须完成 (Required)

- [ ] **接口定义已输出**
  API路径、请求方法、入参、出参、错误码定义清晰

- [ ] **核心逻辑已设计**
  用伪代码或流程图描述核心业务逻辑

- [ ] **技术方案已确认**
  明确使用的库、框架、存储方案、架构模式

- [ ] **数据模型已设计**
  数据库表结构、字段定义、索引设计（如适用）

- [ ] **潜在问题已识别**
  性能瓶颈、安全风险、并发问题、边界情况

### 可选项 (Optional)

- [ ] 用户故事已编写（User Stories）
- [ ] 验收标准已定义（Acceptance Criteria）
- [ ] 依赖关系已梳理（Dependencies）
- [ ] 时间估算已完成（Effort Estimation）

---

## 输出物 (Deliverables)

完成本阶段后，应产出以下文档或产物：

1. **接口定义文档** (API Specification)
   - API端点列表
   - 请求/响应格式
   - 错误码说明

2. **核心逻辑设计** (Core Logic Design)
   - 流程图或伪代码
   - 关键算法说明
   - 状态机图（如适用）

3. **技术方案说明** (Technical Specification)
   - 技术栈选择及理由
   - 架构设计图
   - 第三方依赖列表

4. **数据模型** (Data Model)
   - ER图或数据库Schema
   - 字段说明文档

---

## 完成标准 (Completion Criteria)

满足以下条件可进入下一阶段：

✅ 所有必须项已勾选
✅ 至少产出了接口定义和核心逻辑设计
✅ 技术方案获得团队/客户确认
✅ 没有未解决的重大风险

---

## 项目上下文 (Project Context)

{{project_memory}}

---

## 下一步 (Next Steps)

完成本阶段后，调用 `complete_stage(stage_id="requirement")` 进入**设计方案**阶段。
