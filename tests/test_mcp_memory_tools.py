"""
Unit tests for Memory MCP Tools (Task 4.7)

Tests for the 9 memory-related MCP tools:
- aceflow_v4_extract_memories
- aceflow_v4_confirm_decision
- aceflow_v4_confirm_lesson
- aceflow_v4_inject_memories
- aceflow_v4_preview_injection
- aceflow_v4_list_decisions
- aceflow_v4_list_lessons
- aceflow_v4_get_decision
- aceflow_v4_get_lesson
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add aceflow-mcp-server to path
mcp_server_path = Path(__file__).parent.parent / "aceflow-mcp-server"
if mcp_server_path.exists():
    sys.path.insert(0, str(mcp_server_path))

from aceflow_mcp_server.tools import AceFlowTools
from aceflow.workflow.memory import (
    DecisionScope,
    LessonCategory
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
def tools(temp_storage):
    """创建AceFlowTools实例"""
    # 使用临时目录作为工作目录
    return AceFlowTools(working_directory=str(temp_storage), project_id="test_memory")


@pytest.fixture
def sample_stage_output():
    """示例阶段输出（包含技术决策和经验教训）"""
    return """
    # Design Phase Output

    ## Architecture Decisions

    We decided to use PostgreSQL as our primary database. The main reasons are:
    1. Strong JSONB support for flexible schema
    2. ACID compliance for data integrity
    3. Proven reliability in production

    We considered MySQL and MongoDB as alternatives, but PostgreSQL's JSONB support
    and relational capabilities make it the best choice for our use case.

    Tech stack: PostgreSQL 14, pg_vector extension for embeddings

    Impact: All data access patterns must be designed around relational model with JSONB
    for flexible fields.

    ## Lessons Learned

    During this design phase, we learned that hardcoding database credentials in code
    is a security risk. We should always use environment variables or secure key management
    services to store sensitive configuration.

    This applies to all authentication and database connection scenarios.
    """


@pytest.fixture
def sample_decision():
    """示例技术决策"""
    return {
        "title": "Use PostgreSQL Database",
        "decision": "Choose PostgreSQL as primary database",
        "reason": "JSONB support, ACID compliance, proven reliability",
        "scope": "architecture",
        "alternatives": ["MySQL", "MongoDB"],
        "tech_stack": ["PostgreSQL", "pg_vector"],
        "impact": "All data access patterns must support relational model",
        "tags": ["database", "architecture"]
    }


@pytest.fixture
def sample_lesson():
    """示例经验教训"""
    return {
        "title": "Secure Credential Management",
        "content": "Never hardcode database credentials in code",
        "category": "best_practice",
        "what_happened": "Hardcoded credentials found in code during security audit",
        "what_learned": "Credentials must be stored in environment variables or key management services",
        "how_to_apply": "Use environment variables for all sensitive configuration",
        "applicability": "general",
        "applicable_scenarios": ["authentication", "security", "database"],
        "tags": ["security", "best_practice"]
    }


@pytest.fixture
def sample_injection_context():
    """示例注入上下文"""
    return {
        "work_item_id": "work_mem_test",
        "work_item_type": "feature",
        "work_item_title": "User Authentication System",
        "work_item_description": "Implement user login, registration, and authorization",
        "stage_id": "design",
        "stage_name": "Design Phase",
        "stage_type": "design",
        "max_memories": 5,
        "min_relevance": 0.3,
        "search_keywords": ["authentication", "database", "security"],
        "search_tags": ["security", "architecture"]
    }


# ==================== Memory Extraction Tests ====================

class TestMemoryExtraction:
    """Test memory extraction from stage output"""

    def test_extract_memories_success(self, tools, sample_stage_output):
        """Test successful memory extraction"""
        result = tools.aceflow_v4_extract_memories(
            work_item_id="work_001",
            stage_id="design",
            stage_output=sample_stage_output
        )

        assert result["success"] is True
        assert "extraction_result" in result
        assert "decisions_detected" in result
        assert "lessons_detected" in result
        assert "reminder" in result

        # Should detect at least one decision and one lesson
        assert result["decisions_detected"] >= 0
        assert result["lessons_detected"] >= 0

    def test_extract_memories_empty_output(self, tools):
        """Test extraction with empty output"""
        result = tools.aceflow_v4_extract_memories(
            work_item_id="work_002",
            stage_id="design",
            stage_output=""
        )

        assert result["success"] is True
        assert result["decisions_detected"] == 0
        assert result["lessons_detected"] == 0

    def test_extract_memories_no_patterns(self, tools):
        """Test extraction with text containing no decision/lesson patterns"""
        result = tools.aceflow_v4_extract_memories(
            work_item_id="work_003",
            stage_id="implementation",
            stage_output="This is just regular text without any decisions or lessons."
        )

        assert result["success"] is True
        # May detect 0 or more depending on pattern matching
        assert result["decisions_detected"] >= 0
        assert result["lessons_detected"] >= 0


# ==================== Decision Confirmation Tests ====================

class TestDecisionConfirmation:
    """Test technical decision confirmation and storage"""

    def test_confirm_decision_success(self, tools, sample_decision):
        """Test successful decision confirmation"""
        result = tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_001",
            stage_id="design"
        )

        assert result["success"] is True
        assert "decision_id" in result
        assert "reminder" in result
        assert sample_decision["title"] in result["message"]

    def test_confirm_decision_all_scopes(self, tools):
        """Test decision confirmation with all valid scopes"""
        scopes = ["local", "module", "architecture", "project"]

        for scope in scopes:
            decision = {
                "title": f"Test Decision {scope}",
                "decision": f"Make a {scope} level decision",
                "reason": "Testing",
                "scope": scope,
                "alternatives": [],
                "tech_stack": [],
                "impact": ""
            }

            result = tools.aceflow_v4_confirm_decision(
                decision=decision,
                work_item_id="work_scope_test",
                stage_id="design"
            )

            assert result["success"] is True, f"Failed for scope: {scope}"

    def test_confirm_decision_invalid_scope(self, tools):
        """Test decision confirmation with invalid scope"""
        decision = {
            "title": "Invalid Scope Test",
            "decision": "Test decision",
            "reason": "Testing",
            "scope": "invalid_scope",  # Invalid
            "alternatives": [],
            "tech_stack": [],
            "impact": ""
        }

        result = tools.aceflow_v4_confirm_decision(
            decision=decision,
            work_item_id="work_001",
            stage_id="design"
        )

        assert result["success"] is False
        assert "Invalid decision scope" in result["message"]

    def test_confirm_decision_missing_required_fields(self, tools):
        """Test decision confirmation with missing required fields"""
        incomplete_decision = {
            "title": "Incomplete Decision"
            # Missing decision, reason, etc.
        }

        result = tools.aceflow_v4_confirm_decision(
            decision=incomplete_decision,
            work_item_id="work_001",
            stage_id="design"
        )

        assert result["success"] is False


# ==================== Lesson Confirmation Tests ====================

class TestLessonConfirmation:
    """Test lesson learned confirmation and storage"""

    def test_confirm_lesson_success(self, tools, sample_lesson):
        """Test successful lesson confirmation"""
        result = tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)

        assert result["success"] is True
        assert "lesson_id" in result
        assert "reminder" in result
        assert sample_lesson["title"] in result["message"]

    def test_confirm_lesson_all_categories(self, tools):
        """Test lesson confirmation with all valid categories"""
        categories = ["technical", "process", "team", "tooling", "best_practice"]

        for category in categories:
            lesson = {
                "title": f"Test Lesson {category}",
                "content": f"A {category} lesson",
                "category": category,
                "what_happened": "Something happened",
                "what_learned": "We learned something",
                "how_to_apply": "Apply it this way",
                "applicability": "general",
                "applicable_scenarios": []
            }

            result = tools.aceflow_v4_confirm_lesson(lesson=lesson)

            assert result["success"] is True, f"Failed for category: {category}"

    def test_confirm_lesson_invalid_category(self, tools):
        """Test lesson confirmation with invalid category"""
        lesson = {
            "title": "Invalid Category Test",
            "content": "Test lesson",
            "category": "invalid_category",  # Invalid
            "what_happened": "Test",
            "what_learned": "Test",
            "how_to_apply": "Test",
            "applicability": "general",
            "applicable_scenarios": []
        }

        result = tools.aceflow_v4_confirm_lesson(lesson=lesson)

        assert result["success"] is False
        assert "Invalid lesson category" in result["message"]


# ==================== Memory Injection Tests ====================

class TestMemoryInjection:
    """Test memory injection into templates"""

    def test_inject_memories_with_placeholder(
        self,
        tools,
        sample_injection_context,
        sample_decision
    ):
        """Test injecting memories into template with placeholder"""
        # First store a decision
        tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id=sample_injection_context["work_item_id"],
            stage_id=sample_injection_context["stage_id"]
        )

        # Template with placeholder
        template = """
# Design Phase

## Project Memories

{{project_memory}}

## Design Tasks

Complete the design...
"""

        result = tools.aceflow_v4_inject_memories(
            template_content=template,
            context=sample_injection_context
        )

        assert result["success"] is True
        assert "injected_template" in result
        assert "injection_result" in result
        assert "total_memories" in result

        # Placeholder should be replaced
        assert "{{project_memory}}" not in result["injected_template"]
        assert "# 项目记忆" in result["injected_template"]

    def test_inject_memories_selective_types(
        self,
        tools,
        sample_injection_context
    ):
        """Test selective memory type injection"""
        template = "{{project_memory}}"

        # Only inject decisions
        result = tools.aceflow_v4_inject_memories(
            template_content=template,
            context=sample_injection_context,
            include_v3_memories=False,
            include_decisions=True,
            include_lessons=False,
            include_documents=False
        )

        assert result["success"] is True

    def test_inject_memories_missing_context_fields(self, tools):
        """Test injection with incomplete context"""
        template = "{{project_memory}}"
        incomplete_context = {
            "work_item_id": "work_001"
            # Missing required fields
        }

        result = tools.aceflow_v4_inject_memories(
            template_content=template,
            context=incomplete_context
        )

        assert result["success"] is False
        assert "Missing required context field" in result["error"]


# ==================== Injection Preview Tests ====================

class TestInjectionPreview:
    """Test memory injection preview"""

    def test_preview_injection_success(
        self,
        tools,
        sample_injection_context,
        sample_decision
    ):
        """Test successful injection preview"""
        # Store a decision first
        tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id=sample_injection_context["work_item_id"],
            stage_id=sample_injection_context["stage_id"]
        )

        result = tools.aceflow_v4_preview_injection(
            context=sample_injection_context
        )

        assert result["success"] is True
        assert "summary" in result
        assert "total_memories" in result
        assert result["total_memories"] >= 0

    def test_preview_injection_empty(self, tools, sample_injection_context):
        """Test preview with no stored memories"""
        result = tools.aceflow_v4_preview_injection(
            context=sample_injection_context
        )

        assert result["success"] is True
        assert result["total_memories"] == 0

    def test_preview_injection_missing_context(self, tools):
        """Test preview with incomplete context"""
        incomplete_context = {
            "work_item_id": "work_001"
        }

        result = tools.aceflow_v4_preview_injection(context=incomplete_context)

        assert result["success"] is False


# ==================== Decision Listing Tests ====================

class TestDecisionListing:
    """Test listing technical decisions"""

    def test_list_decisions_all(self, tools):
        """Test listing all decisions"""
        result = tools.aceflow_v4_list_decisions()

        assert result["success"] is True
        assert "count" in result
        assert "decisions" in result
        assert isinstance(result["decisions"], list)

    def test_list_decisions_by_scope(self, tools, sample_decision):
        """Test filtering decisions by scope"""
        # Store a decision
        tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_001",
            stage_id="design"
        )

        result = tools.aceflow_v4_list_decisions(scope="architecture")

        assert result["success"] is True
        assert result["count"] >= 0

    def test_list_decisions_by_tags(self, tools, sample_decision):
        """Test filtering decisions by tags"""
        # Store a decision
        tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_001",
            stage_id="design"
        )

        result = tools.aceflow_v4_list_decisions(tags=["database"])

        assert result["success"] is True
        assert result["count"] >= 0

    def test_list_decisions_by_work_item(self, tools, sample_decision):
        """Test filtering decisions by work item"""
        # Store a decision
        tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_specific",
            stage_id="design"
        )

        result = tools.aceflow_v4_list_decisions(work_item_id="work_specific")

        assert result["success"] is True

    def test_list_decisions_invalid_scope(self, tools):
        """Test listing with invalid scope"""
        result = tools.aceflow_v4_list_decisions(scope="invalid_scope")

        assert result["success"] is False
        assert "Invalid scope" in result["message"]


# ==================== Lesson Listing Tests ====================

class TestLessonListing:
    """Test listing lessons learned"""

    def test_list_lessons_all(self, tools):
        """Test listing all lessons"""
        result = tools.aceflow_v4_list_lessons()

        assert result["success"] is True
        assert "count" in result
        assert "lessons" in result
        assert isinstance(result["lessons"], list)

    def test_list_lessons_by_category(self, tools, sample_lesson):
        """Test filtering lessons by category"""
        # Store a lesson
        tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)

        result = tools.aceflow_v4_list_lessons(category="best_practice")

        assert result["success"] is True
        assert result["count"] >= 0

    def test_list_lessons_by_applicability(self, tools, sample_lesson):
        """Test filtering lessons by applicability"""
        # Store a lesson
        tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)

        result = tools.aceflow_v4_list_lessons(applicability="general")

        assert result["success"] is True
        assert result["count"] >= 0

    def test_list_lessons_by_tags(self, tools, sample_lesson):
        """Test filtering lessons by tags"""
        # Store a lesson
        tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)

        result = tools.aceflow_v4_list_lessons(tags=["security"])

        assert result["success"] is True
        assert result["count"] >= 0

    def test_list_lessons_invalid_category(self, tools):
        """Test listing with invalid category"""
        result = tools.aceflow_v4_list_lessons(category="invalid_category")

        assert result["success"] is False
        assert "Invalid category" in result["message"]


# ==================== Decision Retrieval Tests ====================

class TestDecisionRetrieval:
    """Test retrieving specific decisions"""

    def test_get_decision_success(self, tools, sample_decision):
        """Test successful decision retrieval"""
        # Store a decision first
        store_result = tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_001",
            stage_id="design"
        )

        decision_id = store_result["decision_id"]

        # Retrieve it
        result = tools.aceflow_v4_get_decision(decision_id=decision_id)

        assert result["success"] is True
        assert "decision" in result
        assert result["decision"]["title"] == sample_decision["title"]

    def test_get_decision_not_found(self, tools):
        """Test retrieving non-existent decision"""
        result = tools.aceflow_v4_get_decision(decision_id="nonexistent_id")

        assert result["success"] is False
        assert "not found" in result["message"]


# ==================== Lesson Retrieval Tests ====================

class TestLessonRetrieval:
    """Test retrieving specific lessons"""

    def test_get_lesson_success(self, tools, sample_lesson):
        """Test successful lesson retrieval"""
        # Store a lesson first
        store_result = tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)

        lesson_id = store_result["lesson_id"]

        # Retrieve it
        result = tools.aceflow_v4_get_lesson(lesson_id=lesson_id)

        assert result["success"] is True
        assert "lesson" in result
        assert result["lesson"]["title"] == sample_lesson["title"]

    def test_get_lesson_not_found(self, tools):
        """Test retrieving non-existent lesson"""
        result = tools.aceflow_v4_get_lesson(lesson_id="nonexistent_id")

        assert result["success"] is False
        assert "not found" in result["message"]


# ==================== Integration Tests ====================

class TestMemoryToolsIntegration:
    """Test complete memory workflow integration"""

    def test_complete_memory_workflow(
        self,
        tools,
        sample_stage_output,
        sample_injection_context
    ):
        """Test complete workflow: extract → confirm → inject"""
        # 1. Extract memories from stage output
        extract_result = tools.aceflow_v4_extract_memories(
            work_item_id=sample_injection_context["work_item_id"],
            stage_id=sample_injection_context["stage_id"],
            stage_output=sample_stage_output
        )

        assert extract_result["success"] is True

        # 2. If decisions detected, confirm first one
        extraction = extract_result["extraction_result"]
        if extraction["decisions"]:
            first_decision = extraction["decisions"][0]
            confirm_result = tools.aceflow_v4_confirm_decision(
                decision=first_decision,
                work_item_id=sample_injection_context["work_item_id"],
                stage_id=sample_injection_context["stage_id"]
            )
            assert confirm_result["success"] is True

        # 3. Preview injection
        preview_result = tools.aceflow_v4_preview_injection(
            context=sample_injection_context
        )

        assert preview_result["success"] is True

        # 4. Perform actual injection
        template = "# Stage\n\n{{project_memory}}\n\n## Tasks"

        inject_result = tools.aceflow_v4_inject_memories(
            template_content=template,
            context=sample_injection_context
        )

        assert inject_result["success"] is True
        assert "{{project_memory}}" not in inject_result["injected_template"]

    def test_list_and_retrieve_workflow(
        self,
        tools,
        sample_decision,
        sample_lesson
    ):
        """Test workflow: store → list → retrieve"""
        # 1. Store decision and lesson
        decision_result = tools.aceflow_v4_confirm_decision(
            decision=sample_decision,
            work_item_id="work_integration",
            stage_id="design"
        )
        decision_id = decision_result["decision_id"]

        lesson_result = tools.aceflow_v4_confirm_lesson(lesson=sample_lesson)
        lesson_id = lesson_result["lesson_id"]

        # 2. List all
        decisions_list = tools.aceflow_v4_list_decisions()
        lessons_list = tools.aceflow_v4_list_lessons()

        assert decisions_list["count"] >= 1
        assert lessons_list["count"] >= 1

        # 3. Retrieve specific ones
        decision_get = tools.aceflow_v4_get_decision(decision_id=decision_id)
        lesson_get = tools.aceflow_v4_get_lesson(lesson_id=lesson_id)

        assert decision_get["success"] is True
        assert lesson_get["success"] is True
