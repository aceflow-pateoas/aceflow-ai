# 方案设计阶段 (Refactoring Plan)

## 检查清单 (Checklist)

### 必须完成 (Required)

- [ ] **重构方案已设计**
  明确如何重构（使用哪些重构技术）

- [ ] **重构步骤已分解**
  将重构拆分为可执行的小步骤

- [ ] **测试策略已确定**
  如何验证重构的正确性

- [ ] **回滚方案已准备**
  如果重构失败如何回退

- [ ] **影响范围已确定**
  哪些模块会受到影响

### 可选项 (Optional)

- [ ] **重构工具已选择**
  IDE重构工具、静态分析工具等

- [ ] **进度计划已制定**
  预计每个步骤的耗时

## 输出物 (Deliverables)

1. **重构方案文档**（详细的重构策略）
2. **分步执行计划**（可执行的小步骤）
3. **测试策略**（如何验证）
4. **回滚方案**（失败应对）
5. **影响分析**（依赖关系）

## 重构技术参考 (Refactoring Techniques)

### 提取/内联
- Extract Method - 提取方法
- Extract Variable - 提取变量
- Inline Method - 内联方法
- Extract Class - 提取类

### 移动
- Move Method - 移动方法
- Move Field - 移动字段

### 简化
- Simplify Conditional Expression - 简化条件表达式
- Replace Temp with Query - 以查询取代临时变量
- Decompose Conditional - 分解条件表达式

### 组织数据
- Encapsulate Field - 封装字段
- Replace Magic Number with Symbolic Constant - 以符号常量取代魔法数

### 设计模式
- Replace Constructor with Factory Method - 以工厂方法取代构造函数
- Introduce Null Object - 引入空对象

## 重构原则 (Principles)

1. **小步前进**: 每次重构保持小改动
2. **频繁测试**: 每步重构后立即测试
3. **保持功能**: 重构不改变外部行为
4. **可回退**: 随时可以回滚到上一个稳定状态

## 完成标准 (Completion Criteria)

- 有清晰可执行的重构步骤
- 测试和回滚策略明确
- 影响范围已评估

## 项目上下文 (Project Context)

{{project_memory}}

## 下一步 (Next Steps)

完成本阶段后，调用 `complete_stage(stage_id="plan")` 进入**重构实现**阶段。
