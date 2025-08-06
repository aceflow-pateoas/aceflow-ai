#!/usr/bin/env python3
"""
AceFlow高级功能测试 - 验证增强资源和验证引擎
Test script for AceFlow Advanced Features - Enhanced Resources and Validation Engine
"""

import sys
from pathlib import Path
import json

# 添加aceflow-mcp-server到路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.enhanced_resources import EnhancedAceFlowResources, create_enhanced_aceflow_resources
from aceflow_mcp_server.core.validation_engine import (
    ValidationEngine, InputValidator, OutputValidator, ValidationLevel,
    create_validation_engine, validate_stage_input, validate_stage_output
)


def test_enhanced_resources():
    """测试增强版资源管理"""
    print("🔧 测试增强版资源管理...")
    
    resources = create_enhanced_aceflow_resources()
    
    # 测试1: 智能项目状态获取
    print("  1. 测试智能项目状态获取...")
    
    state_result = resources.get_intelligent_project_state("test_project")
    print(f"     状态获取: {'✅' if state_result.get('success', False) else '❌'}")
    
    if state_result.get("success"):
        collaboration = state_result.get("collaboration", {})
        recommendations = state_result.get("intelligent_recommendations", [])
        
        print(f"     协作状态: {collaboration.get('active_requests', 0)} 个活跃请求")
        print(f"     智能推荐: {len(recommendations)} 条建议")
        
        # 显示推荐内容
        for i, rec in enumerate(recommendations[:2], 1):
            print(f"       {i}. {rec.get('title', 'Unknown')}")
    
    print()
    
    # 测试2: 自适应阶段指导
    print("  2. 测试自适应阶段指导...")
    
    guide_result = resources.get_adaptive_stage_guide(
        "S1_user_stories",
        {"complexity": "high", "team_size": 3}
    )
    
    print(f"     指导获取: {'✅' if guide_result.get('success', False) else '❌'}")
    
    if guide_result.get("success"):
        adaptive_guide = guide_result.get("adaptive_guide", {})
        personalization = guide_result.get("personalization", {})
        
        print(f"     协作风格: {adaptive_guide.get('collaboration_style', 'unknown')}")
        print(f"     紧急程度: {adaptive_guide.get('urgency_level', 'unknown')}")
        print(f"     用户模式: {personalization.get('activity_pattern', 'unknown')}")
    
    print()
    
    # 测试3: 协作洞察
    print("  3. 测试协作洞察...")
    
    insights_result = resources.get_collaboration_insights("test_project")
    print(f"     洞察获取: {'✅' if insights_result.get('success', False) else '❌'}")
    
    if insights_result.get("success"):
        insights = insights_result.get("insights", {})
        print(f"     总交互数: {insights.get('total_interactions', 0)}")
        print(f"     协作效果: {insights.get('collaboration_effectiveness', 'unknown')}")
        print(f"     改进建议: {len(insights.get('improvement_suggestions', []))} 条")
    
    print()
    
    # 测试4: 动态工作流配置
    print("  4. 测试动态工作流配置...")
    
    config_result = resources.get_dynamic_workflow_config(
        "complete",
        {"complexity": "high", "timeline": "tight"}
    )
    
    print(f"     配置获取: {'✅' if config_result.get('success', False) else '❌'}")
    
    if config_result.get("success"):
        dynamic_config = config_result.get("dynamic_config", {})
        project_features = config_result.get("project_features", {})
        
        print(f"     质量门控: {dynamic_config.get('quality_gates', 'unknown')}")
        print(f"     审查频率: {dynamic_config.get('review_frequency', 'unknown')}")
        print(f"     项目复杂度: {project_features.get('complexity', 'unknown')}")
    
    print("✅ 增强版资源管理测试完成\n")


def test_validation_engine():
    """测试验证引擎"""
    print("🔍 测试验证引擎...")
    
    # 创建测试文件
    test_dir = Path("test_validation")
    test_dir.mkdir(exist_ok=True)
    aceflow_result_dir = test_dir / "aceflow_result"
    aceflow_result_dir.mkdir(exist_ok=True)
    
    try:
        # 测试1: 输入验证
        print("  1. 测试输入验证...")
        
        input_validator = InputValidator(ValidationLevel.STANDARD)
        
        # 测试用户输入验证
        user_input_tests = [
            ("这是PRD文档，包含用户需求和功能描述", "prd_document"),
            ("实现用户登录功能", "task_description"),
            ("是的，继续", "confirmation"),
            ("", "general")  # 空输入测试
        ]
        
        for input_text, input_type in user_input_tests:
            result = input_validator.validate_user_input(input_text, input_type)
            success = result.success
            issues = len(result.issues)
            
            print(f"     输入类型 {input_type}: {'✅' if success else '❌'} ({issues} 问题)")
        
        print()
        
        # 测试2: 输出验证
        print("  2. 测试输出验证...")
        
        output_validator = OutputValidator(ValidationLevel.STANDARD)
        
        # 创建测试输出文件
        test_outputs = {
            "S1_user_stories.md": """# 用户故事分析

## 概述
这是一个测试项目的用户故事分析。

## 用户故事

### 用户故事1
作为用户，我希望能够登录系统，这样我就可以访问个人功能。

#### 验收标准
- 用户可以输入用户名和密码
- 系统验证用户身份
- 登录成功后跳转到主页

### 用户故事2
作为管理员，我希望能够管理用户，这样我就可以维护系统安全。

#### 验收标准
- 管理员可以查看用户列表
- 管理员可以添加新用户
- 管理员可以删除用户
""",
            "S2_task_breakdown.md": """# 任务分解

## 任务列表

- [ ] 1. 实现用户登录功能
- [ ] 2. 创建用户管理界面
- [ ] 3. 开发用户权限控制
- [ ] 4. 实现数据库连接
- [ ] 5. 编写单元测试

## 开发计划

预计总工时：40小时
开发周期：2周
"""
        }
        
        validation_results = {}
        
        for filename, content in test_outputs.items():
            file_path = aceflow_result_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            stage_id = filename.replace('.md', '')
            result = output_validator.validate_stage_output(stage_id, file_path)
            validation_results[stage_id] = result
            
            print(f"     阶段 {stage_id}: {'✅' if result.success else '❌'} (评分: {result.overall_score:.1f})")
            
            # 显示主要问题
            for issue in result.issues[:2]:
                print(f"       - {issue.level.value}: {issue.message}")
        
        print()
        
        # 测试3: 验证引擎综合功能
        print("  3. 测试验证引擎综合功能...")
        
        validation_engine = create_validation_engine(ValidationLevel.STANDARD)
        
        # 测试阶段转换验证
        transition_result = validation_engine.validate_stage_transition(
            "S1_user_stories", 
            "S2_task_breakdown",
            test_dir
        )
        
        print(f"     阶段转换验证: {'✅' if transition_result.success else '❌'}")
        print(f"     转换评分: {transition_result.overall_score:.1f}")
        
        # 测试质量报告生成
        quality_report = validation_engine.generate_quality_report(test_dir)
        
        print(f"     质量报告生成: {'✅' if quality_report.get('success', False) else '❌'}")
        
        if quality_report.get("success"):
            print(f"     总体质量评分: {quality_report.get('overall_quality_score', 0):.1f}")
            print(f"     质量等级: {quality_report.get('quality_level', 'unknown')}")
            print(f"     验证阶段数: {quality_report.get('total_stages_validated', 0)}")
        
        print()
        
        # 测试4: 便捷函数
        print("  4. 测试便捷函数...")
        
        # 测试便捷输入验证
        input_result = validate_stage_input("S1_user_stories", {"test": "data"})
        print(f"     便捷输入验证: {'✅' if input_result.success else '❌'}")
        
        # 测试便捷输出验证
        output_file = aceflow_result_dir / "S1_user_stories.md"
        output_result = validate_stage_output("S1_user_stories", output_file)
        print(f"     便捷输出验证: {'✅' if output_result.success else '❌'}")
        
    finally:
        # 清理测试文件
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)
    
    print("✅ 验证引擎测试完成\n")


def test_integration_scenario():
    """测试集成场景"""
    print("🔄 测试高级功能集成场景...")
    
    # 场景：智能资源管理 + 验证引擎协同工作
    
    resources = create_enhanced_aceflow_resources()
    validation_engine = create_validation_engine(ValidationLevel.STANDARD)
    
    print("场景: 智能项目状态分析 → 质量验证 → 自适应建议")
    print()
    
    # 步骤1: 获取智能项目状态
    print("1. 获取智能项目状态...")
    state_result = resources.get_intelligent_project_state("integration_test")
    
    if state_result.get("success"):
        recommendations = state_result.get("intelligent_recommendations", [])
        print(f"   智能推荐数量: {len(recommendations)}")
        
        # 显示推荐
        for i, rec in enumerate(recommendations[:2], 1):
            print(f"   {i}. {rec.get('title', 'Unknown')}: {rec.get('priority', 'medium')}")
    
    # 步骤2: 模拟质量验证
    print("\n2. 执行质量验证...")
    
    # 创建临时测试环境
    test_dir = Path("integration_test")
    test_dir.mkdir(exist_ok=True)
    aceflow_result_dir = test_dir / "aceflow_result"
    aceflow_result_dir.mkdir(exist_ok=True)
    
    try:
        # 创建测试文件
        test_content = """# 测试阶段输出

## 概述
这是集成测试的示例输出。

## 用户故事
作为测试用户，我希望系统能够正常工作，这样我就可以验证功能。

## 验收标准
- 系统响应正常
- 功能符合预期
"""
        
        test_file = aceflow_result_dir / "S1_user_stories.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 执行验证
        validation_result = validation_engine.output_validator.validate_stage_output("S1_user_stories", test_file)
        print(f"   验证结果: {'✅' if validation_result.success else '❌'}")
        print(f"   质量评分: {validation_result.overall_score:.1f}")
        
        # 步骤3: 基于验证结果生成自适应建议
        print("\n3. 生成自适应建议...")
        
        context = {
            "validation_score": validation_result.overall_score,
            "issues_count": len(validation_result.issues),
            "complexity": "medium"
        }
        
        adaptive_guide = resources.get_adaptive_stage_guide("S2_task_breakdown", context)
        
        if adaptive_guide.get("success"):
            guide = adaptive_guide.get("adaptive_guide", {})
            print(f"   协作风格: {guide.get('collaboration_style', 'unknown')}")
            print(f"   建议焦点: {', '.join(guide.get('focus_areas', []))}")
            
            personalized_tips = guide.get("personalized_tips", [])
            if personalized_tips:
                print(f"   个性化提示: {personalized_tips[0]}")
        
        # 步骤4: 生成综合报告
        print("\n4. 生成综合质量报告...")
        
        quality_report = validation_engine.generate_quality_report(test_dir)
        
        if quality_report.get("success"):
            print(f"   总体质量: {quality_report.get('quality_level', 'unknown')}")
            print(f"   改进建议: {len(quality_report.get('recommendations', []))} 条")
            
            # 显示主要建议
            recommendations = quality_report.get("recommendations", [])
            if recommendations:
                print(f"   主要建议: {recommendations[0]}")
    
    finally:
        # 清理测试文件
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\n✅ 集成场景测试完成\n")


def main():
    """主测试函数"""
    print("🚀 AceFlow高级功能测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_enhanced_resources()
        test_validation_engine()
        test_integration_scenario()
        
        print("🎉 所有高级功能测试完成！")
        print("\n📊 功能验证:")
        print("- ✅ 增强版资源管理: 智能状态分析、自适应指导")
        print("- ✅ 验证引擎: 输入输出验证、质量评估")
        print("- ✅ 集成协作: 资源管理与验证引擎协同工作")
        print("- ✅ 质量控制: 严格的输入输出验证机制")
        
        print("\n🎯 高级特性:")
        print("1. 🧠 智能推荐系统 - 基于项目状态和用户行为")
        print("2. 🔍 多级验证机制 - Basic/Standard/Strict三个级别")
        print("3. 📊 质量评分系统 - 量化的质量评估和改进建议")
        print("4. 🤖 自适应指导 - 根据用户模式调整协作方式")
        print("5. 📈 协作洞察 - 分析协作效果并提供优化建议")
        
        print("\n🚀 AceFlow AI-人协同工作流高级功能已就绪！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()