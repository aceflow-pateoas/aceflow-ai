# 项目源码目录

这里放置你的实际项目代码。

## 示例结构

```
src/
├── main.py          # 主程序
├── models/          # 数据模型
├── controllers/     # 控制器
├── services/        # 业务逻辑
└── utils/           # 工具函数
```

## 与AceFlow的关系

- `.aceflow/templates/` - 工作流模板
- `aceflow_result/` - AI生成的开发文档
- `src/` - 基于文档实现的实际代码

## 工作流

1. AI读取模板生成用户故事 → `aceflow_result/iter_001/standard/user_stories.md`
2. AI生成任务分解 → `aceflow_result/iter_001/standard/task_breakdown.md`
3. 开发人员根据任务分解实现代码 → `src/`
4. AI辅助生成测试报告 → `aceflow_result/iter_001/standard/unit_test.md`
