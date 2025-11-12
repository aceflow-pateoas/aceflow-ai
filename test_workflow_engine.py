#!/usr/bin/env python3
"""测试 WorkflowEngine 新实现的状态管理逻辑"""

import sys
import os
import json
import shutil
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.core.workflow_engine import WorkflowEngine, StageStatus, WorkflowMode


def setup_test_env():
    """设置测试环境"""
    test_dir = Path(__file__).parent / "test_workflow_project"
    test_dir.mkdir(exist_ok=True)
    os.chdir(test_dir)

    # 清理之前的状态文件
    aceflow_dir = test_dir / ".aceflow"
    if aceflow_dir.exists():
        shutil.rmtree(aceflow_dir)

    return test_dir


def cleanup_test_env(test_dir):
    """清理测试环境"""
    os.chdir(test_dir.parent)
    if test_dir.exists():
        shutil.rmtree(test_dir)


def print_status(title, status):
    """打印状态信息"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(json.dumps(status, indent=2, ensure_ascii=False))


def test_initial_state():
    """测试1: 初始状态"""
    print("\n🧪 测试1: 初始状态")

    engine = WorkflowEngine()
    status = engine.get_current_status()

    print_status("初始状态", status)

    # 验证初始状态
    assert status["current_stage"]["name"] == "user_stories", "初始阶段应该是 user_stories"
    assert status["current_stage"]["status"] == "pending", "初始状态应该是 pending"
    assert status["current_stage"]["progress"] == 0, "初始进度应该是 0"
    assert status["overall_progress"] == 0, "总体进度应该是 0"
    assert status["completed_stages"] == [], "已完成阶段应该为空"
    assert status["next_stage"] == "task_breakdown", "下一阶段应该是 task_breakdown"

    print("✅ 测试1通过: 初始状态正确")
    return engine


def test_stage_progress_update(engine):
    """测试2: 更新阶段进度"""
    print("\n🧪 测试2: 更新阶段进度")

    # 更新进度到 50%
    status = engine.update_stage_progress(50)
    print_status("更新进度到 50%", status)

    # 验证状态
    assert status["current_stage"]["status"] == "in_progress", "状态应该变为 in_progress"
    assert status["current_stage"]["progress"] == 50, "阶段进度应该是 50"
    assert status["overall_progress"] == 6.25, "总体进度应该是 6.25 (50% of 12.5%)"

    # 更新进度到 100%
    status = engine.update_stage_progress(100)
    print_status("更新进度到 100%", status)

    assert status["current_stage"]["progress"] == 100, "阶段进度应该是 100"
    assert status["overall_progress"] == 12.5, "总体进度应该是 12.5 (100% of 12.5%)"

    print("✅ 测试2通过: 阶段进度更新正确")


def test_advance_to_next_stage(engine):
    """测试3: 推进到下一阶段"""
    print("\n🧪 测试3: 推进到下一阶段")

    result = engine.advance_to_next_stage()
    print_status("推进到下一阶段", result)

    # 验证推进结果
    assert result["success"] == True, "推进应该成功"
    assert result["previous_stage"] == "user_stories", "前一阶段应该是 user_stories"
    assert result["current_stage"]["name"] == "task_breakdown", "当前阶段应该是 task_breakdown"
    assert result["current_stage"]["status"] == "pending", "新阶段状态应该是 pending"
    assert result["current_stage"]["progress"] == 0, "新阶段进度应该是 0"
    assert "user_stories" in result["completed_stages"], "user_stories 应该在已完成列表中"

    # 验证当前状态
    status = engine.get_current_status()
    print_status("当前状态", status)

    assert status["overall_progress"] == 12.5, "总体进度应该是 12.5 (1个阶段完成)"

    print("✅ 测试3通过: 阶段推进正确")


def test_multiple_stage_progression(engine):
    """测试4: 多阶段推进"""
    print("\n🧪 测试4: 多阶段推进")

    # 完成 task_breakdown (当前阶段)
    engine.update_stage_progress(100)
    engine.advance_to_next_stage()

    status = engine.get_current_status()
    print_status("完成 task_breakdown 后", status)

    assert status["current_stage"]["name"] == "test_design", "当前阶段应该是 test_design"
    assert len(status["completed_stages"]) == 2, "应该有2个已完成阶段"
    assert status["overall_progress"] == 25.0, "总体进度应该是 25% (2个阶段完成)"

    # 继续推进到 implementation
    engine.update_stage_progress(50)  # test_design 完成 50%

    status = engine.get_current_status()
    print_status("test_design 完成 50%", status)

    # 验证计算: 2个完成 (25%) + 当前50% (50% of 12.5% = 6.25%) = 31.25%
    assert status["overall_progress"] == 31.25, f"总体进度应该是 31.25, 实际是 {status['overall_progress']}"

    print("✅ 测试4通过: 多阶段推进正确")


def test_list_all_stages(engine):
    """测试5: 列出所有阶段"""
    print("\n🧪 测试5: 列出所有阶段")

    stages = engine.list_all_stages()
    print_status("所有阶段", {"stages": stages})

    # 验证阶段列表
    assert len(stages) == 8, "Standard 模式应该有 8 个阶段"

    # 验证阶段状态
    for i, stage in enumerate(stages):
        if i < 2:  # user_stories, task_breakdown
            assert stage["status"] == "completed", f"{stage['name']} 应该是 completed"
        elif i == 2:  # test_design (当前阶段)
            assert stage["status"] == "in_progress", f"{stage['name']} 应该是 in_progress"
            assert stage["is_current"] == True, f"{stage['name']} 应该是当前阶段"
        else:  # 后续阶段
            assert stage["status"] == "pending", f"{stage['name']} 应该是 pending"

    print("✅ 测试5通过: 阶段列表正确")


def test_reset_project(engine):
    """测试6: 重置项目"""
    print("\n🧪 测试6: 重置项目")

    result = engine.reset_project()
    print_status("重置项目", result)

    # 验证重置结果
    assert result["success"] == True, "重置应该成功"
    assert result["current_stage"]["name"] == "user_stories", "应该回到初始阶段"
    assert result["current_stage"]["status"] == "pending", "状态应该是 pending"
    assert result["overall_progress"] == 0, "总体进度应该是 0"
    assert result["completed_stages"] == [], "已完成阶段应该为空"

    print("✅ 测试6通过: 项目重置正确")


def test_state_persistence():
    """测试7: 状态持久化"""
    print("\n🧪 测试7: 状态持久化")

    # 创建引擎并更新状态
    engine1 = WorkflowEngine()
    engine1.update_stage_progress(75)
    status1 = engine1.get_current_status()
    print_status("引擎1的状态", status1)

    # 创建新引擎,应该加载持久化的状态
    engine2 = WorkflowEngine()
    status2 = engine2.get_current_status()
    print_status("引擎2的状态 (应该与引擎1相同)", status2)

    # 验证状态一致
    assert status1["current_stage"]["progress"] == status2["current_stage"]["progress"], "进度应该一致"
    assert status1["overall_progress"] == status2["overall_progress"], "总体进度应该一致"

    # 验证状态文件存在
    state_file = Path.cwd() / ".aceflow" / "current_state.json"
    assert state_file.exists(), "状态文件应该存在"

    with open(state_file, 'r', encoding='utf-8') as f:
        state_data = json.load(f)
    print_status("状态文件内容", state_data)

    assert state_data["flow"]["stage_progress"] == 75, "状态文件中的进度应该是 75"
    assert state_data["flow"]["stage_status"] == "in_progress", "状态文件中的状态应该是 in_progress"

    print("✅ 测试7通过: 状态持久化正确")


def main():
    """运行所有测试"""
    print("="*60)
    print("  WorkflowEngine 状态管理逻辑测试")
    print("="*60)

    test_dir = setup_test_env()

    try:
        # 运行测试
        engine = test_initial_state()
        test_stage_progress_update(engine)
        test_advance_to_next_stage(engine)
        test_multiple_stage_progression(engine)
        test_list_all_stages(engine)
        test_reset_project(engine)
        test_state_persistence()

        print("\n" + "="*60)
        print("  ✅ 所有测试通过!")
        print("="*60)
        print("\n新的 WorkflowEngine 实现:")
        print("✅ 初始状态正确 (progress=0, status=pending)")
        print("✅ 阶段进度更新正确")
        print("✅ 状态转换正确 (pending → in_progress → completed)")
        print("✅ 总体进度计算正确")
        print("✅ 阶段推进逻辑正确")
        print("✅ 状态持久化工作正常")

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup_test_env(test_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
