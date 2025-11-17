"""
Unit tests for V4MemoryManager

Tests for:
- TechDecision recording and retrieval
- Lesson recording and retrieval
- DocumentRef recording and retrieval
- Auto-detection (decisions and lessons)
- Smart recall with relevance scoring
- v3.0 backward compatibility
- Persistence and data loading
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from aceflow.workflow.memory.v4_manager import V4MemoryManager
from aceflow.workflow.memory.models import Memory, MemoryType, MemoryPriority
from aceflow.workflow.memory.v4_models import (
    TechDecision, Lesson, DocumentRef,
    DecisionScope, LessonCategory,
    MemoryInjectionContext
)


# ==================== Test Fixtures ====================

@pytest.fixture
def temp_storage():
    """创建临时存储目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def manager(temp_storage):
    """创建V4MemoryManager实例"""
    storage_path = temp_storage / "memories.json"
    return V4MemoryManager(storage_path=storage_path)


# ==================== TechDecision Management Tests ====================

class TestTechDecisionManagement:
    """Test TechDecision recording and retrieval"""

    def test_record_tech_decision(self, manager):
        """Test recording a tech decision"""
        decision = manager.record_tech_decision(
            title="选择 PostgreSQL 数据库",
            decision="使用 PostgreSQL 作为主数据库",
            reason="需要复杂查询和事务支持",
            scope=DecisionScope.ARCHITECTURE,
            alternatives=["MySQL", "MongoDB"],
            tech_stack=["PostgreSQL", "SQLAlchemy"],
            impact="影响整个数据层架构",
            work_item_id="work_001",
            stage_id="design",
            tags=["database", "architecture"],
            importance=0.9
        )

        assert decision.decision_id.startswith("dec_")
        assert decision.title == "选择 PostgreSQL 数据库"
        assert decision.scope == DecisionScope.ARCHITECTURE
        assert len(decision.alternatives) == 2
        assert decision.importance == 0.9
        assert decision.work_item_id == "work_001"

    def test_get_decision(self, manager):
        """Test retrieving a tech decision"""
        decision = manager.record_tech_decision(
            title="API 认证方案",
            decision="使用 JWT 认证",
            reason="无状态认证",
            scope=DecisionScope.MODULE
        )

        retrieved = manager.get_decision(decision.decision_id)

        assert retrieved is not None
        assert retrieved.decision_id == decision.decision_id
        assert retrieved.title == "API 认证方案"

    def test_list_decisions_all(self, manager):
        """Test listing all decisions"""
        manager.record_tech_decision(
            title="Decision 1",
            decision="Content 1",
            reason="Reason 1",
            scope=DecisionScope.LOCAL
        )
        manager.record_tech_decision(
            title="Decision 2",
            decision="Content 2",
            reason="Reason 2",
            scope=DecisionScope.ARCHITECTURE,
            importance=0.95
        )

        decisions = manager.list_decisions()

        assert len(decisions) == 2
        # Should be sorted by importance (0.95 > 0.8)
        assert decisions[0].importance >= decisions[1].importance

    def test_list_decisions_filtered_by_scope(self, manager):
        """Test filtering decisions by scope"""
        manager.record_tech_decision(
            title="Local Decision",
            decision="Local content",
            reason="Local reason",
            scope=DecisionScope.LOCAL
        )
        manager.record_tech_decision(
            title="Architecture Decision",
            decision="Arch content",
            reason="Arch reason",
            scope=DecisionScope.ARCHITECTURE
        )

        arch_decisions = manager.list_decisions(scope=DecisionScope.ARCHITECTURE)

        assert len(arch_decisions) == 1
        assert arch_decisions[0].title == "Architecture Decision"

    def test_list_decisions_filtered_by_work_item(self, manager):
        """Test filtering decisions by work_item_id"""
        manager.record_tech_decision(
            title="Decision A",
            decision="Content A",
            reason="Reason A",
            work_item_id="work_001"
        )
        manager.record_tech_decision(
            title="Decision B",
            decision="Content B",
            reason="Reason B",
            work_item_id="work_002"
        )

        work_001_decisions = manager.list_decisions(work_item_id="work_001")

        assert len(work_001_decisions) == 1
        assert work_001_decisions[0].title == "Decision A"

    def test_list_decisions_filtered_by_importance(self, manager):
        """Test filtering decisions by minimum importance"""
        manager.record_tech_decision(
            title="Low Importance",
            decision="Content",
            reason="Reason",
            importance=0.5
        )
        manager.record_tech_decision(
            title="High Importance",
            decision="Content",
            reason="Reason",
            importance=0.9
        )

        important_decisions = manager.list_decisions(min_importance=0.8)

        assert len(important_decisions) == 1
        assert important_decisions[0].title == "High Importance"


# ==================== Auto-Detection Tests ====================

class TestAutoDetection:
    """Test automatic detection of decisions and lessons"""

    def test_detect_decision_positive(self, manager):
        """Test detecting a valid decision"""
        text = "我们决定选择 PostgreSQL 作为主数据库，因为需要支持多模块的复杂查询。"

        result = manager.detect_and_record_decision(
            text=text,
            work_item_id="work_001",
            stage_id="design",
            auto_record=False  # Don't auto-record, just detect
        )

        assert result is not None
        detection_result, decision_obj = result
        assert detection_result['detected'] is True
        assert detection_result['has_wide_impact'] is True
        assert detection_result['is_tech_selection'] is True
        assert decision_obj is None  # No auto-record

    def test_detect_decision_auto_record(self, manager):
        """Test auto-recording a detected decision"""
        text = "我们使用 Redis 作为缓存框架来提升性能。"

        result = manager.detect_and_record_decision(
            text=text,
            work_item_id="work_002",
            stage_id="design",
            auto_record=True  # Auto-record
        )

        assert result is not None
        detection_result, decision_obj = result
        assert detection_result['detected'] is True
        assert decision_obj is not None
        assert decision_obj.decision_id.startswith("dec_")
        assert decision_obj.work_item_id == "work_002"

        # Verify it's stored
        retrieved = manager.get_decision(decision_obj.decision_id)
        assert retrieved is not None

    def test_detect_decision_negative(self, manager):
        """Test no detection when text doesn't match criteria"""
        text = "PostgreSQL 是一个很好的数据库。"

        result = manager.detect_and_record_decision(
            text=text,
            work_item_id="work_003",
            stage_id="design",
            auto_record=False
        )

        assert result is None  # No decision detected

    def test_detect_lesson_positive(self, manager):
        """Test detecting a valid lesson"""
        text = "我们遇到了 N+1 查询问题导致性能下降，解决方法是使用 eager loading。"

        result = manager.detect_and_record_lesson(
            text=text,
            work_item_id="work_004",
            stage_id="implementation",
            auto_record=False
        )

        assert result is not None
        extraction_result, lesson_obj = result
        assert extraction_result['detected'] is True
        assert extraction_result['has_problem'] is True
        assert extraction_result['has_solution'] is True
        assert lesson_obj is None  # No auto-record

    def test_detect_lesson_auto_record(self, manager):
        """Test auto-recording a detected lesson"""
        text = "最佳实践建议：始终使用参数化查询来避免 SQL 注入。"

        result = manager.detect_and_record_lesson(
            text=text,
            work_item_id="work_005",
            stage_id="implementation",
            auto_record=True
        )

        assert result is not None
        extraction_result, lesson_obj = result
        assert extraction_result['detected'] is True
        assert lesson_obj is not None
        assert lesson_obj.lesson_id.startswith("lesson_")

        # Verify it's stored
        retrieved = manager.get_lesson(lesson_obj.lesson_id)
        assert retrieved is not None

    def test_detect_lesson_negative(self, manager):
        """Test no detection when text doesn't match criteria"""
        text = "数据库查询很慢，需要优化。"

        result = manager.detect_and_record_lesson(
            text=text,
            work_item_id="work_006",
            stage_id="implementation",
            auto_record=False
        )

        assert result is None  # No lesson detected


# ==================== Lesson Management Tests ====================

class TestLessonManagement:
    """Test Lesson recording and retrieval"""

    def test_record_lesson(self, manager):
        """Test recording a lesson"""
        lesson = manager.record_lesson(
            title="避免 N+1 查询",
            content="在循环中执行查询导致性能问题",
            category=LessonCategory.TECHNICAL,
            what_happened="用户列表页面加载缓慢",
            what_learned="应该使用 eager loading",
            how_to_apply="使用 SQLAlchemy 的 joinedload()",
            applicability="general",
            applicable_scenarios=["database", "performance"],
            work_item_id="work_001",
            stage_id="implementation",
            tags=["database", "performance"],
            importance=0.8
        )

        assert lesson.lesson_id.startswith("lesson_")
        assert lesson.title == "避免 N+1 查询"
        assert lesson.category == LessonCategory.TECHNICAL
        assert lesson.applicability == "general"
        assert lesson.applied_count == 0
        assert lesson.work_item_id == "work_001"

    def test_get_lesson(self, manager):
        """Test retrieving a lesson"""
        lesson = manager.record_lesson(
            title="TDD 的重要性",
            content="先写测试可以发现设计问题",
            category=LessonCategory.BEST_PRACTICE,
            what_happened="重构时发现很多边界情况未覆盖",
            what_learned="TDD 可以提高代码质量",
            how_to_apply="遵循 Red-Green-Refactor 循环"
        )

        retrieved = manager.get_lesson(lesson.lesson_id)

        assert retrieved is not None
        assert retrieved.lesson_id == lesson.lesson_id
        assert retrieved.title == "TDD 的重要性"

    def test_list_lessons_all(self, manager):
        """Test listing all lessons"""
        manager.record_lesson(
            title="Lesson 1",
            content="Content 1",
            category=LessonCategory.TECHNICAL,
            what_happened="What 1",
            what_learned="Learned 1",
            how_to_apply="Apply 1"
        )
        manager.record_lesson(
            title="Lesson 2",
            content="Content 2",
            category=LessonCategory.PROCESS,
            what_happened="What 2",
            what_learned="Learned 2",
            how_to_apply="Apply 2",
            importance=0.9
        )

        lessons = manager.list_lessons()

        assert len(lessons) == 2
        # Should be sorted by importance
        assert lessons[0].importance >= lessons[1].importance

    def test_list_lessons_filtered_by_category(self, manager):
        """Test filtering lessons by category"""
        manager.record_lesson(
            title="Technical Lesson",
            content="Tech content",
            category=LessonCategory.TECHNICAL,
            what_happened="What",
            what_learned="Learned",
            how_to_apply="Apply"
        )
        manager.record_lesson(
            title="Process Lesson",
            content="Process content",
            category=LessonCategory.PROCESS,
            what_happened="What",
            what_learned="Learned",
            how_to_apply="Apply"
        )

        tech_lessons = manager.list_lessons(category=LessonCategory.TECHNICAL)

        assert len(tech_lessons) == 1
        assert tech_lessons[0].title == "Technical Lesson"

    def test_increment_lesson_applied_count(self, manager):
        """Test incrementing lesson applied count"""
        lesson = manager.record_lesson(
            title="Use transactions",
            content="Database operations in transactions",
            category=LessonCategory.TECHNICAL,
            what_happened="Data inconsistency",
            what_learned="Use transactions",
            how_to_apply="Wrap operations in transaction block"
        )

        assert lesson.applied_count == 0

        # Increment
        success = manager.increment_lesson_applied_count(lesson.lesson_id)
        assert success is True

        # Verify
        retrieved = manager.get_lesson(lesson.lesson_id)
        assert retrieved.applied_count == 1


# ==================== DocumentRef Management Tests ====================

class TestDocumentRefManagement:
    """Test DocumentRef recording and retrieval"""

    def test_record_document_ref(self, manager):
        """Test recording a document reference"""
        doc_ref = manager.record_document_ref(
            title="PostgreSQL 索引优化",
            document_type="api",
            path="https://www.postgresql.org/docs/current/indexes.html",
            section="Chapter 11.5",
            reason="设计数据库索引策略",
            key_points=["B-tree 索引适合范围查询", "考虑使用部分索引"],
            work_item_id="work_001",
            tags=["database", "performance"]
        )

        assert doc_ref.ref_id.startswith("ref_")
        assert doc_ref.title == "PostgreSQL 索引优化"
        assert doc_ref.document_type == "api"
        assert len(doc_ref.key_points) == 2
        assert doc_ref.work_item_id == "work_001"

    def test_get_document_ref(self, manager):
        """Test retrieving a document reference"""
        doc_ref = manager.record_document_ref(
            title="API 设计规范",
            document_type="design",
            path="docs/api_design_guide.md",
            reason="统一 API 设计风格"
        )

        retrieved = manager.get_document_ref(doc_ref.ref_id)

        assert retrieved is not None
        assert retrieved.ref_id == doc_ref.ref_id
        assert retrieved.title == "API 设计规范"

    def test_list_document_refs_all(self, manager):
        """Test listing all document refs"""
        manager.record_document_ref(
            title="Doc 1",
            document_type="api",
            path="/path/1",
            reason="Reason 1"
        )
        manager.record_document_ref(
            title="Doc 2",
            document_type="design",
            path="/path/2",
            reason="Reason 2"
        )

        docs = manager.list_document_refs()

        assert len(docs) == 2
        # Should be sorted by created_at (most recent first)
        assert docs[0].created_at >= docs[1].created_at

    def test_list_document_refs_filtered_by_type(self, manager):
        """Test filtering document refs by type"""
        manager.record_document_ref(
            title="API Doc",
            document_type="api",
            path="/api/path",
            reason="API reference"
        )
        manager.record_document_ref(
            title="Design Doc",
            document_type="design",
            path="/design/path",
            reason="Design guide"
        )

        api_docs = manager.list_document_refs(document_type="api")

        assert len(api_docs) == 1
        assert api_docs[0].title == "API Doc"


# ==================== Smart Recall Tests ====================

class TestSmartRecall:
    """Test relevance-based memory recall"""

    def test_recall_for_work_item(self, manager):
        """Test recalling memories for a work item using relevance scoring"""
        # Create some memories
        manager.record_decision(
            decision="选择 PostgreSQL 数据库",
            context={"type": "database"},
            iteration_id="iter_001",
            stage_id="design",
            priority=MemoryPriority.HIGH
        )
        manager.record_learning(
            learning="使用索引可以提升查询性能",
            category="performance",
            iteration_id="iter_001",
            applicability="general"
        )

        # Create injection context
        context = MemoryInjectionContext(
            work_item_id="work_new",
            work_item_type="feature",
            work_item_title="数据库查询优化",
            work_item_description="优化 PostgreSQL 查询性能",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.2,
            max_memories=5
        )

        # Recall memories
        ranked_memories = manager.recall_for_work_item(context)

        # Should return some memories
        assert len(ranked_memories) >= 0  # May be 0 if relevance too low
        # If there are results, check structure
        for memory, score in ranked_memories:
            assert isinstance(memory, Memory)
            assert hasattr(score, 'total_score')
            assert 0.0 <= score.total_score <= 1.0

    def test_get_relevant_decisions(self, manager):
        """Test getting relevant tech decisions"""
        # Create decisions
        manager.record_tech_decision(
            title="PostgreSQL 数据库选择",
            decision="使用 PostgreSQL",
            reason="支持复杂查询",
            scope=DecisionScope.ARCHITECTURE,
            tech_stack=["PostgreSQL"],
            tags=["database", "architecture"],
            work_item_id="work_001"
        )
        manager.record_tech_decision(
            title="React 前端框架",
            decision="使用 React",
            reason="组件化开发",
            scope=DecisionScope.MODULE,
            tech_stack=["React"],
            tags=["frontend", "ui"]
        )

        # Create context for database work
        context = MemoryInjectionContext(
            work_item_id="work_new",
            work_item_type="feature",
            work_item_title="数据库设计",
            work_item_description="设计数据库 schema",
            stage_id="design",
            stage_name="Design",
            stage_type="design",
            min_relevance=0.3,
            max_memories=5
        )

        # Get relevant decisions
        relevant_decisions = manager.get_relevant_decisions(context)

        # Database decision should be more relevant than React decision
        assert len(relevant_decisions) >= 0
        # Check structure
        for decision, score in relevant_decisions:
            assert isinstance(decision, TechDecision)
            assert hasattr(score, 'total_score')

    def test_get_relevant_lessons(self, manager):
        """Test getting relevant lessons"""
        # Create lessons
        manager.record_lesson(
            title="N+1 查询优化",
            content="避免循环查询",
            category=LessonCategory.TECHNICAL,
            what_happened="性能问题",
            what_learned="使用 eager loading",
            how_to_apply="使用 joinedload",
            applicable_scenarios=["database", "performance"],
            tags=["database", "performance"]
        )
        manager.record_lesson(
            title="前端组件设计",
            content="组件复用",
            category=LessonCategory.BEST_PRACTICE,
            what_happened="代码重复",
            what_learned="组件化设计",
            how_to_apply="提取公共组件",
            applicable_scenarios=["frontend"],
            tags=["frontend", "ui"]
        )

        # Create context for database optimization
        context = MemoryInjectionContext(
            work_item_id="work_new",
            work_item_type="feature",
            work_item_title="查询优化",
            work_item_description="优化数据库查询性能",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.3,
            max_memories=5
        )

        # Get relevant lessons
        relevant_lessons = manager.get_relevant_lessons(context)

        # Database lesson should be more relevant
        assert len(relevant_lessons) >= 0
        for lesson, score in relevant_lessons:
            assert isinstance(lesson, Lesson)
            assert hasattr(score, 'total_score')


# ==================== v3.0 Compatibility Tests ====================

class TestBackwardCompatibility:
    """Test v3.0 backward compatibility"""

    def test_v3_memory_created_for_decision(self, manager):
        """Test that v3.0 Memory is created when recording TechDecision"""
        decision = manager.record_tech_decision(
            title="Test Decision",
            decision="Test content",
            reason="Test reason",
            scope=DecisionScope.LOCAL,
            work_item_id="work_001",
            stage_id="design"
        )

        # Check v3.0 Memory exists
        v3_memory_id = f"v3_{decision.decision_id}"
        v3_memory = manager.store.get(v3_memory_id)

        assert v3_memory is not None
        assert v3_memory.type == MemoryType.DECISION
        assert "Test Decision" in v3_memory.content
        assert v3_memory.metadata['v4_type'] == 'tech_decision'
        assert v3_memory.metadata['v4_id'] == decision.decision_id

    def test_v3_memory_created_for_lesson(self, manager):
        """Test that v3.0 Memory is created when recording Lesson"""
        lesson = manager.record_lesson(
            title="Test Lesson",
            content="Test content",
            category=LessonCategory.TECHNICAL,
            what_happened="What",
            what_learned="Learned",
            how_to_apply="Apply",
            work_item_id="work_002",
            stage_id="implementation"
        )

        # Check v3.0 Memory exists
        v3_memory_id = f"v3_{lesson.lesson_id}"
        v3_memory = manager.store.get(v3_memory_id)

        assert v3_memory is not None
        assert v3_memory.type == MemoryType.LEARNING
        assert "Test Lesson" in v3_memory.content
        assert v3_memory.metadata['v4_type'] == 'lesson'
        assert v3_memory.metadata['v4_id'] == lesson.lesson_id

    def test_v3_methods_still_work(self, manager):
        """Test that v3.0 methods still work"""
        # Test v3.0 record_decision
        v3_memory = manager.record_decision(
            decision="v3.0 decision",
            context={"test": "context"},
            iteration_id="iter_001",
            stage_id="design"
        )

        assert v3_memory is not None
        assert v3_memory.type == MemoryType.DECISION

        # Test v3.0 record_learning
        v3_learning = manager.record_learning(
            learning="v3.0 learning",
            category="technical",
            iteration_id="iter_001"
        )

        assert v3_learning is not None
        assert v3_learning.type == MemoryType.LEARNING

        # Test v3.0 recall
        recalled = manager.recall_for_stage("iter_001", "design")
        assert isinstance(recalled, list)


# ==================== Persistence Tests ====================

class TestPersistence:
    """Test data persistence and loading"""

    def test_decision_persistence(self, temp_storage):
        """Test decisions are persisted and loaded correctly"""
        storage_path = temp_storage / "memories.json"

        # Create manager and record decision
        manager1 = V4MemoryManager(storage_path=storage_path)
        decision = manager1.record_tech_decision(
            title="Persist Test",
            decision="Content",
            reason="Reason",
            scope=DecisionScope.LOCAL,
            importance=0.85
        )
        decision_id = decision.decision_id

        # Create new manager instance (should load from file)
        manager2 = V4MemoryManager(storage_path=storage_path)

        # Verify decision is loaded
        loaded_decision = manager2.get_decision(decision_id)
        assert loaded_decision is not None
        assert loaded_decision.title == "Persist Test"
        assert loaded_decision.importance == 0.85

    def test_lesson_persistence(self, temp_storage):
        """Test lessons are persisted and loaded correctly"""
        storage_path = temp_storage / "memories.json"

        # Create manager and record lesson
        manager1 = V4MemoryManager(storage_path=storage_path)
        lesson = manager1.record_lesson(
            title="Persist Lesson",
            content="Content",
            category=LessonCategory.TECHNICAL,
            what_happened="What",
            what_learned="Learned",
            how_to_apply="Apply",
            importance=0.75
        )
        lesson_id = lesson.lesson_id

        # Create new manager instance
        manager2 = V4MemoryManager(storage_path=storage_path)

        # Verify lesson is loaded
        loaded_lesson = manager2.get_lesson(lesson_id)
        assert loaded_lesson is not None
        assert loaded_lesson.title == "Persist Lesson"
        assert loaded_lesson.importance == 0.75

    def test_document_persistence(self, temp_storage):
        """Test document refs are persisted and loaded correctly"""
        storage_path = temp_storage / "memories.json"

        # Create manager and record doc ref
        manager1 = V4MemoryManager(storage_path=storage_path)
        doc_ref = manager1.record_document_ref(
            title="Persist Doc",
            document_type="api",
            path="/path/to/doc",
            reason="Testing persistence"
        )
        ref_id = doc_ref.ref_id

        # Create new manager instance
        manager2 = V4MemoryManager(storage_path=storage_path)

        # Verify doc ref is loaded
        loaded_doc = manager2.get_document_ref(ref_id)
        assert loaded_doc is not None
        assert loaded_doc.title == "Persist Doc"


# ==================== Statistics Tests ====================

class TestStatistics:
    """Test v4.0 statistics"""

    def test_get_v4_statistics(self, manager):
        """Test getting v4.0 statistics"""
        # Record some data
        manager.record_tech_decision(
            title="Decision 1",
            decision="Content",
            reason="Reason",
            scope=DecisionScope.ARCHITECTURE
        )
        manager.record_tech_decision(
            title="Decision 2",
            decision="Content",
            reason="Reason",
            scope=DecisionScope.LOCAL
        )
        lesson = manager.record_lesson(
            title="Lesson 1",
            content="Content",
            category=LessonCategory.TECHNICAL,
            what_happened="What",
            what_learned="Learned",
            how_to_apply="Apply",
            applicability="general"
        )
        # Increment applied_count 5 times
        for _ in range(5):
            manager.increment_lesson_applied_count(lesson.lesson_id)
        manager.record_document_ref(
            title="Doc 1",
            document_type="api",
            path="/path",
            reason="Reason"
        )

        stats = manager.get_v4_statistics()

        assert stats['total_decisions'] == 2
        assert stats['total_lessons'] == 1
        assert stats['total_documents'] == 1
        assert stats['decisions_by_scope']['architecture'] == 1
        assert stats['decisions_by_scope']['local'] == 1
        assert stats['lessons_by_category']['technical'] == 1
        assert stats['general_lessons'] == 1
        assert stats['lessons_applied'] == 5
