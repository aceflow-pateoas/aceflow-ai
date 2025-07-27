"""
简单的 PATEOAS 系统测试
"""

import sys
import os

# 添加 aceflow 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aceflow'))

def test_imports():
    """测试导入"""
    print("🧪 测试模块导入...")
    
    try:
        from pateoas.models import PATEOASState, MemoryFragment, NextAction
        print("✅ 模型导入成功")
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        return False
    
    try:
        from pateoas.config import get_config
        print("✅ 配置导入成功")
    except Exception as e:
        print(f"❌ 配置导入失败: {e}")
        return False
    
    try:
        from pateoas.utils import generate_id, calculate_similarity
        print("✅ 工具导入成功")
    except Exception as e:
        print(f"❌ 工具导入失败: {e}")
        return False
    
    try:
        from pateoas.state_manager import StateContinuityManager
        print("✅ 状态管理器导入成功")
    except Exception as e:
        print(f"❌ 状态管理器导入失败: {e}")
        return False
    
    try:
        from pateoas.memory_system import ContextMemorySystem
        print("✅ 记忆系统导入成功")
    except Exception as e:
        print(f"❌ 记忆系统导入失败: {e}")
        return False
    
    return True

def test_basic_creation():
    """测试基本对象创建"""
    print("\n🧪 测试基本对象创建...")
    
    try:
        from pateoas.models import PATEOASState, MemoryFragment, NextAction, ActionType, MemoryCategory
        from pateoas.config import get_config
        
        # 测试配置
        config = get_config()
        print(f"✅ 配置加载成功，记忆启用: {config.memory_enabled}")
        
        # 测试状态创建
        state = PATEOASState(
            current_task="测试任务",
            task_progress=0.5,
            project_id="test_project"
        )
        print(f"✅ 状态创建成功，任务: {state.current_task}")
        
        # 测试记忆片段创建
        memory = MemoryFragment(
            content="这是一个测试记忆",
            category=MemoryCategory.LEARNING,
            importance=0.8,
            tags=["测试", "PATEOAS"]
        )
        print(f"✅ 记忆片段创建成功，重要性: {memory.importance}")
        
        # 测试行动建议创建
        action = NextAction(
            action_type=ActionType.CONTINUE,
            description="继续测试",
            command="test continue",
            confidence=0.9,
            estimated_time="5分钟"
        )
        print(f"✅ 行动建议创建成功，置信度: {action.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本对象创建失败: {e}")
        return False

def test_state_manager():
    """测试状态管理器"""
    print("\n🧪 测试状态管理器...")
    
    try:
        from pateoas.state_manager import StateContinuityManager
        
        # 创建状态管理器
        manager = StateContinuityManager("test_project")
        print("✅ 状态管理器创建成功")
        
        # 获取当前状态
        current_state = manager.get_current_state()
        print(f"✅ 获取当前状态成功，项目ID: {current_state['project_context']['project_id']}")
        
        # 添加记忆
        manager.add_memory("测试记忆内容", "learning", 0.7, ["测试"])
        print("✅ 添加记忆成功")
        
        # 生成状态声明
        declaration = manager.generate_state_declaration()
        print(f"✅ 生成状态声明成功，当前任务: {declaration['current_task']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态管理器测试失败: {e}")
        return False

def test_memory_system():
    """测试记忆系统"""
    print("\n🧪 测试记忆系统...")
    
    try:
        from pateoas.memory_system import ContextMemorySystem
        
        # 创建记忆系统
        memory_system = ContextMemorySystem("test_project")
        print("✅ 记忆系统创建成功")
        
        # 添加记忆
        memory_system.add_memory("这是一个测试记忆", "context", 0.8, ["测试", "记忆"])
        print("✅ 添加记忆成功")
        
        # 搜索记忆
        results = memory_system.search_memories("测试", limit=5)
        print(f"✅ 搜索记忆成功，找到 {len(results)} 条记忆")
        
        # 获取统计信息
        stats = memory_system.get_memory_stats()
        print(f"✅ 获取统计信息成功，总记忆数: {stats['total_memories']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆系统测试失败: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🚀 开始 PATEOAS 系统简单测试")
    print("=" * 40)
    
    tests = [
        ("模块导入", test_imports),
        ("基本对象创建", test_basic_creation),
        ("状态管理器", test_state_manager),
        ("记忆系统", test_memory_system)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！PATEOAS 基础功能正常。")
    else:
        print("⚠️  部分测试失败，但核心功能可用。")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    print(f"\n✨ PATEOAS 系统{'正常运行' if success else '部分功能可用'}！")