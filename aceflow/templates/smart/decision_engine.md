# Smart模式智能决策引擎

## 决策算法

### 1. 复杂度评分算法

```python
def calculate_complexity_score(task_info):
    """
    计算任务复杂度总分

    Args:
        task_info: 任务信息字典

    Returns:
        complexity_score: 复杂度总分(0-100)
        breakdown: 各维度得分详情
    """

    # 技术复杂度 (权重: 25%)
    tech_score = assess_technical_complexity(
        tech_stack=task_info['tech_stack'],
        new_technology=task_info['new_technology'],
        integration_count=task_info['integration_count']
    )

    # 业务复杂度 (权重: 25%)
    business_score = assess_business_complexity(
        business_rules=task_info['business_rules'],
        user_scenarios=task_info['user_scenarios'],
        edge_cases=task_info['edge_cases']
    )

    # 团队能力 (权重: 20%)
    team_score = assess_team_capability(
        team_size=task_info['team_size'],
        experience_level=task_info['experience_level'],
        tech_familiarity=task_info['tech_familiarity']
    )

    # 时间约束 (权重: 15%)
    time_score = assess_time_constraint(
        deadline=task_info['deadline'],
        urgency=task_info['urgency']
    )

    # 质量要求 (权重: 15%)
    quality_score = assess_quality_requirement(
        quality_level=task_info['quality_level'],
        compliance=task_info['compliance'],
        security_level=task_info['security_level']
    )

    # 计算加权总分
    complexity_score = (
        tech_score * 0.25 +
        business_score * 0.25 +
        team_score * 0.20 +
        time_score * 0.15 +
        quality_score * 0.15
    )

    breakdown = {
        'technical': tech_score,
        'business': business_score,
        'team': team_score,
        'time': time_score,
        'quality': quality_score
    }

    return complexity_score, breakdown


def assess_technical_complexity(tech_stack, new_technology, integration_count):
    """评估技术复杂度"""
    score = 0

    # 技术栈复杂度
    complex_techs = ['AI/ML', 'Blockchain', '分布式系统', '实时计算']
    if any(tech in tech_stack for tech in complex_techs):
        score += 30

    # 新技术使用
    if new_technology:
        score += 25

    # 集成复杂度
    score += min(integration_count * 5, 25)

    # 跨平台要求
    if len(tech_stack.get('platforms', [])) > 2:
        score += 20

    return min(score, 100)
```

### 2. 模式推荐算法

```python
def recommend_workflow_mode(complexity_score, project_context):
    """
    基于复杂度和项目上下文推荐工作流模式

    Args:
        complexity_score: 复杂度评分
        project_context: 项目上下文信息

    Returns:
        recommended_mode: 推荐的模式
        confidence: 推荐置信度
        reasoning: 推荐理由
    """

    team_size = project_context.get('team_size', 3)
    urgency = project_context.get('urgency', 'normal')
    quality_level = project_context.get('quality_level', 'standard')

    # 紧急情况优先
    if urgency == 'emergency':
        return {
            'mode': 'minimal',
            'path': 'emergency',  # S4↔S5→S8
            'confidence': 0.95,
            'reasoning': '紧急情况,采用紧急修复流程'
        }

    # 基于复杂度评分推荐
    if complexity_score <= 30:
        mode = 'minimal'
        confidence = 0.9
        reasoning = '任务简单,适合轻量级流程'

    elif complexity_score <= 60:
        mode = 'standard'
        confidence = 0.85
        reasoning = '中等复杂度,推荐标准流程'

    else:
        mode = 'complete'
        confidence = 0.9
        reasoning = '高复杂度任务,需要完整流程保障'

    # 团队规模调整
    if team_size >= 10 and mode == 'standard':
        mode = 'complete'
        reasoning += ', 大团队需要更严格的流程管理'

    elif team_size <= 3 and mode == 'complete':
        confidence -= 0.1
        reasoning += ', 小团队执行完整流程可能效率较低,建议评估必要性'

    # 质量要求调整
    if quality_level == 'critical' and mode != 'complete':
        mode = 'complete'
        confidence = 0.95
        reasoning = '关键系统,必须采用完整流程确保质量'

    return {
        'mode': mode,
        'confidence': confidence,
        'reasoning': reasoning,
        'alternative_options': _generate_alternatives(complexity_score, project_context)
    }


def _generate_alternatives(complexity_score, project_context):
    """生成备选方案"""
    alternatives = []

    if 25 <= complexity_score <= 35:
        alternatives.append({
            'mode': 'minimal',
            'condition': '如果时间非常紧迫',
            'trade_off': '牺牲部分文档完整性'
        })
        alternatives.append({
            'mode': 'standard',
            'condition': '如果质量要求较高',
            'trade_off': '增加1-2天周期'
        })

    return alternatives
```

### 3. 动态调整算法

```python
def evaluate_adjustment_need(current_state, execution_data):
    """
    评估是否需要调整流程

    Args:
        current_state: 当前流程状态
        execution_data: 执行数据

    Returns:
        adjustment_needed: 是否需要调整
        adjustment_plan: 调整方案
    """

    signals = []

    # 检查进度偏差
    progress_deviation = (
        execution_data['actual_time'] / execution_data['estimated_time'] - 1
    )
    if progress_deviation > 0.3:
        signals.append({
            'type': 'progress_delay',
            'severity': 'high',
            'message': f'进度延迟{progress_deviation*100:.1f}%'
        })

    # 检查质量指标
    if execution_data['test_coverage'] < 0.7:
        signals.append({
            'type': 'quality_issue',
            'severity': 'medium',
            'message': '测试覆盖率偏低'
        })

    # 检查Bug率
    bug_rate = execution_data['bug_count'] / execution_data['total_tasks']
    if bug_rate > 0.2:
        signals.append({
            'type': 'quality_issue',
            'severity': 'high',
            'message': f'Bug率过高({bug_rate*100:.1f}%)'
        })

    # 生成调整建议
    if signals:
        adjustment_plan = _generate_adjustment_plan(
            current_state, signals
        )
        return True, adjustment_plan

    return False, None
```

### 4. 智能提示增强

```python
def enhance_stage_prompt(base_prompt, context, learning_data):
    """
    基于上下文和历史学习数据增强阶段提示

    Args:
        base_prompt: 基础提示词模板
        context: 当前上下文
        learning_data: 历史学习数据

    Returns:
        enhanced_prompt: 增强后的提示词
    """

    enhancements = []

    # 基于项目类型增强
    if context['project_type'] == 'financial':
        enhancements.append("""
        **金融行业特别注意**:
        - 严格遵守数据安全和隐私保护规范
        - 所有计算必须精确到分,避免浮点数误差
        - 实现完整的审计日志
        - 考虑监管合规要求
        """)

    # 基于技术栈增强
    if 'microservices' in context['tech_stack']:
        enhancements.append("""
        **微服务架构注意**:
        - 明确服务边界和职责
        - 设计服务间通信协议
        - 考虑服务降级和熔断策略
        - 实现分布式追踪
        """)

    # 基于历史问题增强
    common_issues = learning_data.get('common_issues', [])
    if 'performance' in common_issues:
        enhancements.append("""
        **性能优化提醒**(基于历史经验):
        - 提前进行性能测试,不要等到最后
        - 关注数据库查询性能
        - 考虑缓存策略
        - 监控接口响应时间
        """)

    # 合并增强内容
    enhanced_prompt = base_prompt
    if enhancements:
        enhanced_prompt += "\n\n## 智能提醒\n\n"
        enhanced_prompt += "\n".join(enhancements)

    return enhanced_prompt
```

---

## 决策示例

### 示例1: Web应用开发

```yaml
输入:
  task_description: "开发企业内部管理系统"
  team_size: 5
  tech_stack: ["Vue3", "Spring Boot", "MySQL"]
  deadline: "2周"
  quality_level: "standard"

分析结果:
  complexity_score: 45
  breakdown:
    technical: 40 (常规技术栈)
    business: 50 (中等业务复杂度)
    team: 60 (团队能力良好)
    time: 50 (时间适中)
    quality: 40 (标准质量要求)

推荐:
  mode: "standard"
  confidence: 0.88
  reasoning: "中等复杂度,5人团队,2周周期,适合标准流程"
  estimated_duration: "10-14天"
  stages:
    - P1: 需求分析 (1天)
    - P2: 技术设计 (1天)
    - D1: 功能开发 (6天)
    - D2: 测试验证 (2天)
    - R1: 发布准备 (1天)
```

### 示例2: 紧急Bug修复

```yaml
输入:
  task_description: "生产环境支付接口异常"
  team_size: 2
  urgency: "emergency"
  impact: "high"

分析结果:
  complexity_score: 30
  urgency_override: true

推荐:
  mode: "minimal"
  path: "emergency"
  confidence: 0.95
  reasoning: "紧急生产问题,快速定位和修复"
  estimated_duration: "2-4小时"
  stages:
    - S4: 问题定位和修复
    - S5: 快速测试验证
    - S8: 问题总结和预防
```

### 示例3: 大型项目

```yaml
输入:
  task_description: "电商平台核心交易系统重构"
  team_size: 15
  tech_stack: ["微服务", "Kafka", "Redis", "Elasticsearch"]
  deadline: "3个月"
  quality_level: "critical"

分析结果:
  complexity_score: 85
  breakdown:
    technical: 85 (微服务+多技术栈)
    business: 90 (核心业务逻辑复杂)
    team: 75 (大团队协作)
    time: 70 (周期较长需严格管理)
    quality: 95 (关键系统)

推荐:
  mode: "complete"
  confidence: 0.95
  reasoning: "大型关键系统,必须采用完整流程确保质量"
  estimated_duration: "10-12周"
  stages:
    - S1: 用户故事 (1周)
    - S2: 任务拆分 (1周)
    - S3: 测试设计 (1周)
    - S4-S5: 开发测试循环 (6周)
    - S6: 代码评审 (1周)
    - S7: 演示反馈 (0.5周)
    - S8: 总结归档 (0.5周)

  special_considerations:
    - 每周进行进度评审
    - 每2周进行技术评审
    - 实施严格的代码审查
    - 建立完整的监控和告警体系
```

---

## 持续学习

### 学习数据收集

每次迭代结束后,收集以下数据:

```python
learning_data = {
    'iteration_id': 'iter_001',
    'mode_used': 'standard',
    'complexity_score': 45,
    'actual_complexity': 52,  # 实际执行中发现的复杂度

    'time_estimation': {
        'estimated': 14,  # 天
        'actual': 16,     # 天
        'deviation': 0.14  # 14%
    },

    'quality_metrics': {
        'test_coverage': 0.85,
        'bug_count': 8,
        'code_quality_score': 9.2
    },

    'issues_encountered': [
        {
            'type': 'technical',
            'description': '第三方API不稳定',
            'impact': 'medium',
            'resolution': '实现重试机制和降级方案'
        }
    ],

    'team_feedback': {
        'workflow_satisfaction': 4.2,  # 1-5分
        'documentation_quality': 4.5,
        'improvement_suggestions': [
            '希望增加更多示例',
            'API设计阶段可以更详细'
        ]
    }
}
```

### 模型优化

```python
def update_decision_model(learning_data_list):
    """
    基于历史数据优化决策模型
    """

    # 分析预估准确性
    estimation_errors = [
        data['time_estimation']['deviation']
        for data in learning_data_list
    ]
    avg_error = np.mean(estimation_errors)

    # 如果系统性地低估复杂度,调整评分算法
    if avg_error > 0.2:
        adjust_complexity_weights(increase_by=0.1)

    # 识别高风险模式
    high_risk_patterns = identify_risk_patterns(learning_data_list)
    update_risk_detection_rules(high_risk_patterns)

    # 优化提示词
    effective_prompts = identify_effective_prompts(learning_data_list)
    update_prompt_templates(effective_prompts)
```
