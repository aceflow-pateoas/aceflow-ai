"""
Unit tests for v4.0 Memory Models

Tests for:
- TechDecision data model
- Lesson data model
- DocumentRef data model
- DecisionDetector (A+B+C rule)
- LessonExtractor (keyword pattern)
- MemoryInjectionContext
- RelevanceScore
"""

import pytest
from datetime import datetime
from aceflow.workflow.memory.v4_models import (
    V4MemoryType,
    DecisionScope,
    LessonCategory,
    TechDecision,
    Lesson,
    DocumentRef,
    RelevanceScore,
    MemoryInjectionContext,
    DecisionDetector,
    LessonExtractor
)


# ==================== TechDecision Tests ====================

class TestTechDecision:
    """Test TechDecision data model"""

    def test_tech_decision_creation(self):
        """Test creating a TechDecision"""
        decision = TechDecision(
            decision_id="dec_001",
            title="选择 PostgreSQL 作为主数据库",
            decision="使用 PostgreSQL 作为主数据库",
            reason="需要复杂查询和事务支持",
            scope=DecisionScope.ARCHITECTURE,
            alternatives=["MySQL", "MongoDB"],
            tech_stack=["PostgreSQL", "SQLAlchemy"],
            impact="影响整个数据层架构"
        )

        assert decision.decision_id == "dec_001"
        assert decision.scope == DecisionScope.ARCHITECTURE
        assert len(decision.alternatives) == 2
        assert decision.importance == 0.8  # default
        assert decision.created_by == "ai"  # default

    def test_tech_decision_serialization(self):
        """Test TechDecision to_dict and from_dict"""
        original = TechDecision(
            decision_id="dec_002",
            title="采用 Redis 缓存",
            decision="使用 Redis 作为缓存层",
            reason="提高读取性能",
            scope=DecisionScope.MODULE,
            alternatives=["Memcached"],
            tech_stack=["Redis"],
            impact="提升 API 响应速度 50%",
            work_item_id="work_123",
            stage_id="design",
            tags=["performance", "cache"],
            importance=0.9
        )

        # Serialize
        data = original.to_dict()
        assert data['decision_id'] == "dec_002"
        assert data['scope'] == "module"
        assert data['importance'] == 0.9

        # Deserialize
        restored = TechDecision.from_dict(data)
        assert restored.decision_id == original.decision_id
        assert restored.scope == original.scope
        assert restored.title == original.title
        assert restored.tech_stack == original.tech_stack

    def test_tech_decision_with_related_decisions(self):
        """Test TechDecision with related_decisions"""
        decision = TechDecision(
            decision_id="dec_003",
            title="API 认证方案",
            decision="使用 JWT 认证",
            reason="无状态认证适合微服务架构",
            scope=DecisionScope.ARCHITECTURE,
            related_decisions=["dec_001", "dec_002"]  # 依赖数据库和缓存决策
        )

        assert len(decision.related_decisions) == 2
        assert "dec_001" in decision.related_decisions


# ==================== Lesson Tests ====================

class TestLesson:
    """Test Lesson data model"""

    def test_lesson_creation(self):
        """Test creating a Lesson"""
        lesson = Lesson(
            lesson_id="lesson_001",
            title="避免在循环中查询数据库",
            content="在 for 循环中执行数据库查询导致 N+1 问题",
            category=LessonCategory.TECHNICAL,
            what_happened="用户列表页面加载缓慢",
            what_learned="应该使用 eager loading 或 join 查询",
            how_to_apply="使用 SQLAlchemy 的 joinedload() 或 subqueryload()"
        )

        assert lesson.lesson_id == "lesson_001"
        assert lesson.category == LessonCategory.TECHNICAL
        assert lesson.importance == 0.7  # default
        assert lesson.applied_count == 0  # default
        assert lesson.applicability == "general"  # default

    def test_lesson_serialization(self):
        """Test Lesson to_dict and from_dict"""
        original = Lesson(
            lesson_id="lesson_002",
            title="测试先行的重要性",
            content="先写测试可以发现设计问题",
            category=LessonCategory.BEST_PRACTICE,
            what_happened="重构时发现很多边界情况未覆盖",
            what_learned="TDD 可以提高代码质量",
            how_to_apply="遵循 Red-Green-Refactor 循环",
            applicability="specific",
            applicable_scenarios=["unit_testing", "refactoring"],
            work_item_id="work_456",
            stage_id="testing",
            tags=["tdd", "testing"],
            importance=0.8,
            applied_count=3
        )

        # Serialize
        data = original.to_dict()
        assert data['lesson_id'] == "lesson_002"
        assert data['category'] == "best_practice"
        assert data['applied_count'] == 3

        # Deserialize
        restored = Lesson.from_dict(data)
        assert restored.lesson_id == original.lesson_id
        assert restored.category == original.category
        assert restored.applied_count == original.applied_count
        assert restored.applicable_scenarios == original.applicable_scenarios

    def test_lesson_applied_count_increment(self):
        """Test incrementing applied_count"""
        lesson = Lesson(
            lesson_id="lesson_003",
            title="使用参数化查询防止 SQL 注入",
            content="永远不要拼接 SQL 字符串",
            category=LessonCategory.BEST_PRACTICE,
            applied_count=0
        )

        assert lesson.applied_count == 0
        lesson.applied_count += 1
        assert lesson.applied_count == 1


# ==================== DocumentRef Tests ====================

class TestDocumentRef:
    """Test DocumentRef data model"""

    def test_document_ref_creation(self):
        """Test creating a DocumentRef"""
        doc_ref = DocumentRef(
            ref_id="ref_001",
            title="PostgreSQL 官方文档 - 索引优化",
            document_type="api",
            path="https://www.postgresql.org/docs/current/indexes.html",
            section="Chapter 11.5",
            reason="设计数据库索引策略",
            key_points=["B-tree 索引适合范围查询", "考虑使用部分索引"]
        )

        assert doc_ref.ref_id == "ref_001"
        assert doc_ref.document_type == "api"
        assert len(doc_ref.key_points) == 2

    def test_document_ref_serialization(self):
        """Test DocumentRef to_dict and from_dict"""
        original = DocumentRef(
            ref_id="ref_002",
            title="项目 API 设计规范",
            document_type="design",
            path="docs/api_design_guide.md",
            section="RESTful API 设计原则",
            reason="统一 API 设计风格",
            key_points=["使用名词而非动词", "正确使用 HTTP 方法"],
            work_item_id="work_789",
            related_memories=["dec_003"],
            tags=["api", "design"]
        )

        # Serialize
        data = original.to_dict()
        assert data['ref_id'] == "ref_002"
        assert data['document_type'] == "design"
        assert len(data['key_points']) == 2

        # Deserialize
        restored = DocumentRef.from_dict(data)
        assert restored.ref_id == original.ref_id
        assert restored.path == original.path
        assert restored.key_points == original.key_points


# ==================== RelevanceScore Tests ====================

class TestRelevanceScore:
    """Test RelevanceScore data model"""

    def test_relevance_score_creation(self):
        """Test creating a RelevanceScore"""
        score = RelevanceScore(
            memory_id="mem_001",
            total_score=0.85,
            keyword_score=0.9,
            tag_score=0.8,
            stage_score=1.0,
            importance_score=0.7,
            matched_keywords=["database", "query"],
            matched_tags=["performance"],
            reason="关键词匹配度高 (2个)；标签匹配度高 (1个)；阶段高度相关"
        )

        assert score.memory_id == "mem_001"
        assert score.total_score == 0.85
        assert len(score.matched_keywords) == 2
        assert len(score.matched_tags) == 1

    def test_relevance_score_comparison(self):
        """Test RelevanceScore comparison (for sorting)"""
        score1 = RelevanceScore(memory_id="m1", total_score=0.9)
        score2 = RelevanceScore(memory_id="m2", total_score=0.7)

        # __lt__ is implemented for sorting (higher score comes first)
        assert score1 < score2  # 0.9 > 0.7, so score1 < score2 in sort order


# ==================== MemoryInjectionContext Tests ====================

class TestMemoryInjectionContext:
    """Test MemoryInjectionContext data model"""

    def test_memory_injection_context_creation(self):
        """Test creating a MemoryInjectionContext"""
        context = MemoryInjectionContext(
            work_item_id="work_123",
            work_item_type="feature",
            work_item_title="用户认证功能",
            work_item_description="实现 JWT 认证和权限管理",
            stage_id="implementation",
            stage_name="编码实现",
            stage_type="implementation",
            max_memories=5,
            min_relevance=0.3
        )

        assert context.work_item_id == "work_123"
        assert context.stage_type == "implementation"
        assert context.max_memories == 5
        assert context.min_relevance == 0.3

    def test_extract_keywords(self):
        """Test extracting keywords from work item"""
        context = MemoryInjectionContext(
            work_item_id="work_456",
            work_item_type="feature",
            work_item_title="数据库查询优化",
            work_item_description="优化用户列表的查询性能，避免 N+1 问题",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )

        keywords = context.extract_keywords()

        # Keywords are extracted by simple word splitting
        # For Chinese text without spaces, words may be extracted as phrases
        assert len(keywords) > 0
        # Should contain some extracted keywords/phrases
        assert any("优化" in kw or "查询" in kw for kw in keywords)
        # 停用词应该被过滤
        assert "的" not in keywords

    def test_extract_tags(self):
        """Test extracting tags from work item"""
        context = MemoryInjectionContext(
            work_item_id="work_789",
            work_item_type="feature",
            work_item_title="用户登录 API",
            work_item_description="实现 RESTful API 接口，支持 JWT 认证",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )

        tags = context.extract_tags()

        # 应该包含工作流类型和阶段类型
        assert "feature" in tags
        assert "design" in tags

        # 应该包含检测到的技术标签
        assert "api" in tags
        assert "auth" in tags


# ==================== DecisionDetector Tests ====================

class TestDecisionDetector:
    """Test DecisionDetector (A+B+C rule)"""

    def test_detect_decision_with_all_criteria(self):
        """Test detecting decision with A+B+C (all criteria met)"""
        text = "我们决定选择 PostgreSQL 作为主数据库，因为需要支持多模块的复杂查询。"

        result = DecisionDetector.detect(text)

        assert result is not None
        assert result['detected'] is True
        assert result['has_wide_impact'] is True
        assert result['is_tech_selection'] is True
        assert result['confidence'] == 0.9  # A+B+C all met

    def test_detect_decision_with_a_and_b(self):
        """Test detecting decision with A+B (decision + wide impact)"""
        text = "团队决定采用微服务架构，这将影响整个系统级的设计。"

        result = DecisionDetector.detect(text)

        assert result is not None
        assert result['detected'] is True
        assert result['has_wide_impact'] is True
        assert result['confidence'] == 0.7  # Only A+B

    def test_detect_decision_with_a_and_c(self):
        """Test detecting decision with A+C (decision + tech selection)"""
        text = "我们使用 Redis 作为缓存框架来提升性能。"

        result = DecisionDetector.detect(text)

        assert result is not None
        assert result['detected'] is True
        assert result['is_tech_selection'] is True
        assert result['confidence'] == 0.7  # Only A+C

    def test_detect_decision_english(self):
        """Test detecting decision in English"""
        text = "We decided to use PostgreSQL as the database for this project."

        result = DecisionDetector.detect(text)

        assert result is not None
        assert result['detected'] is True
        assert result['is_tech_selection'] is True

    def test_no_detection_without_decision_keyword(self):
        """Test no detection when decision keyword is missing"""
        text = "PostgreSQL 是一个很好的数据库，支持复杂查询。"

        result = DecisionDetector.detect(text)

        assert result is None  # No decision keyword (A missing)

    def test_no_detection_with_only_a(self):
        """Test no detection with only A (decision keyword but no B or C)"""
        text = "我们选择了一个好的方案。"

        result = DecisionDetector.detect(text)

        assert result is None  # Only A, missing B and C


# ==================== LessonExtractor Tests ====================

class TestLessonExtractor:
    """Test LessonExtractor (keyword pattern)"""

    def test_extract_lesson_with_problem_and_solution(self):
        """Test extracting lesson with problem and solution"""
        text = "我们遇到了 N+1 查询问题导致性能下降，解决方法是使用 eager loading。"

        result = LessonExtractor.extract(text)

        assert result is not None
        assert result['detected'] is True
        assert result['has_problem'] is True
        assert result['has_solution'] is True
        assert result['is_complete'] is True
        assert result['confidence'] == 0.9

    def test_extract_lesson_with_only_problem(self):
        """Test extracting lesson with only problem"""
        text = "在测试中发现了一个严重的问题，导致用户数据丢失。"

        result = LessonExtractor.extract(text)

        assert result is not None
        assert result['detected'] is True
        assert result['has_problem'] is True
        assert result['has_solution'] is False
        assert result['is_complete'] is False
        assert result['confidence'] == 0.6

    def test_extract_lesson_with_best_practice(self):
        """Test extracting lesson with best practice keyword"""
        text = "最佳实践建议：始终使用参数化查询来避免 SQL 注入。"

        result = LessonExtractor.extract(text)

        assert result is not None
        assert result['detected'] is True

    def test_extract_lesson_english(self):
        """Test extracting lesson in English"""
        text = "We learned that using async I/O can significantly improve performance."

        result = LessonExtractor.extract(text)

        assert result is not None
        assert result['detected'] is True

    def test_no_extraction_without_lesson_keyword(self):
        """Test no extraction when lesson keyword is missing"""
        text = "数据库查询很慢，需要优化。"

        result = LessonExtractor.extract(text)

        assert result is None  # No lesson keyword


# ==================== Integration Tests ====================

class TestV4ModelsIntegration:
    """Integration tests for v4 models"""

    def test_tech_decision_to_memory_injection_context(self):
        """Test using TechDecision with MemoryInjectionContext"""
        decision = TechDecision(
            decision_id="dec_100",
            title="选择 FastAPI 框架",
            decision="使用 FastAPI 构建 API",
            reason="支持异步和自动文档生成",
            scope=DecisionScope.ARCHITECTURE,
            tech_stack=["FastAPI", "Pydantic"],
            tags=["api", "async", "framework"]
        )

        context = MemoryInjectionContext(
            work_item_id="work_new",
            work_item_type="feature",
            work_item_title="构建异步 API",
            work_item_description="使用现代框架构建高性能 API",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )

        # Extract keywords and tags from context
        context.extract_keywords()
        context.extract_tags()

        # Check if decision tags overlap with context tags
        assert "api" in context.search_tags
        assert "api" in decision.tags

    def test_lesson_applied_count_tracking(self):
        """Test tracking lesson application"""
        lesson = Lesson(
            lesson_id="lesson_100",
            title="使用事务保证数据一致性",
            content="数据库操作应该在事务中执行",
            category=LessonCategory.TECHNICAL,
            applied_count=0
        )

        # Simulate applying the lesson multiple times
        for i in range(3):
            lesson.applied_count += 1

        assert lesson.applied_count == 3

        # Serialize to check persistence
        data = lesson.to_dict()
        assert data['applied_count'] == 3

        # Restore and verify
        restored = Lesson.from_dict(data)
        assert restored.applied_count == 3
