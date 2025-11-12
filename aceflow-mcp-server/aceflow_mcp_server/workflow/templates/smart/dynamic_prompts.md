# Smart 模式动态提示模板

## 任务分析提示

```markdown
# AI任务分析

## 输入信息
- **任务描述**: {task_description}
- **项目上下文**: {project_context}
- **团队规模**: {team_size}
- **时间约束**: {time_constraint}

## 分析维度

### 1. 复杂度评估
请分析任务的复杂度,从以下维度打分(1-10分):
- **技术复杂度**: 涉及的技术难度
- **业务复杂度**: 业务逻辑的复杂程度
- **集成复杂度**: 与其他系统的集成难度
- **数据复杂度**: 数据处理和迁移的复杂度

**总分**: {complexity_score}/40

### 2. 团队能力评估
- **团队经验**: {team_experience}
- **技术栈熟悉度**: {tech_stack_familiarity}
- **协作成熟度**: {collaboration_maturity}

### 3. 风险识别
识别潜在风险:
- [ ] 技术风险
- [ ] 时间风险
- [ ] 资源风险
- [ ] 依赖风险

### 4. 流程推荐

基于以上分析,推荐执行流程:

**如果 complexity_score ≤ 15**:
→ 推荐 **Minimal 模式** (P→D→R)
- 理由: 任务简单,快速迭代即可
- 预计周期: 0.5-2天
- 团队规模: 1-3人

**如果 15 < complexity_score ≤ 28**:
→ 推荐 **Standard 模式** (P1→P2→D1→D2→R1)
- 理由: 需要标准化流程管理
- 预计周期: 3-7天
- 团队规模: 3-10人

**如果 complexity_score > 28**:
→ 推荐 **Complete 模式** (S1→S2→...→S8)
- 理由: 复杂度高,需要完整流程保障
- 预计周期: 1-4周
- 团队规模: 10+人

## 输出决策

**推荐模式**: {recommended_mode}
**置信度**: {confidence}%
**主要理由**: {main_reason}

**执行计划建议**:
1. {step_1}
2. {step_2}
3. {step_3}

**风险应对建议**:
- {risk_mitigation_1}
- {risk_mitigation_2}
```

---

## 动态阶段调整提示

```markdown
# 阶段动态调整

## 当前状态
- **当前模式**: {current_mode}
- **当前阶段**: {current_stage}
- **执行进度**: {progress}%
- **遇到的问题**: {issues}

## 调整分析

### 是否需要调整流程?

**触发条件检查**:
- [ ] 进度严重落后(>30%)
- [ ] 发现重大技术风险
- [ ] 需求发生重大变更
- [ ] 团队资源发生变化
- [ ] 质量指标不达标

**如果需要调整**:

### 选项1: 简化流程
适用场景: 时间紧迫,可以适当降低非核心要求

调整建议:
- 合并相近阶段
- 跳过非必要文档
- 聚焦核心功能

### 选项2: 增强流程
适用场景: 发现重大风险,需要加强质量管控

调整建议:
- 增加评审环节
- 增加测试覆盖
- 增加技术调研

### 选项3: 切换模式
适用场景: 当前模式明显不适合

建议切换:
- 从Complete→Standard: 复杂度评估过高
- 从Standard→Minimal: 任务比预期简单
- 从Minimal→Standard: 发现隐藏复杂度

## 调整决策

**是否调整**: Yes / No
**调整方案**: {adjustment_plan}
**预期效果**: {expected_outcome}
```

---

## 智能提示生成

```markdown
# 阶段智能提示

## 基于上下文的提示增强

### 输入上下文
- **项目类型**: {project_type}
- **技术栈**: {tech_stack}
- **团队经验**: {team_experience}
- **历史问题**: {historical_issues}

### 智能提示生成规则

#### For 需求分析阶段:
- 如果 project_type == "B2C": 强调用户体验和场景设计
- 如果 project_type == "B2B": 强调业务流程和集成接口
- 如果 team_experience == "低": 提供需求分析模板和示例
- 如果 historical_issues 包含"需求变更": 强调需求确认和签字流程

#### For 技术设计阶段:
- 如果 tech_stack 包含新技术: 增加技术调研和POC环节
- 如果 team_experience == "低": 提供架构设计参考和最佳实践
- 如果 historical_issues 包含"性能问题": 强调性能设计和测试

#### For 开发阶段:
- 如果 tech_stack 包含新技术: 增加代码review频率
- 如果 team_size > 5: 强调分支管理和冲突解决
- 如果 historical_issues 包含"代码质量": 强调编码规范和静态检查

#### For 测试阶段:
- 如果 project_type == "金融/医疗": 强调安全测试和合规检查
- 如果 historical_issues 包含"生产Bug": 增加回归测试和压力测试
- 如果 team_experience == "低": 提供测试用例模板

## 生成的智能提示

**当前阶段**: {current_stage}
**智能提示内容**:

{dynamic_prompt_content}

**关键关注点**:
1. {key_point_1}
2. {key_point_2}
3. {key_point_3}

**常见陷阱提醒**:
- ⚠️ {pitfall_1}
- ⚠️ {pitfall_2}
```

---

## 学习和优化提示

```markdown
# 流程学习和优化

## 数据收集

### 本次迭代数据
- **实际耗时 vs 预估耗时**: {actual_vs_estimated}
- **质量指标**: {quality_metrics}
- **遇到的问题**: {issues_encountered}
- **团队反馈**: {team_feedback}

### 历史数据对比
- **平均完成时间**: {avg_completion_time}
- **平均质量评分**: {avg_quality_score}
- **常见问题模式**: {common_issue_patterns}

## 学习分析

### 成功模式识别
**识别到的成功模式**:
1. {success_pattern_1}
2. {success_pattern_2}

**可复用的实践**:
- {best_practice_1}
- {best_practice_2}

### 问题模式识别
**识别到的问题模式**:
1. {issue_pattern_1}
2. {issue_pattern_2}

**根因分析**:
- {root_cause_1}
- {root_cause_2}

## 优化建议

### 流程优化
**建议优化的环节**:
1. {optimization_1}
   - 当前问题: {current_issue}
   - 优化方案: {solution}
   - 预期效果: {expected_improvement}

### 模板优化
**建议更新的模板**:
- {template_1}: {update_reason}
- {template_2}: {update_reason}

### 提示词优化
**建议优化的提示词**:
- 阶段: {stage}
- 当前提示效果: {current_effectiveness}
- 优化建议: {optimization_suggestion}

## 知识沉淀

**记忆池更新**:
- [ ] 新增决策记录: {decision_record}
- [ ] 新增问题解决方案: {solution_record}
- [ ] 新增最佳实践: {best_practice_record}
- [ ] 更新风险清单: {risk_update}

**下次执行建议**:
基于本次学习,下次遇到类似任务时建议:
1. {suggestion_1}
2. {suggestion_2}
3. {suggestion_3}
```
