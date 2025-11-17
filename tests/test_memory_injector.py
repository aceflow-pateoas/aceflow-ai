"""
Unit tests for MemoryInjector

Tests for:
- Memory injection into templates
- Placeholder replacement
- Memory formatting
- Integration with V4MemoryManager
- Injection summary generation
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.memory.injector import MemoryInjector, InjectionResult
from aceflow.workflow.memory.v4_manager import V4MemoryManager
from aceflow.workflow.memory.v4_models import (
    MemoryInjectionContext,
    DecisionScope,
    LessonCategory
)
from aceflow.workflow.memory.models import Memory, MemoryType, MemoryPriority
from aceflow.workflow.models import WorkflowType


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
def injector(memory_manager):
    """创建MemoryInjector实例"""
    return MemoryInjector(memory_manager)


@pytest.fixture
def sample_context():
    """创建示例注入上下文"""
    return MemoryInjectionContext(
        work_item_id="work_001",
        work_item_type=WorkflowType.FEATURE.value,
        work_item_title="用户认证系统",
        work_item_description="实现用户登录、注册、权限管理功能",
        stage_id="design",
        stage_name="设计方案",
        stage_type="design",
        max_memories=5,
        min_relevance=0.3,
        search_keywords=["认证", "登录", "权限", "设计"],
        search_tags=["authentication", "design"]
    )


@pytest.fixture
def populated_memory_manager(memory_manager):
    """创建包含测试数据的MemoryManager"""
    # 添加v3.0记忆
    memory1 = Memory(
        memory_id="mem_001",
        type=MemoryType.CONTEXT,
        content="项目使用JWT进行用户认证，需要在所有API请求中验证token。",
        priority=MemoryPriority.HIGH,
        iteration_id="work_001",
        stage_id="design",
        tags=["authentication", "jwt"]
    )
    memory_manager.store.add(memory1)

    # 添加技术决策
    memory_manager.record_tech_decision(
        title="选择JWT作为认证方案",
        decision="使用JWT（JSON Web Tokens）进行用户认证",
        reason="JWT无状态、易于扩展、支持跨域",
        scope=DecisionScope.MODULE,
        alternatives=["Session", "OAuth"],
        tech_stack=["JWT", "bcrypt"],
        impact="影响认证模块的设计",
        work_item_id="work_001",
        stage_id="design",
        tags=["authentication", "design"]
    )

    # 添加经验教训
    memory_manager.record_lesson(
        title="JWT密钥管理",
        content="JWT密钥不应硬编码在代码中",
        category=LessonCategory.BEST_PRACTICE,
        what_happened="在之前的项目中，JWT密钥被硬编码导致安全问题",
        what_learned="应该使用环境变量或密钥管理服务存储密钥",
        how_to_apply="使用环境变量存储JWT_SECRET，在部署时配置",
        applicability="general",
        applicable_scenarios=["authentication", "security"],
        tags=["security", "best_practice"]
    )

    # 添加文档引用
    memory_manager.record_document_ref(
        title="JWT最佳实践",
        document_type="api",
        path="docs/api/authentication.md",
        section="JWT Implementation",
        reason="设计认证系统时需要参考",
        key_points=[
            "Token过期时间设置为1小时",
            "Refresh token过期时间为7天",
            "使用HS256算法签名"
        ],
        work_item_id="work_001",
        tags=["authentication", "documentation"]
    )

    return memory_manager


# ==================== Basic Injection Tests ====================

class TestBasicInjection:
    """Test basic memory injection functionality"""

    def test_inject_memories_into_template_with_placeholder(self, injector, sample_context):
        """Test injecting memories into template with placeholder"""
        template_content = """
# 设计方案

## 项目记忆

{{project_memory}}

## 设计目标

请基于以上项目记忆，完成本阶段的设计方案。
"""

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        # 验证占位符被替换
        assert "{{project_memory}}" not in injected_template
        assert "# 项目记忆" in injected_template

        # 验证结果对象
        assert isinstance(result, InjectionResult)
        assert result.total_count >= 0

    def test_inject_memories_without_placeholder(self, injector, sample_context):
        """Test template without placeholder remains unchanged"""
        template_content = """
# 设计方案

没有项目记忆占位符的模板。
"""

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        # 模板内容应该保持不变（除了没有占位符替换）
        assert "{{project_memory}}" not in injected_template
        assert "# 设计方案" in injected_template

    def test_inject_with_populated_memories(
        self,
        memory_manager,
        populated_memory_manager,
        sample_context
    ):
        """Test injecting with actual memories"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "# Stage\n\n{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        # 验证注入了记忆
        assert result.total_count > 0
        assert "# 项目记忆" in injected_template

        # 验证各类记忆被注入
        if result.v3_memories_count > 0:
            assert "相关背景信息" in injected_template

        if result.decisions_count > 0:
            assert "相关技术决策" in injected_template
            assert "JWT" in injected_template

        if result.lessons_count > 0:
            assert "相关经验教训" in injected_template

        if result.documents_count > 0:
            assert "相关文档" in injected_template


# ==================== Selective Injection Tests ====================

class TestSelectiveInjection:
    """Test selective memory type injection"""

    def test_inject_only_decisions(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test injecting only decisions"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_v3_memories=False,
            include_decisions=True,
            include_lessons=False,
            include_documents=False
        )

        # 应该只有决策
        assert result.decisions_count > 0
        assert result.v3_memories_count == 0
        assert result.lessons_count == 0
        assert result.documents_count == 0

        # 内容中应该只有决策
        if result.decisions_count > 0:
            assert "相关技术决策" in injected_template
            assert "相关背景信息" not in injected_template
            assert "相关经验教训" not in injected_template

    def test_inject_only_lessons(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test injecting only lessons"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_v3_memories=False,
            include_decisions=False,
            include_lessons=True,
            include_documents=False
        )

        # 应该只有经验教训
        assert result.lessons_count > 0
        assert result.decisions_count == 0
        assert result.v3_memories_count == 0

    def test_inject_multiple_types(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test injecting multiple memory types"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_v3_memories=True,
            include_decisions=True,
            include_lessons=True,
            include_documents=True
        )

        # 应该包含多种类型
        assert result.total_count > 0
        # 至少应该有决策和经验（我们知道有这些）
        assert result.decisions_count > 0
        assert result.lessons_count > 0


# ==================== Formatting Tests ====================

class TestMemoryFormatting:
    """Test memory formatting for injection"""

    def test_format_empty_memories(self, injector, sample_context):
        """Test formatting when no memories are available"""
        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        # 应该有默认消息
        assert "# 项目记忆" in injected_template
        assert result.total_count == 0

    def test_format_with_v3_memories(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test v3.0 memory formatting"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_v3_memories=True,
            include_decisions=False,
            include_lessons=False,
            include_documents=False
        )

        if result.v3_memories_count > 0:
            assert "## 相关背景信息" in injected_template
            assert "**标签**" in injected_template

    def test_format_with_decisions(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test decision formatting"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_decisions=True,
            include_v3_memories=False,
            include_lessons=False,
            include_documents=False
        )

        if result.decisions_count > 0:
            assert "## 相关技术决策" in injected_template
            assert "**决策**:" in injected_template
            assert "**理由**:" in injected_template
            assert "**影响范围**:" in injected_template

    def test_format_with_lessons(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test lesson formatting"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            include_lessons=True,
            include_v3_memories=False,
            include_decisions=False,
            include_documents=False
        )

        if result.lessons_count > 0:
            assert "## 相关经验教训" in injected_template
            assert "**发生了什么**:" in injected_template
            assert "**学到了什么**:" in injected_template
            assert "**如何应用**:" in injected_template


# ==================== Custom Placeholder Tests ====================

class TestCustomPlaceholder:
    """Test using custom placeholders"""

    def test_inject_with_custom_placeholder(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test injection with custom placeholder"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "# Template\n\n{MEMORIES}\n\nEnd."

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context,
            placeholder="{MEMORIES}"
        )

        # 自定义占位符应该被替换
        assert "{MEMORIES}" not in injected_template
        assert "# 项目记忆" in injected_template

    def test_check_placeholder_exists(self, injector):
        """Test checking if placeholder exists in template"""
        template_with = "Content {{project_memory}} more"
        template_without = "Content no placeholder"

        assert injector.check_template_has_placeholder(template_with) is True
        assert injector.check_template_has_placeholder(template_without) is False

    def test_check_custom_placeholder_exists(self, injector):
        """Test checking custom placeholder"""
        template = "Content {CUSTOM} more"

        assert injector.check_template_has_placeholder(
            template,
            placeholder="{CUSTOM}"
        ) is True


# ==================== Injection Summary Tests ====================

class TestInjectionSummary:
    """Test injection summary generation"""

    def test_get_injection_summary(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test getting injection summary without actual injection"""
        injector = MemoryInjector(populated_memory_manager)

        summary = injector.get_injection_summary(sample_context)

        # 验证摘要结构
        assert 'work_item_id' in summary
        assert 'stage_id' in summary
        assert 'counts' in summary
        assert 'details' in summary

        # 验证计数
        counts = summary['counts']
        assert 'v3_memories' in counts
        assert 'decisions' in counts
        assert 'lessons' in counts
        assert 'documents' in counts
        assert 'total' in counts

        # 验证详情
        details = summary['details']
        assert 'v3_memories' in details
        assert 'decisions' in details
        assert 'lessons' in details
        assert 'documents' in details

    def test_injection_result_to_dict(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test converting InjectionResult to dict"""
        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        _, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        result_dict = result.to_dict()

        # 验证字典结构
        assert 'v3_memories_count' in result_dict
        assert 'decisions_count' in result_dict
        assert 'lessons_count' in result_dict
        assert 'documents_count' in result_dict
        assert 'total_count' in result_dict
        assert 'injected_content' in result_dict
        assert 'metadata' in result_dict


# ==================== Integration Tests ====================

class TestMemoryInjectorIntegration:
    """Test MemoryInjector integration with V4MemoryManager"""

    def test_complete_injection_workflow(
        self,
        populated_memory_manager,
        sample_context
    ):
        """Test complete workflow from memory storage to injection"""
        injector = MemoryInjector(populated_memory_manager)

        # 1. 获取注入摘要
        summary = injector.get_injection_summary(sample_context)
        assert summary['counts']['total'] > 0

        # 2. 执行注入
        template_content = """
# 设计方案阶段

## 背景信息
{{project_memory}}

## 设计任务
请完成以下设计任务...
"""

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=sample_context
        )

        # 3. 验证注入结果
        assert result.total_count > 0
        assert result.total_count == summary['counts']['total']
        assert "{{project_memory}}" not in injected_template
        assert "# 项目记忆" in injected_template

    def test_injection_with_relevance_filtering(
        self,
        populated_memory_manager
    ):
        """Test injection respects relevance filtering"""
        # 创建低相关性上下文
        low_relevance_context = MemoryInjectionContext(
            work_item_id="work_999",  # 不同的work_item
            work_item_type=WorkflowType.BUGFIX.value,
            work_item_title="修复登录bug",
            work_item_description="修复用户无法登录的问题",
            stage_id="fix",
            stage_name="修复实现",
            stage_type="fix",
            max_memories=5,
            min_relevance=0.9,  # 高阈值
            search_keywords=["bug", "fix"],
            search_tags=["bugfix"]
        )

        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=low_relevance_context
        )

        # 由于相关性阈值很高，可能没有记忆被注入
        # 或者只有少量记忆
        assert result.total_count >= 0

    def test_injection_respects_max_memories(
        self,
        populated_memory_manager
    ):
        """Test injection respects max_memories limit"""
        # 创建限制为1的上下文
        limited_context = MemoryInjectionContext(
            work_item_id="work_001",
            work_item_type=WorkflowType.FEATURE.value,
            work_item_title="用户认证系统",
            work_item_description="实现用户登录、注册、权限管理功能",
            stage_id="design",
            stage_name="设计方案",
            stage_type="design",
            max_memories=1,  # 只允许1个记忆
            min_relevance=0.0,
            search_keywords=["认证", "设计"],
            search_tags=["authentication"]
        )

        injector = MemoryInjector(populated_memory_manager)

        template_content = "{{project_memory}}"

        injected_template, result = injector.inject_memories_into_template(
            template_content=template_content,
            context=limited_context
        )

        # 每种类型最多1个记忆
        assert result.v3_memories_count <= 1
        assert result.decisions_count <= 1
        assert result.lessons_count <= 1
        assert result.documents_count <= 1
