# AceFlow v3.0 模板库

## 📚 模板结构说明

本目录包含 AceFlow v3.0 所有流程模式的模板文件,支持 **Minimal**、**Standard**、**Complete** 和 **Smart** 四种模式。

```
templates/
├── README.md                          # 本文档
│
├── minimal/                           # 轻量级模式(P→D→R)
│   ├── README.md                      # 模式使用指南
│   ├── planning.md                    # P阶段: 规划
│   ├── development.md                 # D阶段: 开发
│   ├── review.md                      # R阶段: 评审
│   ├── summary.md                     # 迭代总结
│   └── workflows/                     # 工作流模板
│       ├── bug_fix.md                 # Bug修复流程
│       ├── feature_quick.md           # 快速功能开发
│       └── prototype.md               # 原型开发流程
│
├── standard/                          # 标准模式(P1→P2→D1→D2→R1)
│   ├── README.md                      # 模式使用指南
│   ├── p1_requirements.md             # P1阶段: 需求分析
│   ├── p2_design.md                   # P2阶段: 技术设计
│   ├── d1_implementation.md           # D1阶段: 功能开发
│   ├── d2_testing.md                  # D2阶段: 测试验证
│   ├── r1_release.md                  # R1阶段: 发布准备
│   └── template.yaml                  # 模式配置
│
├── complete/                          # 完整模式(S1→S2→...→S8)
│   ├── README.md                      # 模式使用指南
│   ├── s1_user_story.md               # S1: 用户故事
│   ├── s2_tasks_main.md               # S2: 主任务清单
│   ├── s2_tasks_group.md              # S2: 任务分组
│   ├── s3_testcases.md                # S3: 测试用例汇总
│   ├── s3_testcases_main.md           # S3: 单个测试用例
│   ├── s4_implementation.md           # S4: 功能实现汇总
│   ├── s4_implementation_report.md    # S4: 单个任务实现报告
│   ├── s5_test_report.md              # S5: 测试报告
│   ├── s6_codereview.md               # S6: 代码评审
│   ├── s7_demo_script.md              # S7: 演示脚本
│   ├── s8_summary_report.md           # S8: 迭代总结
│   ├── s8_learning_summary.md         # S8: 经验总结
│   └── template.yaml                  # 模式配置
│
├── smart/                             # 智能模式(动态流程)
│   ├── README.md                      # 模式使用指南
│   ├── dynamic_prompts.md             # 动态提示模板
│   ├── decision_engine.md             # 智能决策引擎
│   └── learning_system.md             # 学习优化系统
│
├── document_templates/                # 文档模板
│   ├── config_guide.md                # 配置指南模板
│   └── process_spec.md                # 流程规范模板
│
└── task-status-table.md               # 任务状态表模板
```

---

## 🎯 模式选择指南

### 快速选择表

| 判断因素 | Minimal | Standard | Complete | Smart |
|---------|---------|----------|----------|-------|
| **团队规模** | 1-3人 | 3-10人 | 10+人 | 任意 |
| **项目周期** | 0.5-2天 | 3-7天 | 1-4周 | 动态 |
| **复杂度** | 简单 | 中等 | 复杂 | 不确定 |
| **质量要求** | 基础 | 标准 | 严格 | 自适应 |
| **文档需求** | 最小 | 标准 | 完整 | 按需 |
| **适用场景** | 快速原型<br/>Bug修复 | 常规功能开发<br/>企业应用 | 大型项目<br/>关键系统 | 复杂度难预估<br/>AI辅助决策 |

### 详细对比

#### 🚀 Minimal 模式 (轻量级)

**流程**: P → D → R (3个阶段)

**优点**:
- ✅ 流程简单,上手快
- ✅ 开发速度快
- ✅ 适合小团队和快速迭代
- ✅ 文档负担轻

**缺点**:
- ❌ 质量保障相对薄弱
- ❌ 不适合大团队协作
- ❌ 文档可能不够完整

**典型场景**:
- 快速原型验证
- 紧急Bug修复
- 简单功能开发
- 个人或2-3人小项目

---

#### ⚙️ Standard 模式 (标准级)

**流程**: P1 → P2 → D1 → D2 → R1 (5个阶段)

**优点**:
- ✅ 流程完整度适中
- ✅ 质量和效率平衡好
- ✅ 适合中型团队
- ✅ 文档标准化

**缺点**:
- ❌ 不如Minimal灵活
- ❌ 不如Complete严格
- ❌ 需要一定流程学习成本

**典型场景**:
- Web/移动应用开发
- 企业内部系统
- 常规功能迭代
- 3-10人团队项目

---

#### 🏗️ Complete 模式 (完整级)

**流程**: S1 → S2 → S3 → (S4↔S5) → S6 → S7 → S8 (8个阶段)

**优点**:
- ✅ 流程最完整
- ✅ 质量保障最强
- ✅ 适合大团队和复杂项目
- ✅ 文档完整,可追溯性强

**缺点**:
- ❌ 流程复杂,学习成本高
- ❌ 执行周期长
- ❌ 小团队可能效率低
- ❌ 文档工作量大

**典型场景**:
- 大型企业级项目
- 金融、医疗等关键系统
- 高合规要求项目
- 10人以上大团队

---

#### 🧠 Smart 模式 (智能级)

**流程**: AI动态决策,自适应调整

**优点**:
- ✅ AI智能推荐最优流程
- ✅ 动态调整,适应变化
- ✅ 持续学习和优化
- ✅ 减少决策负担

**缺点**:
- ❌ 需要AI集成
- ❌ 决策透明度相对较低
- ❌ 依赖历史数据质量

**典型场景**:
- 复杂度难以预估的项目
- 需求可能快速变化
- 希望优化流程效率
- 有AI Agent支持的环境

---

## 📖 使用指南

### 1. 选择模式

根据项目特征选择合适的模式:

```bash
# 方式1: 手动选择
# 根据上表判断,选择合适的模式

# 方式2: 使用Smart模式让AI推荐
# AI会根据项目信息自动推荐最优模式
```

### 2. 初始化项目

```bash
# 使用 init 脚本初始化项目
python .aceflow/scripts/init.py --mode <minimal|standard|complete|smart>

# 或者手动创建目录结构
mkdir -p aceflow_result/iter_001/{阶段目录}
```

### 3. 使用模板

**方式1: 复制模板**
```bash
# 复制对应模式的模板到输出目录
cp .aceflow/templates/standard/p1_requirements.md \
   aceflow_result/iter_001/P1_requirements/requirements.md
```

**方式2: AI自动生成**
```markdown
# AI会根据模板格式自动生成内容
# 在 .clinerules 中配置 AceFlow 集成规则
# AI会自动使用对应模板
```

### 4. 填写模板

模板中使用 `{变量名}` 表示需要填充的内容:

- `{iteration_id}`: 迭代ID,如 "iter_001"
- `{start_time}`: 开始时间
- `{owner}`: 负责人
- `{completion_time}`: 完成时间
- 等等...

**示例**:
```markdown
# 原模板
**迭代ID**: `{iteration_id}`
**负责人**: `{owner}`

# 填充后
**迭代ID**: `iter_001`
**负责人**: 张三
```

---

## 🔧 模板变量说明

### 通用变量

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| `{iteration_id}` | 迭代ID | iter_001 |
| `{project_name}` | 项目名称 | 用户管理系统 |
| `{start_time}` | 开始时间 | 2025-11-06 09:00 |
| `{completion_time}` | 完成时间 | 2025-11-06 18:00 |
| `{owner}` | 负责人 | 张三 |
| `{reviewer}` | 审核人 | 李四 |
| `{version}` | 版本号 | v1.2.0 |

### Complete模式特有变量

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| `{task_id}` | 任务ID | TASK-001 |
| `{story_id}` | 用户故事ID | US-001 |
| `{test_id}` | 测试用例ID | TC-001 |
| `{commit_hash}` | Git提交哈希 | abc1234 |

### Smart模式特有变量

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| `{complexity_score}` | 复杂度评分 | 45 |
| `{recommended_mode}` | 推荐模式 | standard |
| `{confidence}` | 置信度 | 0.85 |
| `{reasoning}` | 推荐理由 | 中等复杂度,适合标准流程 |

---

## 🎨 模板自定义

### 1. 修改现有模板

可以直接修改 `templates/` 目录下的模板文件:

```bash
# 编辑模板
vim .aceflow/templates/standard/p1_requirements.md

# 添加自定义章节
# 调整章节顺序
# 修改字段名称
```

### 2. 创建自定义模式

```bash
# 1. 复制现有模式
cp -r .aceflow/templates/standard .aceflow/templates/my_custom

# 2. 修改模板
# 根据团队需求调整模板内容

# 3. 更新配置
# 在 config.yaml 中添加自定义模式配置
```

### 3. 版本控制

建议将自定义模板纳入版本控制:

```bash
git add .aceflow/templates/my_custom/
git commit -m "Add custom workflow template"
```

---

## 💡 最佳实践

### 1. 模板使用建议

**✅ 推荐做法**:
- 根据实际需要调整模板内容
- 保持模板格式一致性
- 及时更新模板(基于经验改进)
- 团队共同维护模板库

**❌ 不推荐做法**:
- 完全照搬模板不做调整
- 频繁大幅修改模板格式
- 不同项目使用不同模板版本
- 模板过于复杂难以使用

### 2. 文档填写建议

**简洁明了**:
- 避免冗长描述
- 使用表格和列表
- 重点突出关键信息

**持续更新**:
- 及时记录变更
- 保持文档最新
- 定期review和清理

**团队协作**:
- 明确文档负责人
- 建立Review机制
- 统一术语和格式

### 3. 模式切换建议

**何时考虑切换模式**:
- ✅ 发现当前模式明显不适合
- ✅ 项目复杂度评估有误
- ✅ 团队规模发生重大变化
- ✅ 质量要求发生变化

**如何平滑切换**:
- 在迭代边界切换(不要中途切换)
- 保留已完成的文档
- 团队培训新模式
- 试运行1-2个迭代

---

## 📚 相关文档

- **主规范**: [aceflow-spec_v3.0.md](../aceflow-spec_v3.0.md) - AceFlow v3.0完整规范
- **v2规范**: [aceflow-spec_v2.0.md](../aceflow-spec_v2.0.md) - v2版本参考
- **配置指南**: [document_templates/config_guide.md](document_templates/config_guide.md)
- **流程规范**: [document_templates/process_spec.md](document_templates/process_spec.md)

---

## 🔄 模板版本历史

### v3.0.0 (2025-11-06)
- ✨ 新增 Standard 模式完整模板(5个阶段)
- ✨ 新增 Smart 模式智能决策系统
- ✨ 重构 Complete 模式模板组织
- ✨ 改进 Minimal 模式工作流模板
- 📝 完善所有模板的变量说明和示例

### v2.0.0 (2025-07)
- ✨ 初始版本
- ✨ Complete 模式8阶段模板
- ✨ Minimal 模式基础模板

---

## 📞 支持和反馈

如有问题或建议,请:
- 📧 提交Issue: https://github.com/aceflow/aceflow/issues
- 💬 加入讨论: https://community.aceflow.dev
- 📖 查看文档: https://docs.aceflow.dev

---

**© 2025 AceFlow Team. All rights reserved.**
