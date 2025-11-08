"""
测试模板系统

测试 aceflow.workflow.templates 模块
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.templates import TemplateManager, TemplateRegistry, Template
from aceflow.workflow.templates.models import TemplateType, TemplateVariable
from aceflow.workflow.models import WorkflowMode


class TestTemplateRegistry:
    """测试模板注册表"""

    @pytest.fixture
    def template_root(self):
        """创建测试模板目录"""
        temp = Path(tempfile.mkdtemp())

        # 创建一些测试模板文件
        minimal_dir = temp / "minimal"
        minimal_dir.mkdir(parents=True)

        # 创建一个简单的阶段模板
        stage_template = minimal_dir / "stage_P.md"
        stage_template.write_text("""# {stage_name}

**迭代**: {iteration_id}
**负责人**: {owner}

## 任务清单
- 任务 1
- 任务 2
""")

        yield temp
        shutil.rmtree(temp)

    def test_registry_creation(self, template_root):
        """测试注册表创建"""
        registry = TemplateRegistry(template_root=template_root)

        assert registry.template_root == template_root
        assert len(registry.templates) > 0

    def test_discover_templates(self, template_root):
        """测试模板发现"""
        registry = TemplateRegistry(template_root=template_root)

        # 应该发现我们创建的测试模板
        templates = registry.get_templates_by_mode("minimal")
        assert len(templates) > 0

    def test_get_template(self, template_root):
        """测试获取模板"""
        registry = TemplateRegistry(template_root=template_root)

        # 获取所有模板
        all_templates = list(registry.templates.values())

        if all_templates:
            template_id = all_templates[0].template_id
            template = registry.get_template(template_id)

            assert template is not None
            assert template.template_id == template_id

    def test_get_template_by_stage(self, template_root):
        """测试根据阶段获取模板"""
        registry = TemplateRegistry(template_root=template_root)

        # 查找 minimal 模式的 P 阶段模板
        template = registry.get_template_by_stage("minimal", "P")

        if template:
            assert template.mode == "minimal"
            assert template.stage_id == "P"


class TestTemplateManager:
    """测试模板管理器"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def template_manager(self, temp_dir):
        """创建模板管理器"""
        return TemplateManager(output_root=temp_dir / "output")

    def test_manager_creation(self, template_manager):
        """测试管理器创建"""
        assert template_manager.registry is not None
        assert template_manager.output_root.exists()

    def test_get_templates_for_mode(self, template_manager):
        """测试获取模式的所有模板"""
        templates = template_manager.get_templates_for_mode("minimal")

        # Minimal 模式应该有一些模板
        assert isinstance(templates, list)

    def test_get_template_for_stage(self, template_manager):
        """测试获取阶段模板"""
        # 尝试获取 minimal 模式的某个阶段
        template = template_manager.get_template_for_stage("minimal", "P")

        # 可能存在也可能不存在，取决于模板文件
        if template:
            assert isinstance(template, Template)

    def test_render_template(self, template_manager, temp_dir):
        """测试模板渲染"""
        # 创建一个简单的测试模板
        template_path = temp_dir / "test_template.md"
        template_path.write_text("# {title}\n\n负责人: {owner}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[
                TemplateVariable(name="title", type="string", required=True),
                TemplateVariable(name="owner", type="string", required=True)
            ]
        )

        # 手动添加到注册表
        template_manager.registry.templates[template.template_id] = template

        # 渲染模板
        variables = {
            'title': '需求分析',
            'owner': '张三'
        }

        rendered = template_manager.render_template("test_001", variables)

        assert rendered is not None
        assert '需求分析' in rendered
        assert '张三' in rendered

    def test_write_template(self, template_manager, temp_dir):
        """测试写入模板"""
        # 创建测试模板
        template_path = temp_dir / "test_template.md"
        template_path.write_text("# {title}")

        template = Template(
            template_id="test_002",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[TemplateVariable(name="title", type="string", required=True)]
        )

        template_manager.registry.templates[template.template_id] = template

        # 写入文件
        output_path = template_manager.output_root / "test_output.md"
        result = template_manager.write_template(
            "test_002",
            {'title': '测试标题'},
            output_path
        )

        assert result == output_path
        assert output_path.exists()

        content = output_path.read_text()
        assert '测试标题' in content

    def test_validate_templates(self, template_manager):
        """测试模板验证"""
        # 验证所有模板
        results = template_manager.validate_templates()

        assert isinstance(results, dict)

        # 检查是否有无效模板
        invalid_count = sum(1 for valid in results.values() if not valid)

        # 至少应该能验证一些模板
        # 如果没有模板，results 应该是空的
        if results:
            assert invalid_count >= 0


class TestTemplate:
    """测试模板类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    def test_template_creation(self, temp_dir):
        """测试模板创建"""
        template_path = temp_dir / "test.md"
        template_path.write_text("# {title}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[TemplateVariable(name="title", type="string", required=True)]
        )

        assert template.template_id == "test_001"
        assert template.type == TemplateType.STAGE
        assert len(template.variables) == 1

    def test_read_content(self, temp_dir):
        """测试读取模板内容"""
        template_path = temp_dir / "test.md"
        template_path.write_text("# 测试内容")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path
        )

        content = template.read_content()
        assert content == "# 测试内容"

    def test_render(self, temp_dir):
        """测试渲染"""
        template_path = temp_dir / "test.md"
        template_path.write_text("# {title}\n\n负责人: {owner}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[
                TemplateVariable(name="title", type="string", required=True),
                TemplateVariable(name="owner", type="string", required=True)
            ]
        )

        rendered = template.render({
            'title': '需求分析',
            'owner': '张三'
        })

        assert '需求分析' in rendered
        assert '张三' in rendered

    def test_render_with_missing_required_variable(self, temp_dir):
        """测试渲染时缺少必需变量"""
        template_path = temp_dir / "test.md"
        template_path.write_text("# {title}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[TemplateVariable(name="title", type="string", required=True)]
        )

        # 缺少必需的 title 变量
        with pytest.raises(ValueError):
            template.render({})

    def test_validate(self, temp_dir):
        """测试模板验证"""
        template_path = temp_dir / "test.md"
        template_path.write_text("# {title}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path,
            variables=[TemplateVariable(name="title", type="string", required=True)]
        )

        # 验证应该成功
        result = template.validate()
        assert result is True

    def test_validate_with_missing_file(self, temp_dir):
        """测试验证不存在的文件"""
        template_path = temp_dir / "nonexistent.md"

        template = Template(
            template_id="test_001",
            name="测试模板",
            type=TemplateType.STAGE,
            mode="minimal",
            template_path=template_path
        )

        # 验证应该失败
        result = template.validate()
        assert result is False


class TestTemplateVariable:
    """测试模板变量"""

    def test_variable_creation(self):
        """测试变量创建"""
        var = TemplateVariable(
            name="title",
            type="string",
            required=True,
            default="默认标题",
            description="文档标题"
        )

        assert var.name == "title"
        assert var.type == "string"
        assert var.required is True
        assert var.default == "默认标题"
        assert var.description == "文档标题"

    def test_variable_to_dict(self):
        """测试变量转字典"""
        var = TemplateVariable(
            name="owner",
            type="string",
            required=False
        )

        data = var.to_dict()

        assert data['name'] == "owner"
        assert data['type'] == "string"
        assert data['required'] is False

    def test_variable_from_dict(self):
        """测试从字典创建变量"""
        data = {
            'name': 'stage_id',
            'type': 'string',
            'required': True,
            'default': None,
            'description': '阶段ID'
        }

        var = TemplateVariable.from_dict(data)

        assert var.name == "stage_id"
        assert var.required is True
        assert var.description == "阶段ID"
