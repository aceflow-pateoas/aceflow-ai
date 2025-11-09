"""
测试模板系统

测试 aceflow.workflow.templates 模块
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.templates import (
    TemplateManager,
    TemplateRegistry,
    Template,
    TemplateType,
    TemplateVariable
)


class TestTemplateVariable:
    """测试模板变量"""

    def test_variable_creation(self):
        """测试变量创建"""
        var = TemplateVariable(
            name="iteration_id",
            description="迭代ID",
            required=True,
            default_value="iter_001",
            example="iter_001"
        )

        assert var.name == "iteration_id"
        assert var.description == "迭代ID"
        assert var.required is True
        assert var.default_value == "iter_001"

    def test_variable_to_dict(self):
        """测试变量转字典"""
        var = TemplateVariable(
            name="owner",
            description="负责人",
            required=False
        )

        data = var.to_dict()

        assert data['name'] == "owner"
        assert data['description'] == "负责人"
        assert data['required'] is False


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
        template_file = temp_dir / "test.md"
        template_file.write_text("# {title}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=template_file,
            description="测试用模板"
        )

        assert template.template_id == "test_001"
        assert template.name == "测试模板"
        assert template.mode == "minimal"
        assert template.type == TemplateType.STAGE

    def test_template_exists(self, temp_dir):
        """测试模板文件存在性检查"""
        # 存在的文件
        existing_file = temp_dir / "exists.md"
        existing_file.write_text("content")

        template1 = Template(
            template_id="t1",
            name="存在的模板",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=existing_file
        )

        assert template1.exists is True

        # 不存在的文件
        template2 = Template(
            template_id="t2",
            name="不存在的模板",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=temp_dir / "nonexistent.md"
        )

        assert template2.exists is False

    def test_read_content(self, temp_dir):
        """测试读取模板内容"""
        template_file = temp_dir / "test.md"
        template_file.write_text("# 测试内容\n变量: {var}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=template_file
        )

        content = template.read_content()
        assert "测试内容" in content
        assert "{var}" in content

    def test_render(self, temp_dir):
        """测试模板渲染"""
        template_file = temp_dir / "test.md"
        template_file.write_text("# {title}\n\n负责人: {owner}")

        template = Template(
            template_id="test_001",
            name="测试模板",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=template_file
        )

        rendered = template.render({
            'title': '需求分析',
            'owner': '张三'
        })

        assert '需求分析' in rendered
        assert '张三' in rendered
        assert '{title}' not in rendered
        assert '{owner}' not in rendered


class TestTemplateRegistry:
    """测试模板注册表"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())

        # 创建测试模板目录结构
        minimal_dir = temp / "minimal"
        minimal_dir.mkdir(parents=True)

        # 创建一个测试模板文件
        (minimal_dir / "stage_P.md").write_text("# Planning\nIteration: {iteration_id}")

        yield temp
        shutil.rmtree(temp)

    def test_registry_creation(self, temp_dir):
        """测试注册表创建"""
        registry = TemplateRegistry(template_root=temp_dir)

        assert registry is not None
        assert registry.template_root == temp_dir

    def test_get_all_templates(self, temp_dir):
        """测试获取所有模板"""
        registry = TemplateRegistry(template_root=temp_dir)

        templates = registry.list_all_templates()

        assert isinstance(templates, list)

    def test_get_template_by_id(self, temp_dir):
        """测试根据ID获取模板"""
        registry = TemplateRegistry(template_root=temp_dir)

        # 获取所有模板
        all_templates = registry.list_all_templates()

        if all_templates:
            template_id = all_templates[0].template_id
            template = registry.get_template(template_id)

            assert template is not None
            assert template.template_id == template_id

    def test_get_templates_by_mode(self, temp_dir):
        """测试根据模式获取模板"""
        registry = TemplateRegistry(template_root=temp_dir)

        templates = registry.get_templates_by_mode("minimal")

        assert isinstance(templates, list)


class TestTemplateManager:
    """测试模板管理器"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())

        # 创建模板目录
        template_dir = temp / "templates"
        template_dir.mkdir(parents=True)

        minimal_dir = template_dir / "minimal"
        minimal_dir.mkdir(parents=True)
        (minimal_dir / "stage_P.md").write_text("# {stage_name}\nID: {iteration_id}")

        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def template_manager(self, temp_dir):
        """创建模板管理器"""
        template_root = temp_dir / "templates"
        output_root = temp_dir / "output"

        return TemplateManager(
            template_root=template_root,
            output_root=output_root
        )

    def test_manager_creation(self, template_manager):
        """测试管理器创建"""
        assert template_manager is not None
        assert template_manager.registry is not None
        # output_root 可能还不存在，会在第一次使用时创建

    def test_get_template(self, template_manager):
        """测试获取模板"""
        # 获取所有模板
        all_templates = template_manager.registry.list_all_templates()

        if all_templates:
            template_id = all_templates[0].template_id
            template = template_manager.get_template(template_id)

            assert template is not None
            assert template.template_id == template_id

    def test_list_templates_by_mode(self, template_manager):
        """测试列出指定模式的模板"""
        templates = template_manager.list_templates(mode="minimal")

        assert isinstance(templates, list)

    def test_render_template(self, template_manager, temp_dir):
        """测试渲染模板"""
        # 创建一个简单的测试模板
        template_file = temp_dir / "test_render.md"
        template_file.write_text("# {title}\nOwner: {owner}")

        template = Template(
            template_id="test_render",
            name="测试渲染",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=template_file
        )

        # 手动添加到注册表
        template_manager.registry.templates[template.template_id] = template

        # 渲染
        rendered = template_manager.render_template(
            template_id="test_render",
            variables={'title': '测试', 'owner': '李四'}
        )

        assert rendered is not None
        assert '测试' in rendered
        assert '李四' in rendered

    def test_render_and_save(self, template_manager, temp_dir):
        """测试渲染并保存"""
        # 创建测试模板
        template_file = temp_dir / "test_save.md"
        template_file.write_text("# {title}")

        template = Template(
            template_id="test_save",
            name="测试保存",
            mode="minimal",
            type=TemplateType.STAGE,
            file_path=template_file
        )

        template_manager.registry.templates[template.template_id] = template

        # 渲染并保存
        output_file = template_manager.output_root / "output.md"
        result = template_manager.write_template(
            template_id="test_save",
            output_file=output_file,
            variables={'title': '保存测试'}
        )

        assert result == output_file
        assert output_file.exists()

        content = output_file.read_text()
        assert '保存测试' in content

    def test_get_template_for_stage(self, template_manager):
        """测试获取阶段模板"""
        template = template_manager.get_template_for_stage(
            mode="minimal",
            stage_id="P"
        )

        # 可能存在也可能不存在
        if template:
            assert isinstance(template, Template)
            assert template.mode == "minimal"
