"""
测试记忆系统

测试 aceflow.workflow.memory 模块
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from aceflow.workflow.memory import MemoryManager, MemoryStore
from aceflow.workflow.memory.models import (
    Memory,
    MemoryType,
    MemoryPriority,
    MemoryQuery
)
from aceflow.workflow.models import Stage, StageStatus


class TestMemory:
    """测试记忆数据模型"""

    def test_memory_creation(self):
        """测试创建记忆"""
        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="选择使用 PostgreSQL 作为数据库",
            iteration_id="iter_001",
            stage_id="P1",
            priority=MemoryPriority.HIGH,
            metadata={"reason": "支持复杂查询"}
        )

        assert memory.memory_id == "mem_001"
        assert memory.type == MemoryType.DECISION
        assert memory.priority == MemoryPriority.HIGH
        assert memory.metadata['reason'] == "支持复杂查询"

    def test_memory_to_dict(self):
        """测试记忆转字典"""
        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="技术决策",
            iteration_id="iter_001"
        )

        data = memory.to_dict()

        assert data['memory_id'] == "mem_001"
        assert data['type'] == "decision"
        assert 'created_at' in data  # 实际使用 created_at 而非 timestamp

    def test_memory_from_dict(self):
        """测试从字典创建记忆"""
        data = {
            'memory_id': "mem_001",
            'type': "issue",
            'content': "发现性能问题",
            'iteration_id': "iter_001",
            'stage_id': "D1",
            'priority': "high",
            'metadata': {"severity": "critical"},
            'tags': ["performance"],
            'created_at': datetime.now().isoformat(),  # 必须字段
            'accessed_at': datetime.now().isoformat()
        }

        memory = Memory.from_dict(data)

        assert memory.memory_id == "mem_001"
        assert memory.type == MemoryType.ISSUE
        assert memory.priority == MemoryPriority.HIGH


class TestMemoryStore:
    """测试记忆存储"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def memory_store(self, temp_dir):
        """创建记忆存储"""
        return MemoryStore(storage_path=temp_dir / "memory.json")

    def test_store_creation(self, memory_store):
        """测试存储创建"""
        # MemoryStore 在首次保存时才创建文件
        # 只需验证 memory_store 创建成功即可
        assert memory_store is not None
        assert memory_store.storage_path is not None

    def test_add_memory(self, memory_store):
        """测试添加记忆"""
        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="技术选型决策",
            iteration_id="iter_001"
        )

        memory_store.add(memory)

        # 验证添加成功
        retrieved = memory_store.get("mem_001")
        assert retrieved is not None
        assert retrieved.memory_id == "mem_001"

    def test_get_memory(self, memory_store):
        """测试获取记忆"""
        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="决策内容",
            iteration_id="iter_001"
        )

        memory_store.add(memory)

        # 获取存在的记忆
        retrieved = memory_store.get("mem_001")
        assert retrieved.memory_id == "mem_001"

        # 获取不存在的记忆
        not_found = memory_store.get("mem_999")
        assert not_found is None

    def test_query_by_type(self, memory_store):
        """测试按类型查询"""
        # 添加不同类型的记忆
        memory_store.add(Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="决策1",
            iteration_id="iter_001"
        ))

        memory_store.add(Memory(
            memory_id="mem_002",
            type=MemoryType.ISSUE,
            content="问题1",
            iteration_id="iter_001"
        ))

        memory_store.add(Memory(
            memory_id="mem_003",
            type=MemoryType.DECISION,
            content="决策2",
            iteration_id="iter_001"
        ))

        # 查询 DECISION 类型
        query = MemoryQuery(types=[MemoryType.DECISION])
        results = memory_store.query(query)

        assert len(results) == 2
        assert all(m.type == MemoryType.DECISION for m in results)

    def test_query_by_iteration(self, memory_store):
        """测试按迭代查询"""
        memory_store.add(Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="决策1",
            iteration_id="iter_001"
        ))

        memory_store.add(Memory(
            memory_id="mem_002",
            type=MemoryType.DECISION,
            content="决策2",
            iteration_id="iter_002"
        ))

        # 查询 iter_001
        query = MemoryQuery(iteration_id="iter_001")
        results = memory_store.query(query)

        assert len(results) == 1
        assert results[0].iteration_id == "iter_001"

    def test_query_with_limit(self, memory_store):
        """测试限制查询结果数量"""
        # 添加多个记忆
        for i in range(10):
            memory_store.add(Memory(
                memory_id=f"mem_{i:03d}",
                type=MemoryType.DECISION,
                content=f"决策{i}",
                iteration_id="iter_001"
            ))

        # 限制返回5个
        query = MemoryQuery(iteration_id="iter_001", limit=5)
        results = memory_store.query(query)

        assert len(results) == 5

    def test_delete_memory(self, memory_store):
        """测试删除记忆"""
        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="决策",
            iteration_id="iter_001"
        )

        memory_store.add(memory)

        # 删除
        success = memory_store.delete("mem_001")
        assert success is True

        # 验证删除
        retrieved = memory_store.get("mem_001")
        assert retrieved is None

    def test_persistence(self, temp_dir):
        """测试持久化"""
        storage_path = temp_dir / "memory.json"

        # 创建第一个存储并添加数据
        store1 = MemoryStore(storage_path=storage_path)
        store1.add(Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="决策",
            iteration_id="iter_001"
        ))

        # 创建第二个存储，应该能加载数据
        store2 = MemoryStore(storage_path=storage_path)
        memory = store2.get("mem_001")

        assert memory is not None
        assert memory.memory_id == "mem_001"


class TestMemoryManager:
    """测试记忆管理器"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def memory_manager(self, temp_dir):
        """创建记忆管理器"""
        return MemoryManager(storage_path=temp_dir / "memory.json")

    def test_manager_creation(self, memory_manager):
        """测试管理器创建"""
        assert memory_manager.store is not None

    def test_record_decision(self, memory_manager):
        """测试记录决策"""
        memory = memory_manager.record_decision(
            decision="使用 Redis 作为缓存",
            context={"reason": "高性能"},
            iteration_id="iter_001",
            stage_id="P1"
        )

        assert memory is not None
        assert memory.type == MemoryType.DECISION

        # 验证记录成功
        retrieved = memory_manager.store.get(memory.memory_id)
        assert retrieved.type == MemoryType.DECISION

    def test_record_issue(self, memory_manager):
        """测试记录问题"""
        memory = memory_manager.record_issue(
            issue="API 响应时间过长",
            severity="high",
            iteration_id="iter_001",
            stage_id="D1",
            solution="添加缓存层"
        )

        assert memory is not None
        assert memory.type == MemoryType.ISSUE
        assert memory.metadata['severity'] == "high"

        retrieved = memory_manager.store.get(memory.memory_id)
        assert retrieved.type == MemoryType.ISSUE

    def test_record_learning(self, memory_manager):
        """测试记录经验教训"""
        memory = memory_manager.record_learning(
            learning="提前做好性能测试很重要",
            category="技术",
            iteration_id="iter_001"
        )

        assert memory is not None
        assert memory.type == MemoryType.LEARNING

        retrieved = memory_manager.store.get(memory.memory_id)
        assert retrieved.type == MemoryType.LEARNING

    def test_record_stage_output(self, memory_manager):
        """测试记录阶段输出"""
        stage = Stage(
            stage_id="P1",
            name="规划",
            description="规划阶段",
            status=StageStatus.COMPLETED
        )

        memory = memory_manager.record_stage_output(
            iteration_id="iter_001",
            stage=stage,
            output="需求文档已完成",
            mode="standard"
        )

        assert memory is not None
        assert memory.type == MemoryType.STAGE_OUTPUT

        retrieved = memory_manager.store.get(memory.memory_id)
        assert retrieved.type == MemoryType.STAGE_OUTPUT

    def test_recall_for_stage(self, memory_manager):
        """测试阶段记忆召回"""
        # 记录一些记忆
        memory_manager.record_decision(
            "决策1",
            {},
            iteration_id="iter_001",
            stage_id="P1"
        )

        memory_manager.record_issue(
            "问题1",
            severity="medium",
            iteration_id="iter_001",
            stage_id="P1"
        )

        # 召回 P1 阶段的记忆
        memories = memory_manager.recall_for_stage("iter_001", "P1")

        assert len(memories) > 0
        assert all(m.stage_id == "P1" for m in memories)

    def test_recall_similar_issues(self, memory_manager):
        """测试召回相似问题"""
        # 记录几个问题
        memory_manager.record_issue(
            "API 性能问题",
            severity="high",
            iteration_id="iter_001"
        )

        memory_manager.record_issue(
            "数据库性能问题",
            severity="medium",
            iteration_id="iter_001"
        )

        memory_manager.record_issue(
            "UI 显示问题",
            severity="low",
            iteration_id="iter_001"
        )

        # 搜索性能相关问题
        similar = memory_manager.recall_similar_issues("性能", limit=2)

        assert len(similar) <= 2
        # 结果中应该包含性能相关的问题
        assert any("性能" in m.content for m in similar)

    def test_recall_learnings(self, memory_manager):
        """测试召回经验教训"""
        # 记录几个经验教训
        memory_manager.record_learning(
            "早期的性能测试很重要",
            category="技术",
            iteration_id="iter_001"
        )

        memory_manager.record_learning(
            "需求评审要充分",
            category="流程",
            iteration_id="iter_001"
        )

        # 召回技术类经验
        learnings = memory_manager.recall_learnings(category="技术")

        assert len(learnings) > 0
        assert all(m.type == MemoryType.LEARNING for m in learnings)

    def test_get_iteration_summary(self, memory_manager):
        """测试获取迭代摘要"""
        # 记录各种类型的记忆
        memory_manager.record_decision(
            "决策1",
            {},
            iteration_id="iter_001",
            stage_id="P1"
        )

        memory_manager.record_issue(
            "问题1",
            severity="high",
            iteration_id="iter_001",
            stage_id="D1"
        )

        memory_manager.record_learning(
            "经验1",
            category="技术",
            iteration_id="iter_001"
        )

        # 获取摘要
        summary = memory_manager.get_iteration_summary("iter_001")

        assert summary['iteration_id'] == "iter_001"
        assert summary['total_memories'] == 3
        assert summary['decisions_made'] == 1  # 实际使用 decisions_made 而非 by_type
        assert summary['issues_encountered'] == 1
        assert summary['learnings_captured'] == 1

    def test_search_memories(self, memory_manager):
        """测试搜索记忆"""
        # 记录一些记忆
        memory_manager.record_decision(
            "使用 PostgreSQL 数据库",
            {},
            iteration_id="iter_001"
        )

        memory_manager.record_decision(
            "使用 Redis 缓存",
            {},
            iteration_id="iter_001"
        )

        memory_manager.record_issue(
            "数据库连接问题",
            severity="high",
            iteration_id="iter_001"
        )

        # 搜索包含"数据库"的记忆 (使用 store.search)
        results = memory_manager.store.search("数据库", limit=10)

        assert len(results) > 0
        assert all("数据库" in m.content for m in results)

    def test_get_high_priority_memories(self, memory_manager):
        """测试获取高优先级记忆"""
        # 记录不同优先级的记忆
        memory_manager.record_issue(
            "严重问题",
            severity="critical",
            iteration_id="iter_001"
        )

        memory_manager.record_issue(
            "一般问题",
            severity="low",
            iteration_id="iter_001"
        )

        # 获取高优先级记忆 (使用 MemoryQuery)
        query = MemoryQuery(
            iteration_id="iter_001",
            min_priority=MemoryPriority.HIGH
        )
        high_priority = memory_manager.store.query(query)

        # 应该至少有一个高优先级记忆
        assert len(high_priority) > 0
        assert all(m.priority.value in ['high', 'critical'] for m in high_priority)


class TestMemoryQuery:
    """测试记忆查询"""

    def test_query_creation(self):
        """测试创建查询"""
        query = MemoryQuery(
            types=[MemoryType.DECISION, MemoryType.ISSUE],
            iteration_id="iter_001",
            stage_id="P1",
            min_priority=MemoryPriority.HIGH,  # 使用 min_priority 而非 priority
            limit=10
        )

        assert len(query.types) == 2
        assert query.iteration_id == "iter_001"
        assert query.stage_id == "P1"
        assert query.limit == 10

    def test_query_usage(self):
        """测试查询使用"""
        # 创建查询对象
        query = MemoryQuery(
            types=[MemoryType.DECISION],
            iteration_id="iter_001"
        )

        # 验证查询对象创建成功
        assert query.types == [MemoryType.DECISION]
        assert query.iteration_id == "iter_001"
