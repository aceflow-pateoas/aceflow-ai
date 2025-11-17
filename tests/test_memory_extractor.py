"""
Unit tests for MemoryExtractor

Tests for:
- Batch extraction from stage outputs
- Single decision/lesson extraction
- Auto-record functionality
- User confirmation workflow
- Text segmentation
- Summary generation
- Integration with V4MemoryManager
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.memory.extractor import MemoryExtractor, ExtractionResult
from aceflow.workflow.memory.v4_manager import V4MemoryManager
from aceflow.workflow.memory.v4_models import (
    DecisionScope, LessonCategory
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
def memory_manager(temp_storage):
    """创建V4MemoryManager实例"""
    storage_path = temp_storage / "memories.json"
    return V4MemoryManager(storage_path=storage_path)


@pytest.fixture
def extractor(memory_manager):
    """创建MemoryExtractor实例"""
    return MemoryExtractor(memory_manager)


# ==================== Batch Extraction Tests ====================

class TestBatchExtraction:
    """Test batch extraction from stage outputs"""

    def test_extract_from_stage_output_with_decisions(self, extractor):
        """Test extracting decisions from stage output"""
        stage_output = """
        经过详细的技术评估，我们决定选择 PostgreSQL 作为主数据库，因为需要支持多模块的复杂查询和事务管理。
        备选方案包括 MySQL 和 MongoDB，但它们在复杂查询性能上不如 PostgreSQL。

        这个决策将影响整个数据层架构和长期的系统扩展性。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_001",
            stage_id="design",
            auto_record=False,
            extract_decisions=True,
            extract_lessons=False
        )

        assert 'decisions' in results
        assert 'lessons' in results
        assert 'summary' in results

        # Should detect at least one decision
        assert results['summary']['total_decisions'] >= 1

        # Check first decision
        if results['decisions']:
            decision = results['decisions'][0]
            assert decision.extraction_type == 'decision'
            assert decision.detected is True
            assert decision.confidence > 0.5
            assert decision.recorded_object is None  # auto_record=False

    def test_extract_from_stage_output_with_lessons(self, extractor):
        """Test extracting lessons from stage output"""
        stage_output = """
        在实现过程中，我们遇到了 N+1 查询问题导致性能下降。
        经过分析发现，在循环中执行单独的查询会导致大量数据库往返。
        解决方法是使用 ORM 的 eager loading 功能，通过一次查询获取所有需要的数据。
        这个经验教训告诉我们，在处理关联数据时，应该始终考虑使用批量加载策略。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_002",
            stage_id="implementation",
            auto_record=False,
            extract_decisions=False,
            extract_lessons=True
        )

        # Should detect at least one lesson
        assert results['summary']['total_lessons'] >= 1

        # Check first lesson
        if results['lessons']:
            lesson = results['lessons'][0]
            assert lesson.extraction_type == 'lesson'
            assert lesson.detected is True
            assert lesson.confidence > 0.5
            assert lesson.recorded_object is None  # auto_record=False

    def test_extract_from_stage_output_with_auto_record(self, extractor):
        """Test auto-recording during extraction"""
        stage_output = """
        我们使用 Redis 作为缓存框架来提升性能，这是一个关键的架构决策。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_003",
            stage_id="design",
            auto_record=True,  # Auto-record
            extract_decisions=True,
            extract_lessons=False
        )

        # Should have recorded objects
        assert results['summary']['recorded_count'] >= 1

        # Check first decision is recorded
        if results['decisions']:
            decision = results['decisions'][0]
            assert decision.recorded_object is not None
            assert hasattr(decision.recorded_object, 'decision_id')

    def test_extract_from_stage_output_mixed_content(self, extractor):
        """Test extracting from content with both decisions and lessons"""
        stage_output = """
        # Design Phase Summary

        我们决定采用微服务架构来构建这个系统，因为需要支持独立部署和扩展。
        这将影响整个系统的长期架构设计。

        在之前的项目中，我们学到一个重要的经验：过早的优化是万恶之源。
        应该先实现功能，然后根据性能测试结果进行针对性优化。
        避免在没有数据支撑的情况下做优化决策。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_004",
            stage_id="design",
            auto_record=False,
            extract_decisions=True,
            extract_lessons=True
        )

        # Should detect both
        assert results['summary']['total_decisions'] >= 1
        assert results['summary']['total_lessons'] >= 1

    def test_extract_from_stage_output_empty_text(self, extractor):
        """Test extraction from empty text"""
        results = extractor.extract_from_stage_output(
            stage_output="",
            work_item_id="work_005",
            stage_id="design",
            auto_record=False
        )

        assert results['summary']['total_decisions'] == 0
        assert results['summary']['total_lessons'] == 0


# ==================== Single Extraction Tests ====================

class TestSingleExtraction:
    """Test single decision/lesson extraction"""

    def test_extract_decision_positive(self, extractor):
        """Test extracting a valid decision"""
        text = "我们选择使用 PostgreSQL 数据库，因为需要支持复杂查询和整体架构设计。"

        result = extractor.extract_decision(
            text=text,
            work_item_id="work_001",
            stage_id="design",
            auto_record=False
        )

        assert result is not None
        assert result.extraction_type == 'decision'
        assert result.detected is True
        assert result.confidence > 0.5
        assert result.text_snippet in text
        assert result.metadata['work_item_id'] == "work_001"
        assert result.metadata['stage_id'] == "design"

    def test_extract_decision_negative(self, extractor):
        """Test no detection when text doesn't match"""
        text = "PostgreSQL 是一个很好的数据库。"

        result = extractor.extract_decision(
            text=text,
            work_item_id="work_002",
            stage_id="design",
            auto_record=False
        )

        assert result is None

    def test_extract_decision_with_auto_record(self, extractor):
        """Test extracting and auto-recording a decision"""
        text = "经过评估，我们决定采用 Redis 作为缓存框架，这将影响系统的整体性能架构。"

        result = extractor.extract_decision(
            text=text,
            work_item_id="work_003",
            stage_id="design",
            auto_record=True
        )

        assert result is not None
        assert result.recorded_object is not None
        assert hasattr(result.recorded_object, 'decision_id')

    def test_extract_lesson_positive(self, extractor):
        """Test extracting a valid lesson"""
        text = """
        我们遇到了内存泄漏问题，导致应用崩溃。
        经过排查发现是事件监听器没有正确移除。
        解决方法是在组件销毁时调用 removeEventListener。
        """

        result = extractor.extract_lesson(
            text=text,
            work_item_id="work_004",
            stage_id="implementation",
            auto_record=False
        )

        assert result is not None
        assert result.extraction_type == 'lesson'
        assert result.detected is True
        assert result.confidence > 0.5

    def test_extract_lesson_negative(self, extractor):
        """Test no detection when text doesn't match"""
        text = "我们需要优化性能。"

        result = extractor.extract_lesson(
            text=text,
            work_item_id="work_005",
            stage_id="implementation",
            auto_record=False
        )

        assert result is None

    def test_extract_lesson_with_auto_record(self, extractor):
        """Test extracting and auto-recording a lesson"""
        text = "最佳实践：始终使用参数化查询来避免 SQL 注入，这是一个重要的安全经验。"

        result = extractor.extract_lesson(
            text=text,
            work_item_id="work_006",
            stage_id="implementation",
            auto_record=True
        )

        assert result is not None
        assert result.recorded_object is not None
        assert hasattr(result.recorded_object, 'lesson_id')


# ==================== User Confirmation Workflow Tests ====================

class TestUserConfirmationWorkflow:
    """Test user confirmation and recording workflow"""

    def test_confirm_and_record_decision(self, extractor):
        """Test confirming and recording a decision"""
        # First, extract without recording
        text = "我们选择 Kubernetes 作为容器编排平台，因为需要支持大规模部署和自动扩展。"

        extraction_result = extractor.extract_decision(
            text=text,
            work_item_id="work_007",
            stage_id="design",
            auto_record=False
        )

        assert extraction_result is not None
        assert extraction_result.recorded_object is None

        # User confirms and provides details
        decision = extractor.confirm_and_record_decision(
            extraction_result=extraction_result,
            title="选择 Kubernetes 作为编排平台",
            decision="使用 Kubernetes 进行容器编排",
            reason="需要支持大规模部署和自动扩展",
            scope=DecisionScope.ARCHITECTURE,
            alternatives=["Docker Swarm", "Nomad"],
            tech_stack=["Kubernetes", "Docker"],
            impact="影响整个部署架构",
            tags=["infrastructure", "containers"]
        )

        assert decision is not None
        assert decision.decision_id.startswith("dec_")
        assert decision.title == "选择 Kubernetes 作为编排平台"
        assert extraction_result.recorded_object == decision

    def test_confirm_and_record_lesson(self, extractor):
        """Test confirming and recording a lesson"""
        # First, extract without recording
        text = """
        我们在生产环境遇到了数据库连接池耗尽的问题。
        原因是没有正确关闭数据库连接。
        解决方法是使用上下文管理器（with语句）自动管理连接。
        """

        extraction_result = extractor.extract_lesson(
            text=text,
            work_item_id="work_008",
            stage_id="implementation",
            auto_record=False
        )

        assert extraction_result is not None
        assert extraction_result.recorded_object is None

        # User confirms and provides details
        lesson = extractor.confirm_and_record_lesson(
            extraction_result=extraction_result,
            title="正确管理数据库连接",
            content="始终使用上下文管理器来管理数据库连接",
            category=LessonCategory.TECHNICAL,
            what_happened="生产环境数据库连接池耗尽",
            what_learned="必须正确关闭数据库连接",
            how_to_apply="使用 with 语句或 try-finally 块",
            applicability="general",
            applicable_scenarios=["database", "resource_management"],
            tags=["database", "best_practice"]
        )

        assert lesson is not None
        assert lesson.lesson_id.startswith("lesson_")
        assert lesson.title == "正确管理数据库连接"
        assert extraction_result.recorded_object == lesson


# ==================== Text Segmentation Tests ====================

class TestTextSegmentation:
    """Test text segmentation logic"""

    def test_segment_text_by_double_newline(self, extractor):
        """Test segmentation by double newline"""
        text = "第一段内容，包含足够的字符数来满足最小长度要求，用于测试分段功能。\n\n第二段内容，也包含足够的字符数，同样用于测试文本分段的功能。\n\n第三段内容，继续提供足够的字符数，确保分段算法正常工作。"

        segments = extractor._segment_text(text)

        # Should have at least one segment
        assert len(segments) >= 1
        # If split into multiple segments, check each one
        for segment in segments:
            assert len(segment) >= 50  # Each segment >= 50 chars

    def test_segment_text_by_single_newline(self, extractor):
        """Test segmentation by single newline when no double newline"""
        text = """
        第一行内容，包含足够的字符数来满足最小长度要求，用于测试分段功能。
        第二行内容，也包含足够的字符数，同样用于测试文本分段的功能。
        第三行内容，继续提供足够的字符数，确保分段算法正常工作。
        """

        segments = extractor._segment_text(text)

        assert len(segments) >= 1

    def test_segment_text_short_content(self, extractor):
        """Test segmentation with short content"""
        text = "Short text."

        segments = extractor._segment_text(text)

        # Should return the original text as single segment
        assert len(segments) == 1
        assert segments[0] == text


# ==================== Summary Generation Tests ====================

class TestSummaryGeneration:
    """Test extraction summary generation"""

    def test_get_extraction_summary_with_decisions(self, extractor):
        """Test generating summary with decisions"""
        stage_output = """
        我们决定使用 GraphQL 作为 API 层，因为需要灵活的数据查询能力，这将影响整个系统架构。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_009",
            stage_id="design",
            auto_record=False,
            extract_decisions=True,
            extract_lessons=False
        )

        summary = extractor.get_extraction_summary(results)

        assert isinstance(summary, str)
        assert "# 记忆提取摘要" in summary
        assert "## 统计" in summary
        assert "技术决策" in summary

        # Should contain decision count
        if results['summary']['total_decisions'] > 0:
            assert "## 检测到的技术决策" in summary

    def test_get_extraction_summary_with_lessons(self, extractor):
        """Test generating summary with lessons"""
        stage_output = """
        我们遇到了性能问题，发现是因为没有使用索引。
        解决方法���在常查询的列上添加索引。
        这个经验教训很重要。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_010",
            stage_id="implementation",
            auto_record=False,
            extract_decisions=False,
            extract_lessons=True
        )

        summary = extractor.get_extraction_summary(results)

        assert isinstance(summary, str)
        assert "经验教训" in summary

    def test_get_extraction_summary_with_auto_recorded(self, extractor):
        """Test summary shows recorded items"""
        stage_output = """
        我们采用 TypeScript 作为主要开发语言，因为需要类型安全和更好的工具支持，这是一个架构级决策。
        """

        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_011",
            stage_id="design",
            auto_record=True  # Auto-record
        )

        summary = extractor.get_extraction_summary(results)

        # Should mention recorded items
        if results['summary']['recorded_count'] > 0:
            assert "已记录" in summary


# ==================== ExtractionResult Tests ====================

class TestExtractionResult:
    """Test ExtractionResult dataclass"""

    def test_extraction_result_creation(self):
        """Test creating an ExtractionResult"""
        result = ExtractionResult(
            extraction_type='decision',
            detected=True,
            confidence=0.85,
            text_snippet="Test snippet",
            detection_details={'has_wide_impact': True},
            metadata={'work_item_id': 'work_001'}
        )

        assert result.extraction_type == 'decision'
        assert result.detected is True
        assert result.confidence == 0.85
        assert result.text_snippet == "Test snippet"
        assert result.recorded_object is None

    def test_extraction_result_to_dict(self):
        """Test converting ExtractionResult to dict"""
        result = ExtractionResult(
            extraction_type='lesson',
            detected=True,
            confidence=0.9,
            text_snippet="Lesson snippet",
            detection_details={'has_problem': True, 'has_solution': True},
            metadata={'stage_id': 'implementation'}
        )

        result_dict = result.to_dict()

        assert result_dict['extraction_type'] == 'lesson'
        assert result_dict['detected'] is True
        assert result_dict['confidence'] == 0.9
        assert 'detection_details' in result_dict


# ==================== Integration Tests ====================

class TestMemoryExtractorIntegration:
    """Test MemoryExtractor integration with V4MemoryManager"""

    def test_complete_extraction_and_recording_workflow(self, extractor, memory_manager):
        """Test complete workflow from extraction to storage"""
        stage_output = """
        # Implementation Phase Completion

        经过仔细评估，我们决定使用 FastAPI 作为 Web 框架，因为需要高性能和自动文档生成能力。
        这个决策将影响整个 API 层的架构设计。

        在开发过程中，我们学到一个重要经验：API 设计应该优先考虑版本兼容性。
        遇到过一次因为破坏性变更导致客户端崩溃的问题。
        解决方法是使用 API 版本号（如 /v1/、/v2/）来管理不同版本。
        """

        # Extract with auto-record
        results = extractor.extract_from_stage_output(
            stage_output=stage_output,
            work_item_id="work_012",
            stage_id="implementation",
            auto_record=True
        )

        # Verify extraction
        assert results['summary']['total_decisions'] >= 1
        assert results['summary']['total_lessons'] >= 1
        assert results['summary']['recorded_count'] >= 2

        # Verify storage in V4MemoryManager
        decisions = memory_manager.list_decisions(work_item_id="work_012")
        lessons = memory_manager.list_lessons()

        assert len(decisions) >= 1
        assert len(lessons) >= 1

        # Verify v3.0 compatibility
        v3_memories = memory_manager.store.get_all()
        assert len(v3_memories) >= 2  # Both decision and lesson create v3.0 memories

    def test_extraction_without_recording_then_manual_confirm(self, extractor, memory_manager):
        """Test extraction without auto-record, then manual confirmation"""
        text = "我们选择 MongoDB 作为文档存储，因为需要灵活的 schema 和横向扩展能力，这是一个架构决策。"

        # Extract without recording
        result = extractor.extract_decision(
            text=text,
            work_item_id="work_013",
            stage_id="design",
            auto_record=False
        )

        assert result is not None
        assert result.recorded_object is None

        # Manual confirmation
        decision = extractor.confirm_and_record_decision(
            extraction_result=result,
            title="选择 MongoDB",
            decision="使用 MongoDB 作为文档存储",
            reason="需要灵活schema和横向扩展",
            scope=DecisionScope.ARCHITECTURE,
            alternatives=["CouchDB", "DynamoDB"],
            tech_stack=["MongoDB"],
            tags=["database", "nosql"]
        )

        # Verify stored
        retrieved = memory_manager.get_decision(decision.decision_id)
        assert retrieved is not None
        assert retrieved.title == "选择 MongoDB"
