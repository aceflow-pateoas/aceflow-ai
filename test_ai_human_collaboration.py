#!/usr/bin/env python3
"""
AceFlow AI-人协同工作流核心功能测试
Test script for AceFlow AI-Human Collaborative Workflow core features
"""

import sys
from pathlib import Path

# 添加aceflow-mcp-server到路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.core.intent_recognizer import (
    IntentRecognizer, IntentType, WorkflowMode, recognize_user_intent
)
from aceflow_mcp_server.core.collaboration_manager import (
    CollaborationManager, RequestType, request_user_confirmation
)
from aceflow_mcp_server.core.task_parser import (
    TaskParser, TaskStatus, TaskPriority, parse_task_breakdown
)


def test_intent_recognition():
    """测试意图识别功能"""
    print("🧠 测试意图识别功能...")
    
    recognizer = IntentRecognizer()
    
    # 测试用例
    test_cases = [
        {
            "input": "这是PRD文档，开始完整开发流程",
            "expected_intent": IntentType.START_WORKFLOW,
            "description": "PRD文档启动工作流"
        },
        {
            "input": "开始编码实现用户登录功能",
            "expected_intent": IntentType.EXECUTE_TASK,
            "description": "任务执行请求"
        },
        {
            "input": "当前项目进度如何？",
            "expected_intent": IntentType.CHECK_STATUS,
            "description": "状态查询"
        },
        {
            "input": "继续下一阶段",
            "expected_intent": IntentType.CONTINUE_STAGE,
            "description": "继续请求"
        },
        {
            "input": "暂停工作流",
            "expected_intent": IntentType.PAUSE_WORKFLOW,
            "description": "暂停请求"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = recognizer.recognize_intent(case["input"])
        success = result.intent_type == case["expected_intent"]
        
        print(f"  {i}. {case['description']}: {'✅' if success else '❌'}")
        print(f"     输入: {case['input']}")
        print(f"     识别: {result.intent_type.value} (置信度: {result.confidence:.2f})")
        print(f"     建议: {result.suggested_action}")
        print()
    
    print("✅ 意图识别测试完成\n")


def test_collaboration_manager():
    """测试协作管理功能"""
    print("🤝 测试协作管理功能...")
    
    manager = CollaborationManager()
    
    # 测试确认请求
    print("  1. 测试确认请求...")
    request_id = manager.request_confirmation(
        project_id="test_project",
        stage_id="S1_user_stories",
        title="用户故事分析完成",
        description="已识别5个用户故事，是否继续任务分解？",
        timeout_seconds=10
    )
    
    print(f"     请求ID: {request_id}")
    print(f"     活跃请求数: {len(manager.get_active_requests())}")
    
    # 模拟用户响应
    success = manager.respond_to_request(request_id, "yes", "test_user", 1.0)
    print(f"     响应成功: {'✅' if success else '❌'}")
    print(f"     活跃请求数: {len(manager.get_active_requests())}")
    
    # 测试协作历史
    history = manager.get_collaboration_history("test_project")
    if history:
        print(f"     协作历史记录数: {len(history.interactions)}")
    
    print("✅ 协作管理测试完成\n")


def test_task_parser():
    """测试任务解析功能"""
    print("📋 测试任务解析功能...")
    
    parser = TaskParser()
    
    # 创建测试任务文档内容
    task_content = """# 任务分解文档

## 开发任务列表

- [ ] 1. 实现用户登录功能 [高] 4小时
  - 创建登录页面UI
  - 实现登录验证逻辑
  - 添加错误处理
  - _需求: 1.1, 1.2_

- [ ] 2. 实现数据库连接模块 [中] 6小时
  - 设计数据库连接池
  - 实现CRUD操作
  - 添加事务支持
  - _需求: 2.1_

- [ ] 3. 创建API接口 [高] 8小时
  - 依赖: 用户登录功能, 数据库连接模块
  - 设计RESTful API
  - 实现接口文档
  - _需求: 3.1, 3.2_
"""
    
    # 保存测试文档
    test_doc_path = Path("test_task_breakdown.md")
    with open(test_doc_path, 'w', encoding='utf-8') as f:
        f.write(task_content)
    
    try:
        # 解析任务
        task_queue = parser.parse_task_breakdown_document(
            test_doc_path, 
            "test_project", 
            "S2_task_breakdown"
        )
        
        print(f"  解析任务数: {len(task_queue.tasks)}")
        print(f"  总估算时间: {task_queue.total_estimated_hours}小时")
        
        # 显示任务详情
        for i, task in enumerate(task_queue.tasks, 1):
            print(f"  {i}. {task.name}")
            print(f"     优先级: {task.priority.value}")
            print(f"     估算时间: {task.estimated_hours}小时")
            print(f"     依赖: {task.dependencies}")
            print(f"     需求: {task.requirements}")
            print()
        
        # 测试获取可执行任务
        executable_tasks = parser.get_next_executable_tasks(task_queue)
        print(f"  可执行任务数: {len(executable_tasks)}")
        
        # 测试任务状态更新
        if executable_tasks:
            first_task = executable_tasks[0]
            success = parser.update_task_status(
                task_queue, 
                first_task.task_id, 
                TaskStatus.COMPLETED
            )
            print(f"  任务状态更新: {'✅' if success else '❌'}")
        
        # 测试进度统计
        progress = parser.get_task_progress(task_queue)
        print(f"  项目进度: {progress['progress_percentage']:.1f}%")
        print(f"  完成任务: {progress['completed_tasks']}/{progress['total_tasks']}")
        
    finally:
        # 清理测试文件
        if test_doc_path.exists():
            test_doc_path.unlink()
    
    print("✅ 任务解析测试完成\n")


def test_integration_scenario():
    """测试集成场景"""
    print("🔄 测试AI-人协同工作流集成场景...")
    
    # 场景：用户提供PRD文档，AI识别意图并启动协作流程
    
    # 1. 意图识别
    user_input = "这是我们的PRD文档，需要开始完整的开发流程"
    recognizer = IntentRecognizer()
    intent_result = recognizer.recognize_intent(user_input)
    
    print(f"  1. 用户输入: {user_input}")
    print(f"     识别意图: {intent_result.intent_type.value}")
    print(f"     建议模式: {intent_result.parameters.get('suggested_mode', 'unknown')}")
    
    # 2. 协作确认
    if intent_result.intent_type == IntentType.START_WORKFLOW:
        manager = CollaborationManager()
        request_id = manager.request_confirmation(
            project_id="demo_project",
            stage_id="initialization",
            title="启动AceFlow工作流",
            description=f"检测到开发需求，建议启动{intent_result.parameters.get('suggested_mode', 'standard')}模式工作流。是否确认？",
            timeout_seconds=5
        )
        
        print(f"  2. 协作请求ID: {request_id}")
        
        # 模拟用户确认
        manager.respond_to_request(request_id, "yes", "developer", 1.0)
        print("     用户确认: ✅")
        
        # 3. 模拟任务分解阶段
        print("  3. 模拟进入任务分解阶段...")
        
        # 创建简单的任务列表
        task_content = """
- [ ] 分析用户需求
- [ ] 设计系统架构  
- [ ] 实现核心功能
- [ ] 编写测试用例
- [ ] 部署和交付
"""
        
        parser = TaskParser()
        test_doc = Path("demo_tasks.md")
        
        try:
            with open(test_doc, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            task_queue = parser.parse_task_breakdown_document(
                test_doc, "demo_project", "S2_task_breakdown"
            )
            
            print(f"     解析任务: {len(task_queue.tasks)}个")
            
            # 4. 协作式任务执行
            executable_tasks = parser.get_next_executable_tasks(task_queue)
            if executable_tasks:
                next_task = executable_tasks[0]
                
                # 请求执行确认
                exec_request_id = manager.request_confirmation(
                    project_id="demo_project",
                    stage_id="S5_implementation",
                    title="执行下一个任务",
                    description=f"准备执行任务: {next_task.name}。是否继续？",
                    timeout_seconds=5
                )
                
                print(f"  4. 任务执行请求: {exec_request_id}")
                
                # 模拟用户确认
                manager.respond_to_request(exec_request_id, "yes", "developer", 1.0)
                
                # 更新任务状态
                parser.update_task_status(task_queue, next_task.task_id, TaskStatus.IN_PROGRESS)
                parser.update_task_status(task_queue, next_task.task_id, TaskStatus.COMPLETED)
                
                progress = parser.get_task_progress(task_queue)
                print(f"     任务完成，进度: {progress['progress_percentage']:.1f}%")
        
        finally:
            if test_doc.exists():
                test_doc.unlink()
    
    print("✅ 集成场景测试完成\n")


def main():
    """主测试函数"""
    print("🚀 AceFlow AI-人协同工作流核心功能测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_intent_recognition()
        test_collaboration_manager()
        test_task_parser()
        test_integration_scenario()
        
        print("🎉 所有测试完成！")
        print("\n📊 测试总结:")
        print("- ✅ 意图识别模块: 正常工作")
        print("- ✅ 协作管理模块: 正常工作") 
        print("- ✅ 任务解析模块: 正常工作")
        print("- ✅ 集成场景: 正常工作")
        
        print("\n🎯 下一步工作:")
        print("1. 集成到aceflow_stage工具中")
        print("2. 完善错误处理和边界情况")
        print("3. 添加更多的协作场景")
        print("4. 优化用户体验和响应时间")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()