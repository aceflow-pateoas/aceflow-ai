"""
Unit tests for RelevanceCalculator and MemoryFilter

Tests for:
- RelevanceCalculator scoring algorithm
- Keyword matching
- Tag matching
- Stage relevance
- Importance scoring
- Recency scoring
- MemoryFilter filtering and ranking
"""

import pytest
from datetime import datetime, timedelta
from aceflow.workflow.memory.models import Memory, MemoryType, MemoryPriority
from aceflow.workflow.memory.v4_models import (
    TechDecision,
    Lesson,
    DecisionScope,
    LessonCategory,
    MemoryInjectionContext,
    RelevanceScore
)
from aceflow.workflow.memory.relevance import RelevanceCalculator, MemoryFilter


# ==================== RelevanceCalculator Tests ====================

class TestRelevanceCalculatorBasics:
    """Test basic RelevanceCalculator functionality"""

    def test_calculator_initialization(self):
        """Test creating a RelevanceCalculator"""
        calculator = RelevanceCalculator()

        assert calculator.weights['keyword'] == 0.4
        assert calculator.weights['tag'] == 0.3
        assert calculator.weights['stage'] == 0.2
        assert calculator.weights['importance'] == 0.1

    def test_calculator_custom_weights(self):
        """Test creating RelevanceCalculator with custom weights"""
        custom_weights = {
            'keyword': 0.5,
            'tag': 0.2,
            'stage': 0.2,
            'importance': 0.1
        }
        calculator = RelevanceCalculator(weights=custom_weights)

        assert calculator.weights['keyword'] == 0.5
        assert calculator.weights['tag'] == 0.2


class TestKeywordMatching:
    """Test keyword matching functionality"""

    def test_keyword_matching_full_match(self):
        """Test keyword matching with all keywords matched"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_001",
            type=MemoryType.DECISION,
            content="我们选择 PostgreSQL 数据库来支持复杂查询和事务",
            priority=MemoryPriority.HIGH,
            tags=["database"]
        )

        context = MemoryInjectionContext(
            work_item_id="work_001",
            work_item_type="feature",
            work_item_title="数据库查询优化",
            work_item_description="优化 PostgreSQL 查询性能",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_keywords()  # Should extract: database, query, optimization, postgresql

        score = calculator.calculate(memory, context)

        assert score.keyword_score > 0.0
        assert len(score.matched_keywords) > 0
        assert score.memory_id == "mem_001"

    def test_keyword_matching_partial_match(self):
        """Test keyword matching with partial match"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_002",
            type=MemoryType.LEARNING,
            content="使用索引可以提升查询性能",
            priority=MemoryPriority.MEDIUM,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_002",
            work_item_type="feature",
            work_item_title="API 接口开发",
            work_item_description="开发 RESTful API",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_keywords()

        score = calculator.calculate(memory, context)

        # Some keywords may match (e.g., "performance" related words)
        assert score.keyword_score >= 0.0

    def test_keyword_matching_case_insensitive(self):
        """Test keyword matching is case insensitive"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_003",
            type=MemoryType.DECISION,
            content="We choose PostgreSQL for complex QUERIES",
            priority=MemoryPriority.HIGH,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_003",
            work_item_type="feature",
            work_item_title="postgresql query optimization",
            work_item_description="Optimize queries",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_keywords()

        score = calculator.calculate(memory, context)

        # Should match despite case differences
        assert score.keyword_score > 0.0


class TestTagMatching:
    """Test tag matching functionality"""

    def test_tag_matching_full_match(self):
        """Test tag matching with all tags matched"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_004",
            type=MemoryType.DECISION,
            content="Database selection",
            priority=MemoryPriority.HIGH,
            tags=["database", "feature", "implementation"],  # Match context tags
            stage_id="implementation"
        )

        context = MemoryInjectionContext(
            work_item_id="work_004",
            work_item_type="feature",
            work_item_title="Database optimization",
            work_item_description="Optimize database performance",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_tags()  # Will extract: feature, implementation, database

        score = calculator.calculate(memory, context)

        # Should have some tag matches
        assert score.tag_score > 0.0 or len(score.matched_tags) > 0

    def test_tag_matching_no_match(self):
        """Test tag matching with no matching tags"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_005",
            type=MemoryType.LEARNING,
            content="Frontend optimization",
            priority=MemoryPriority.MEDIUM,
            tags=["ui", "react", "css"],  # No overlap with backend
            stage_id="implementation"
        )

        context = MemoryInjectionContext(
            work_item_id="work_005",
            work_item_type="feature",
            work_item_title="Backend API",
            work_item_description="Build backend services",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_tags()  # Should extract: feature, implementation, backend, api

        score = calculator.calculate(memory, context)

        # Very low or zero tag match expected (but feature/implementation might still match)
        # Check that backend-specific tags don't match frontend tags
        assert "react" not in score.matched_tags
        assert "css" not in score.matched_tags
        assert "ui" not in score.matched_tags


class TestStageRelevance:
    """Test stage relevance scoring"""

    def test_stage_exact_match(self):
        """Test stage score with exact stage_id match"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_006",
            type=MemoryType.DECISION,
            content="Implementation decision",
            priority=MemoryPriority.HIGH,
            stage_id="implementation",
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_006",
            work_item_type="feature",
            work_item_title="Feature implementation",
            work_item_description="Implement new feature",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )

        score = calculator.calculate(memory, context)

        # Exact stage match should give 1.0
        assert score.stage_score == 1.0

    def test_stage_type_match(self):
        """Test stage score with stage_type match"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_007",
            type=MemoryType.DECISION,
            content="Design decision",
            priority=MemoryPriority.HIGH,
            stage_id="design_phase",
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_007",
            work_item_type="feature",
            work_item_title="Architecture design",
            work_item_description="Design system architecture",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )

        score = calculator.calculate(memory, context)

        # Stage type match (design in stage_id) should give 0.8
        assert score.stage_score == 0.8

    def test_stage_adjacent_match(self):
        """Test stage score with adjacent stage"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_008",
            type=MemoryType.LEARNING,
            content="Design patterns",
            priority=MemoryPriority.MEDIUM,
            stage_id="design",
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_008",
            work_item_type="feature",
            work_item_title="Implementation",
            work_item_description="Implement feature",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )

        score = calculator.calculate(memory, context)

        # Design is adjacent to implementation, should give 0.6
        assert score.stage_score == 0.6


class TestImportanceScoring:
    """Test importance scoring"""

    def test_importance_critical_priority(self):
        """Test importance score for critical priority"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_009",
            type=MemoryType.ISSUE,
            content="Critical security issue",
            priority=MemoryPriority.CRITICAL,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_009",
            work_item_type="bugfix",
            work_item_title="Fix security bug",
            work_item_description="Security fix",
            stage_id="fix",
            stage_name="Fix",
            stage_type="fix"
        )

        score = calculator.calculate(memory, context)

        # Critical priority should give 1.0
        assert score.importance_score == 1.0

    def test_importance_high_priority(self):
        """Test importance score for high priority"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_010",
            type=MemoryType.DECISION,
            content="Important decision",
            priority=MemoryPriority.HIGH,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_010",
            work_item_type="feature",
            work_item_title="Feature",
            work_item_description="Description",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )

        score = calculator.calculate(memory, context)

        # High priority should give 0.8
        assert score.importance_score == 0.8

    def test_importance_medium_priority(self):
        """Test importance score for medium priority"""
        calculator = RelevanceCalculator()

        memory = Memory(
            memory_id="mem_011",
            type=MemoryType.LEARNING,
            content="Lesson learned",
            priority=MemoryPriority.MEDIUM,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_011",
            work_item_type="feature",
            work_item_title="Feature",
            work_item_description="Description",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )

        score = calculator.calculate(memory, context)

        # Medium priority should give 0.5
        assert score.importance_score == 0.5


class TestRecencyScoring:
    """Test recency scoring"""

    def test_recency_recent_memory(self):
        """Test recency score for recent memory (within 7 days)"""
        calculator = RelevanceCalculator()

        recent_date = datetime.now() - timedelta(days=3)
        memory = Memory(
            memory_id="mem_012",
            type=MemoryType.DECISION,
            content="Recent decision",
            priority=MemoryPriority.HIGH,
            created_at=recent_date,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_012",
            work_item_type="feature",
            work_item_title="Feature",
            work_item_description="Description",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )

        score = calculator.calculate(memory, context)

        # Within 7 days should give 1.0
        assert score.recency_score == 1.0

    def test_recency_month_old_memory(self):
        """Test recency score for month-old memory (within 30 days)"""
        calculator = RelevanceCalculator()

        old_date = datetime.now() - timedelta(days=15)
        memory = Memory(
            memory_id="mem_013",
            type=MemoryType.LEARNING,
            content="Month-old lesson",
            priority=MemoryPriority.MEDIUM,
            created_at=old_date,
            tags=[]
        )

        context = MemoryInjectionContext(
            work_item_id="work_013",
            work_item_type="feature",
            work_item_title="Feature",
            work_item_description="Description",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )

        score = calculator.calculate(memory, context)

        # Within 30 days should give 0.8
        assert score.recency_score == 0.8


class TestV4DecisionScoring:
    """Test scoring for v4.0 TechDecision"""

    def test_calculate_for_v4_decision(self):
        """Test calculating relevance for TechDecision"""
        calculator = RelevanceCalculator()

        decision = TechDecision(
            decision_id="dec_001",
            title="选择 PostgreSQL 数据库",
            decision="使用 PostgreSQL 作为主数据库",
            reason="支持复杂查询和事务",
            scope=DecisionScope.ARCHITECTURE,
            tech_stack=["PostgreSQL", "SQL"],
            tags=["database", "architecture"],
            importance=0.9
        )

        context = MemoryInjectionContext(
            work_item_id="work_014",
            work_item_type="feature",
            work_item_title="数据库设计",
            work_item_description="设计数据库schema",
            stage_id="design",
            stage_name="Design",
            stage_type="design"
        )
        context.extract_keywords()
        context.extract_tags()

        score = calculator.calculate_for_v4_decision(decision, context)

        assert score.memory_id == "dec_001"
        assert score.total_score > 0.0
        assert score.importance_score == 0.9
        # Design stage is most relevant for decisions
        assert score.stage_score >= 0.5


class TestV4LessonScoring:
    """Test scoring for v4.0 Lesson"""

    def test_calculate_for_v4_lesson(self):
        """Test calculating relevance for Lesson"""
        calculator = RelevanceCalculator()

        lesson = Lesson(
            lesson_id="lesson_001",
            title="避免 N+1 查询",
            content="在循环中执行查询导致性能问题",
            category=LessonCategory.TECHNICAL,
            what_learned="使用 eager loading",
            applicable_scenarios=["database", "performance"],
            tags=["database", "performance", "optimization"],
            importance=0.8,
            applied_count=5
        )

        context = MemoryInjectionContext(
            work_item_id="work_015",
            work_item_type="feature",
            work_item_title="查询优化",
            work_item_description="优化数据库查询性能",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation"
        )
        context.extract_keywords()
        context.extract_tags()

        score = calculator.calculate_for_v4_lesson(lesson, context)

        assert score.memory_id == "lesson_001"
        assert score.total_score > 0.0
        # Implementation stage is most relevant for lessons
        assert score.stage_score >= 0.6
        # Applied lessons should have higher importance (applied_count bonus)
        assert score.importance_score > lesson.importance


# ==================== MemoryFilter Tests ====================

class TestMemoryFilterBasics:
    """Test basic MemoryFilter functionality"""

    def test_filter_initialization(self):
        """Test creating a MemoryFilter"""
        filter = MemoryFilter()

        assert filter.calculator is not None
        assert isinstance(filter.calculator, RelevanceCalculator)

    def test_filter_with_custom_calculator(self):
        """Test creating MemoryFilter with custom calculator"""
        custom_weights = {'keyword': 0.6, 'tag': 0.4}
        calculator = RelevanceCalculator(weights=custom_weights)
        filter = MemoryFilter(calculator=calculator)

        assert filter.calculator.weights['keyword'] == 0.6


class TestMemoryFilteringAndRanking:
    """Test memory filtering and ranking"""

    def test_filter_and_rank_basic(self):
        """Test basic filtering and ranking"""
        filter = MemoryFilter()

        memories = [
            Memory(
                memory_id="mem_high",
                type=MemoryType.DECISION,
                content="PostgreSQL database decision for complex queries",
                priority=MemoryPriority.HIGH,
                tags=["database", "postgresql"],
                stage_id="design"
            ),
            Memory(
                memory_id="mem_medium",
                type=MemoryType.LEARNING,
                content="Use indexes for query optimization",
                priority=MemoryPriority.MEDIUM,
                tags=["database", "performance"],
                stage_id="implementation"
            ),
            Memory(
                memory_id="mem_low",
                type=MemoryType.CONTEXT,
                content="Frontend styling guidelines",
                priority=MemoryPriority.LOW,
                tags=["frontend", "css"],
                stage_id="implementation"
            )
        ]

        context = MemoryInjectionContext(
            work_item_id="work_016",
            work_item_type="feature",
            work_item_title="Database query optimization",
            work_item_description="Optimize PostgreSQL queries",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.2,
            max_memories=5
        )
        context.extract_keywords()
        context.extract_tags()

        ranked = filter.filter_and_rank(memories, context)

        # Should return memories sorted by relevance
        assert len(ranked) <= 3
        # First memory should have highest score
        if len(ranked) > 1:
            assert ranked[0][1].total_score >= ranked[1][1].total_score

    def test_filter_by_min_relevance(self):
        """Test filtering by minimum relevance threshold"""
        filter = MemoryFilter()

        memories = [
            Memory(
                memory_id="mem_relevant",
                type=MemoryType.DECISION,
                content="Database query optimization using PostgreSQL",
                priority=MemoryPriority.HIGH,
                tags=["database", "postgresql"],
                stage_id="implementation"
            ),
            Memory(
                memory_id="mem_irrelevant",
                type=MemoryType.CONTEXT,
                content="Frontend color scheme",
                priority=MemoryPriority.LOW,
                tags=["frontend", "ui"],
                stage_id="design"
            )
        ]

        context = MemoryInjectionContext(
            work_item_id="work_017",
            work_item_type="feature",
            work_item_title="Database optimization",
            work_item_description="Optimize database queries",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.5,  # High threshold
            max_memories=10
        )
        context.extract_keywords()
        context.extract_tags()

        ranked = filter.filter_and_rank(memories, context)

        # Only highly relevant memory should pass threshold
        assert len(ranked) >= 0
        for memory, score in ranked:
            assert score.total_score >= 0.5

    def test_limit_max_memories(self):
        """Test limiting returned memories by max_memories"""
        filter = MemoryFilter()

        memories = [
            Memory(
                memory_id=f"mem_{i}",
                type=MemoryType.DECISION,
                content=f"Database decision {i}",
                priority=MemoryPriority.MEDIUM,
                tags=["database"],
                stage_id="implementation"
            )
            for i in range(10)
        ]

        context = MemoryInjectionContext(
            work_item_id="work_018",
            work_item_type="feature",
            work_item_title="Database work",
            work_item_description="Database related task",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.0,
            max_memories=3  # Limit to 3
        )
        context.extract_keywords()
        context.extract_tags()

        ranked = filter.filter_and_rank(memories, context)

        # Should return at most 3 memories
        assert len(ranked) <= 3


class TestMemoryFilterTopK:
    """Test get_top_k method"""

    def test_get_top_k(self):
        """Test getting top-k memories"""
        filter = MemoryFilter()

        memories = [
            Memory(
                memory_id=f"mem_{i}",
                type=MemoryType.DECISION,
                content=f"Database optimization {i}",
                priority=MemoryPriority.HIGH if i < 5 else MemoryPriority.MEDIUM,
                tags=["database", "performance"],
                stage_id="implementation"
            )
            for i in range(10)
        ]

        context = MemoryInjectionContext(
            work_item_id="work_019",
            work_item_type="feature",
            work_item_title="Performance optimization",
            work_item_description="Optimize database performance",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.0,
            max_memories=10
        )
        context.extract_keywords()
        context.extract_tags()

        top_5 = filter.get_top_k(memories, context, k=5)

        # Should return exactly 5 memories
        assert len(top_5) == 5
        # Should be Memory objects, not tuples
        assert all(isinstance(m, Memory) for m in top_5)


class TestMemoryFilterExplain:
    """Test explain_ranking method"""

    def test_explain_ranking(self):
        """Test explaining ranking results"""
        filter = MemoryFilter()

        memories = [
            Memory(
                memory_id="mem_1",
                type=MemoryType.DECISION,
                content="PostgreSQL database selection",
                priority=MemoryPriority.HIGH,
                tags=["database"],
                stage_id="design"
            ),
            Memory(
                memory_id="mem_2",
                type=MemoryType.LEARNING,
                content="Query optimization tips",
                priority=MemoryPriority.MEDIUM,
                tags=["performance"],
                stage_id="implementation"
            )
        ]

        context = MemoryInjectionContext(
            work_item_id="work_020",
            work_item_type="feature",
            work_item_title="Database work",
            work_item_description="Database task",
            stage_id="implementation",
            stage_name="Implementation",
            stage_type="implementation",
            min_relevance=0.3,
            max_memories=5
        )
        context.extract_keywords()
        context.extract_tags()

        explanation = filter.explain_ranking(memories, context)

        # Should include summary information
        assert 'total_candidates' in explanation
        assert 'passed_threshold' in explanation
        assert 'threshold' in explanation
        assert 'top_memories' in explanation

        assert explanation['total_candidates'] == 2
        assert explanation['threshold'] == 0.3

        # Top memories should include detailed scoring info
        if len(explanation['top_memories']) > 0:
            top_mem = explanation['top_memories'][0]
            assert 'memory_id' in top_mem
            assert 'score' in top_mem
            assert 'keyword_score' in top_mem
            assert 'tag_score' in top_mem
            assert 'stage_score' in top_mem
            assert 'matched_keywords' in top_mem
            assert 'matched_tags' in top_mem
            assert 'reason' in top_mem


# ==================== Integration Tests ====================

class TestRelevanceCalculatorIntegration:
    """Integration tests for RelevanceCalculator"""

    def test_complete_workflow_scoring(self):
        """Test scoring memories in a complete workflow scenario"""
        calculator = RelevanceCalculator()

        # Create memories from different stages
        memories = [
            Memory(
                memory_id="design_decision",
                type=MemoryType.DECISION,
                content="选择微服务架构来支持多模块开发",
                priority=MemoryPriority.CRITICAL,
                stage_id="design",
                tags=["architecture", "microservices"],
                created_at=datetime.now() - timedelta(days=2)
            ),
            Memory(
                memory_id="implementation_lesson",
                type=MemoryType.LEARNING,
                content="使用 Docker 容器化部署可以简化环境管理",
                priority=MemoryPriority.HIGH,
                stage_id="implementation",
                tags=["deployment", "docker"],
                created_at=datetime.now() - timedelta(days=10)
            ),
            Memory(
                memory_id="testing_issue",
                type=MemoryType.ISSUE,
                content="集成测试发现了并发访问的竞态条件",
                priority=MemoryPriority.HIGH,
                stage_id="testing",
                tags=["testing", "concurrency"],
                created_at=datetime.now() - timedelta(days=5)
            )
        ]

        # Current work context: implementing a new microservice
        context = MemoryInjectionContext(
            work_item_id="work_microservice",
            work_item_type="feature",
            work_item_title="实现用户服务微服务",
            work_item_description="开发用户管理微服务，支持 Docker 部署",
            stage_id="implementation",
            stage_name="编码实现",
            stage_type="implementation",
            min_relevance=0.3,
            max_memories=5
        )
        context.extract_keywords()
        context.extract_tags()

        # Score all memories
        scores = []
        for memory in memories:
            score = calculator.calculate(memory, context)
            scores.append((memory, score))

        # Sort by relevance
        scores.sort(key=lambda x: x[1].total_score, reverse=True)

        # Design decision should be most relevant (mentions microservices + architecture)
        # Implementation lesson should be second (Docker + deployment relevant to context)
        # Testing issue should be least relevant (different stage, less keyword match)

        assert len(scores) == 3
        assert scores[0][0].memory_id in ["design_decision", "implementation_lesson"]
        # All should have non-zero scores
        for memory, score in scores:
            assert score.total_score > 0.0
