# 📂 aceflow_result 目录说明

这个目录用于存放AI基于模板生成的工作流文档。

## 目录结构

```
aceflow_result/
└── iter_001/                   # 第一次迭代
    └── standard/               # 使用的工作流模式
        ├── user_stories.md     # ✅ 已生成（示例）
        ├── task_breakdown.md   # 待生成
        ├── test_design.md      # 待生成
        ├── implementation.md   # 待生成
        ├── unit_test.md        # 待生成
        ├── integration_test.md # 待生成
        └── code_review.md      # 待生成
```

## 工作流推进

### ✅ 已完成阶段

1. **user_stories.md** - 用户故事
   - 为"用户登录"功能编写了3个用户故事
   - 包含完整的验收标准
   - 已评审通过

### ⏳ 待完成阶段

按顺序推进：
2. task_breakdown.md - 任务分解
3. test_design.md - 测试设计
4. implementation.md - 功能实现
5. unit_test.md - 单元测试
6. integration_test.md - 集成测试
7. code_review.md - 代码审查

## 如何使用

### 与AI对话推进工作流

```
User: 用户故事阶段已完成，现在进入任务分解阶段。
      请根据 .aceflow/templates/standard/task_breakdown.md 模板，
      基于 aceflow_result/iter_001/standard/user_stories.md 中的用户故事，
      生成任务分解文档。

AI: [读取模板和用户故事]
    [生成任务分解内容]
    [保存到 aceflow_result/iter_001/standard/task_breakdown.md]
```

### 多迭代管理

每次新功能开发创建新的迭代目录：

```bash
# 第二次迭代
mkdir -p aceflow_result/iter_002/standard

# 第三次迭代
mkdir -p aceflow_result/iter_003/complete
```

## Git版本控制

### 选项1: 提交到Git（推荐）

将 `aceflow_result/` 作为项目文档提交：
- 记录开发过程
- 团队成员可查看
- 便于回顾和学习

### 选项2: 不提交

在 `.gitignore` 中添加：
```
aceflow_result/
```

## 注意事项

1. **命名规范**: 迭代目录建议使用 `iter_001`, `iter_002` 等格式
2. **模式选择**: 每个迭代目录下只有一个模式目录（standard 或 complete）
3. **文档完整性**: 建议每个阶段都生成对应文档，保持完整性

---

**示例文档**: `user_stories.md` 是一个完整的示例，展示AI基于模板生成的文档格式。
