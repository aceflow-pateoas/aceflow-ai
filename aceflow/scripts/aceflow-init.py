#!/usr/bin/env python3
"""
AceFlow v3.0 项目初始化脚本 (Python版本)
AI Agent 增强层初始化工具

提供跨平台的项目初始化功能，支持多种流程模式。
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import tempfile

# 脚本信息
SCRIPT_NAME = "aceflow-init.py"
VERSION = "3.0.0"
ACEFLOW_HOME = os.environ.get('ACEFLOW_HOME', 
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 颜色定义 (ANSI色彩代码)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class Logger:
    """日志工具类"""
    
    @staticmethod
    def info(message: str):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
    
    @staticmethod
    def success(message: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    @staticmethod
    def header():
        print(f"""{Colors.PURPLE}
╔══════════════════════════════════════╗
║         AceFlow v3.0 初始化          ║
║       AI Agent 增强层配置工具        ║
╚══════════════════════════════════════╝{Colors.NC}""")

class AceFlowInit:
    """AceFlow 初始化类"""
    
    def __init__(self):
        self.logger = Logger()
        
    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
AceFlow v3.0 项目初始化脚本 (Python版本)

用法: {SCRIPT_NAME} [选项]

选项:
  -m, --mode MODE       指定流程模式 (minimal|standard|complete|smart)
  -p, --project NAME    指定项目名称
  -d, --directory DIR   指定项目目录 (默认: 当前目录)
  -i, --interactive     启用交互式配置
  -f, --force          强制覆盖已存在的配置
  -h, --help           显示此帮助信息
  -v, --version        显示版本信息

模式说明:
  minimal   - 最简流程，适合快速原型和小型项目
  standard  - 标准流程，适合中等规模团队项目  
  complete  - 完整流程，适合企业级大型项目
  smart     - 智能流程，AI驱动的自适应模式

示例:
  {SCRIPT_NAME} --mode=smart --interactive
  {SCRIPT_NAME} -m standard -p "我的项目" -d ./my-project
  {SCRIPT_NAME} --force --mode=complete
"""
        print(help_text)

    def check_dependencies(self) -> bool:
        """检查环境依赖"""
        self.logger.info("检查环境依赖...")
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            self.logger.error("需要Python 3.7或更高版本")
            return False
        
        # 检查AceFlow Python包
        try:
            import aceflow
            self.logger.info("发现AceFlow Python包")
        except ImportError:
            self.logger.warning("AceFlow Python包未安装，将使用本地版本")
        
        # 检查Git
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, check=True)
            self.logger.info("发现Git")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("Git未安装，某些功能可能受限")
        
        self.logger.success("环境检查完成")
        return True

    def detect_ai_agent(self) -> bool:
        """检测AI Agent环境"""
        self.logger.info("检测AI Agent环境...")
        
        detected_agents = []
        
        # 检测Cline
        if shutil.which('cline') or Path('.cline_project').exists():
            detected_agents.append("Cline")
        
        # 检测Cursor
        if shutil.which('cursor') or Path('.cursor').exists():
            detected_agents.append("Cursor")
        
        # 检测Claude Code
        if shutil.which('claude') or os.environ.get('CLAUDE_CODE_API_KEY'):
            detected_agents.append("Claude Code")
        
        if not detected_agents:
            self.logger.warning("未检测到支持的AI Agent环境")
            self.logger.info("AceFlow支持: Cline, Cursor, Claude Code")
            return False
        else:
            self.logger.success(f"检测到AI Agent: {', '.join(detected_agents)}")
            return True

    def ai_interview(self) -> str:
        """AI智能访谈 (Smart模式专用)"""
        project_data_file = "aceflow_result/project_analysis.json"
        
        self.logger.header()
        print(f"{Colors.CYAN}🧠 AI智能项目分析访谈{Colors.NC}")
        print("AceFlow将通过几个问题了解您的项目，以提供最适合的配置建议。")
        print("")
        
        # 收集用户回答
        questions = {
            '项目性质和目标': "请简要描述您的项目性质、主要目标和预期成果：",
            '团队背景': "请描述团队规模、成员经验水平和技术背景：\n例如: 5人团队，2年经验，主要使用Python/React技术栈",
            '约束条件': "主要约束条件有哪些？(时间、预算、技术限制、合规要求等)",
            '成功标准': "什么情况下您认为这个项目是成功的？关键指标是什么？",
            '风险关注': "您最担心的风险点是什么？技术风险、进度风险还是质量风险？"
        }
        
        answers = {}
        for key, question in questions.items():
            print(f"{Colors.YELLOW}📋 问题: {key}{Colors.NC}")
            print(question)
            answer = input("> ")
            answers[key] = answer
            print("")
        
        # AI分析 (简化的评分算法)
        self.logger.info("AI正在分析您的回答...")
        
        complexity_score = 0
        text_to_analyze = " ".join(answers.values()).lower()
        
        # 基于关键词的简单评分算法
        if any(keyword in text_to_analyze for keyword in ['大型', '企业级', '复杂', '银行', '金融', '医疗']):
            complexity_score += 30
        
        if any(keyword in text_to_analyze for keyword in ['1人', '2人', '个人', '新手']):
            complexity_score += 10
        elif any(keyword in text_to_analyze for keyword in ['5人', '6人', '7人', '8人', '9人', '经验丰富']):
            complexity_score += 20
        elif any(keyword in text_to_analyze for keyword in ['10人以上', '大团队']):
            complexity_score += 30
        
        if any(keyword in text_to_analyze for keyword in ['合规', '监管', '严格']):
            complexity_score += 25
        
        if any(keyword in text_to_analyze for keyword in ['紧急', '快速', '原型']):
            complexity_score -= 15
        
        # 推荐模式
        if complexity_score <= 30:
            recommended_mode = "minimal"
        elif complexity_score <= 70:
            recommended_mode = "standard"
        else:
            recommended_mode = "complete"
        
        # 保存分析结果
        os.makedirs("aceflow_result", exist_ok=True)
        analysis_data = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "answers": answers,
            "complexity_score": complexity_score,
            "recommended_mode": recommended_mode,
            "ai_insights": {
                "primary_risks": ["基于输入识别的主要风险"],
                "technical_recommendations": ["建议的技术栈和工具"],
                "process_suggestions": ["流程优化建议"],
                "success_factors": ["关键成功因素"]
            }
        }
        
        with open(project_data_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        # 显示AI分析结果
        print("")
        print(f"{Colors.GREEN}🎯 AI分析结果{Colors.NC}")
        print("─────────────────────────────")
        print(f"复杂度评分: {Colors.BLUE}{complexity_score}分{Colors.NC}")
        print(f"推荐模式: {Colors.GREEN}{recommended_mode}{Colors.NC}")
        print("")
        
        mode_descriptions = {
            "minimal": "💡 建议理由: 项目相对简单，团队规模较小或时间紧迫，适合轻量级流程",
            "standard": "💡 建议理由: 项目复杂度适中，团队有一定经验，标准流程能平衡效率和质量",
            "complete": "💡 建议理由: 项目复杂度高，有严格质量要求或合规需求，需要完整流程保障"
        }
        print(mode_descriptions[recommended_mode])
        
        print("")
        accept = input("是否接受推荐的模式? (Y/n): ").strip().lower()
        if accept in ['n', 'no']:
            print("请选择您偏好的模式:")
            print("1) minimal  - 最简流程")
            print("2) standard - 标准流程")
            print("3) complete - 完整流程")
            choice = input("选择 (1-3): ").strip()
            mode_map = {"1": "minimal", "2": "standard", "3": "complete"}
            recommended_mode = mode_map.get(choice, recommended_mode)
            if choice not in mode_map:
                self.logger.warning(f"无效选择，使用推荐模式: {recommended_mode}")
        
        return recommended_mode

    def create_clinerules(self, mode: str, project_dir: str, project_name: str):
        """创建.clinerules目录和系统提示词 (混合策略)"""
        self.logger.info("创建AI Agent集成配置...")
        
        clinerules_dir = Path(project_dir) / ".clinerules"
        clinerules_dir.mkdir(exist_ok=True)
        
        # 1. 固定产出文件 - README.md
        self._create_clinerules_readme(clinerules_dir)
        
        # 2. 固定产出文件 - system_prompt.md
        self._create_system_prompt(clinerules_dir, mode, project_name)
        
        # 3. 固定产出文件 - output_format_spec.md
        self._create_output_format_spec(clinerules_dir)
        
        # 4. 固定产出文件 - quality_standards.md
        self._create_quality_standards(clinerules_dir)
        
        # 5. 按模式生成 - [mode]_mode_guide.md
        self._create_mode_guide(clinerules_dir, mode)
        
        self.logger.success("AI Agent集成配置已创建 (.clinerules目录)")

    def _create_clinerules_readme(self, clinerules_dir: Path):
        """创建README.md (固定产出)"""
        readme_content = """# .clinerules 目录说明

## 📋 目录设计说明

`.clinerules` 是一个**目录**，存放着驱动AI Agent理解和遵从AceFlow流程规范工作的系统提示词文件。

## 📁 文件结构 (混合策略)

```
.clinerules/
├── README.md                   # 目录说明 (固定产出)
├── system_prompt.md            # 核心系统提示词 (固定产出)
├── output_format_spec.md       # 输出格式规范 (固定产出)
├── quality_standards.md        # 质量标准规范 (固定产出)
├── [mode]_mode_guide.md        # 模式指导 (按模式生成)
└── current_stage_guide.md      # 当前阶段指导 (动态生成)
```

## 🎯 文件说明

### 固定产出文件 (初始化时生成)
- **README.md**: 目录结构和使用说明
- **system_prompt.md**: AI助手身份定义和核心工作原则
- **output_format_spec.md**: 统一的输出格式规范
- **quality_standards.md**: 企业级质量标准和检查清单

### 模式相关文件 (按需生成)
- **[mode]_mode_guide.md**: 当前流程模式的详细指导

### 动态文件 (运行时更新)
- **current_stage_guide.md**: 当前阶段的具体工作指导

## 🔄 工作原理

1. **初始化**: 固定文件立即可用，提供基础框架和标准
2. **模式适配**: 根据选择的流程模式生成对应指导
3. **动态更新**: 随项目进展更新阶段指导和自定义规则

## 💡 设计优势

- **即时可用**: 核心规范和标准立即生效
- **动态适应**: 阶段指导根据项目状态实时更新
- **维护高效**: 固定文件统一维护，动态文件按需生成

---

**关键理解**: 这套提示词体系让AI Agent从简单的代码助手升级为具备完整项目管理能力的专业开发伙伴！
"""
        
        with open(clinerules_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _create_system_prompt(self, clinerules_dir: Path, mode: str, project_name: str):
        """创建system_prompt.md (固定产出)"""
        system_prompt_content = f"""# AceFlow 系统提示词 - 核心配置

你是一个集成了AceFlow v3.0工作流管理能力的AI助手。AceFlow是一个AI Agent增强层，旨在为你提供企业级的软件开发工作流管理能力。

## 🎯 你的核心使命

你不再是一个简单的代码助手，而是一个具备完整软件工程流程管理能力的专业开发伙伴。你需要：

1. **严格遵循流程规范** - 按照当前项目的流程模式执行工作
2. **维护项目状态** - 实时更新和跟踪项目进度
3. **标准化输出** - 所有工作产出都必须符合AceFlow规范
4. **保持工作连续性** - 跨对话保持项目上下文和状态

## 📋 当前项目信息

- **项目名称**: {project_name}
- **流程模式**: {mode}
- **输出目录**: aceflow_result/
- **配置目录**: .aceflow/

## 🔄 工作流程原则

### 1. 会话开始时必须执行
```
1. 读取 aceflow_result/current_state.json 了解项目当前状态
2. 检查 aceflow_result/stage_progress.json 确定当前阶段进度
3. 根据当前阶段加载对应的工作指导
4. 向用户汇报当前项目状态和下一步工作计划
```

### 2. 工作执行中必须遵循
```
1. 严格按照当前阶段的要求和标准执行任务
2. 所有文档和代码输出必须保存到 aceflow_result/ 目录
3. 遵循统一的文件命名和格式规范
4. 实时更新项目状态和进度信息
```

### 3. 阶段完成时必须执行
```
1. 生成阶段完成总结和质量检查报告
2. 更新 aceflow_result/stage_progress.json 标记阶段完成
3. 更新 aceflow_result/current_state.json 准备进入下一阶段
4. 为下一阶段准备工作上下文和交接信息
```

## 🛠️ 工具集成

你可以使用以下AceFlow工具来辅助工作：

- `./aceflow-stage.py status` - 查看项目状态
- `./aceflow-stage.py next` - 推进到下一阶段
- `./aceflow-validate.py` - 验证项目合规性
- `./aceflow-templates.py` - 管理流程模板

## ⚠️ 重要约束

1. **绝不能跳过阶段** - 必须按照定义的流程顺序执行
2. **绝不能随意修改状态** - 状态变更必须通过正确的流程
3. **绝不能忽略质量标准** - 所有输出都必须符合质量要求
4. **绝不能破坏输出规范** - 文件必须保存到正确的位置和格式

记住：你不仅仅是在写代码或文档，你是在管理一个完整的软件项目！
"""
        
        with open(clinerules_dir / "system_prompt.md", 'w', encoding='utf-8') as f:
            f.write(system_prompt_content)

    def _create_output_format_spec(self, clinerules_dir: Path):
        """创建output_format_spec.md (固定产出)"""
        # 尝试从已有文件复制，否则创建基础版本
        source_file = Path(ACEFLOW_HOME).parent / "taskmaster-demo" / ".clinerules" / "output_format_spec.md"
        
        if source_file.exists():
            shutil.copy2(source_file, clinerules_dir / "output_format_spec.md")
        else:
            self.logger.warning(f"源文件不存在，将创建基础版本: {source_file}")
            self._create_basic_output_format_spec(clinerules_dir)

    def _create_basic_output_format_spec(self, clinerules_dir: Path):
        """创建基础版本的output_format_spec.md"""
        content = """# AceFlow 输出格式规范

## 📁 标准化输出目录

所有工作产出必须保存到 `aceflow_result/` 目录，按照以下结构组织：

```
aceflow_result/
├── current_state.json          # 项目当前状态
├── stage_progress.json         # 各阶段进度跟踪
├── user_stories.md            # 用户故事文档
├── tasks_planning.md          # 任务规划文档
├── test_design.md             # 测试设计文档
├── implementation_report.md   # 实现报告
├── test_report.md             # 测试报告
└── review_report.md           # 评审报告
```

## 📝 文档格式规范

### 标准文档头部
每个文档都必须包含：

```markdown
# 文档标题

> **项目**: 项目名称  
> **阶段**: 当前阶段名称  
> **创建时间**: YYYY-MM-DD  
> **状态**: 进行中/已完成/待审核

## 📋 概述
文档内容概述...
```

### Markdown格式要求
- 使用标准的Markdown格式
- 代码块必须指定语言类型
- 表格使用标准Markdown表格格式
- 适度使用Emoji增强可读性

## 💾 状态文件格式

### current_state.json
```json
{
  "project": {
    "name": "项目名称",
    "mode": "流程模式",
    "created_at": "ISO时间戳",
    "last_updated": "ISO时间戳"
  },
  "flow": {
    "current_stage": "当前阶段名",
    "completed_stages": ["已完成阶段列表"],
    "next_stage": "下一阶段名",
    "progress_percentage": 数字
  }
}
```

## 🏷️ 文件命名规范

- 使用小写字母和下划线
- 阶段文档使用标准命名
- 状态文件使用.json扩展名
- 避免特殊字符和空格
"""
        
        with open(clinerules_dir / "output_format_spec.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_quality_standards(self, clinerules_dir: Path):
        """创建quality_standards.md (固定产出)"""
        # 尝试从已有文件复制，否则创建基础版本
        source_file = Path(ACEFLOW_HOME).parent / "taskmaster-demo" / ".clinerules" / "quality_standards.md"
        
        if source_file.exists():
            shutil.copy2(source_file, clinerules_dir / "quality_standards.md")
        else:
            self.logger.warning(f"源文件不存在，将创建基础版本: {source_file}")
            self._create_basic_quality_standards(clinerules_dir)

    def _create_basic_quality_standards(self, clinerules_dir: Path):
        """创建基础版本的quality_standards.md"""
        content = """# AceFlow 质量标准规范

## 🎯 质量理念

AceFlow的核心价值在于提供**企业级的质量标准**。你的每一个输出都应该达到可以直接在生产环境使用的专业水准。

## 📊 质量标准体系

### Level 1: 基础质量标准 (必须达到)

#### 📝 文档质量
- **完整性**: 包含所有必需的信息，无遗漏
- **准确性**: 技术信息正确，无错误概念
- **清晰性**: 表达清楚，逻辑结构明确
- **专业性**: 使用行业标准术语和格式
- **可读性**: 格式规范，易于理解和维护

#### 💻 代码质量
- **功能性**: 代码能够正确实现预期功能
- **可维护性**: 结构清晰，注释完整
- **可扩展性**: 架构设计支持未来扩展
- **安全性**: 无明显安全漏洞
- **性能**: 满足基本性能要求

#### 🔄 流程质量
- **规范遵循**: 严格按照定义的流程执行
- **状态管理**: 及时准确更新项目状态
- **交付标准**: 每个阶段都有明确的交付物
- **连续性**: 保持跨阶段的工作连续性

### Level 2: 专业质量标准 (努力达到)

#### 📋 需求分析质量
- **用户视角**: 真正从用户需求出发
- **场景完整**: 覆盖主要和边缘使用场景
- **可测试性**: 需求可以转化为具体测试用例
- **可实现性**: 技术方案具备可行性

#### 🏗️ 设计质量
- **架构合理**: 技术架构适合项目规模和需求
- **模块化**: 良好的模块划分和接口设计
- **可扩展**: 设计支持功能扩展和性能扩展
- **容错性**: 考虑异常情况和错误处理

## ⚠️ 质量红线

以下情况绝对不能接受：

1. **功能缺陷**: 核心功能无法正常工作
2. **安全漏洞**: 存在数据泄露或权限绕过风险
3. **性能问题**: 响应时间超出用户可接受范围
4. **数据丢失**: 任何可能导致数据丢失的问题
5. **兼容性问题**: 主流浏览器或设备无法正常使用

记住：**质量不是检查出来的，而是设计和开发出来的！**
"""
        
        with open(clinerules_dir / "quality_standards.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_mode_guide(self, clinerules_dir: Path, mode: str):
        """创建模式指导文件 (按模式生成)"""
        if mode == "standard":
            source_file = Path(ACEFLOW_HOME).parent / "taskmaster-demo" / ".clinerules" / "standard_mode_guide.md"
            if source_file.exists():
                shutil.copy2(source_file, clinerules_dir / "standard_mode_guide.md")
            else:
                self.logger.warning(f"源文件不存在，将创建基础版本: {source_file}")
                self._create_basic_standard_mode_guide(clinerules_dir)
        elif mode == "minimal":
            self._create_minimal_mode_guide(clinerules_dir)
        elif mode == "complete":
            self._create_complete_mode_guide(clinerules_dir)
        elif mode == "smart":
            self._create_smart_mode_guide(clinerules_dir)

    def _create_minimal_mode_guide(self, clinerules_dir: Path):
        """创建minimal模式指导"""
        content = """# AceFlow Minimal模式流程指导

## 🎯 模式概述

Minimal模式是AceFlow最轻量级的工作流程，适合快速原型、小型项目或个人开发。

## 📋 流程阶段 (4个阶段)

1. **analysis** - 需求分析
2. **planning** - 简化规划  
3. **implementation** - 快速实现
4. **validation** - 基础验证

## 🚀 各阶段工作要求

### Analysis (需求分析)
- 快速理解核心需求
- 识别主要功能点
- 评估技术可行性

### Planning (简化规划)
- 选择合适技术栈
- 制定简化架构
- 规划开发顺序

### Implementation (快速实现)
- MVP实现
- 核心功能优先
- 快速迭代

### Validation (基础验证)
- 功能测试
- 基础性能检查
- 用户反馈收集

## ⚡ 模式特点

- **速度优先**: 快速交付可用版本
- **精简流程**: 去除复杂环节
- **核心聚焦**: 专注最重要功能
- **灵活调整**: 支持快速变更
"""
        
        with open(clinerules_dir / "minimal_mode_guide.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_complete_mode_guide(self, clinerules_dir: Path):
        """创建complete模式指导"""
        content = """# AceFlow Complete模式流程指导

## 🎯 模式概述

Complete模式是AceFlow最完整的企业级工作流程，适合大型项目、关键系统或有严格质量要求的项目。

## 📋 流程阶段 (8个阶段)

1. **s1_user_story** - 用户故事分析
2. **s2_tasks_group** - 任务分组规划
3. **s3_testcases** - 测试用例设计
4. **s4_implementation** - 功能实现
5. **s5_test_report** - 测试报告
6. **s6_codereview** - 代码评审
7. **s7_demo_script** - 演示脚本
8. **s8_summary_report** - 项目总结

## 🏗️ 各阶段详细要求

### S1: User Story (用户故事分析)
- 完整的用户故事定义
- 验收标准明确
- 业务价值评估
- 优先级排序

### S2: Tasks Group (任务分组规划)
- 详细任务分解
- 依赖关系分析
- 资源需求评估
- 时间规划

### S3: Test Cases (测试用例设计)
- 全面测试策略
- 详细测试用例
- 自动化测试规划
- 性能测试设计

### S4: Implementation (功能实现)
- 高质量代码实现
- 代码规范遵循
- 文档同步更新
- 安全考虑

### S5: Test Report (测试报告)
- 完整测试执行
- 详细测试报告
- 缺陷跟踪
- 质量评估

### S6: Code Review (代码评审)
- 全面代码评审
- 架构评审
- 安全评审
- 性能评审

### S7: Demo Script (演示脚本)
- 完整演示流程
- 关键功能展示
- 用户培训材料
- 部署指导

### S8: Summary Report (项目总结)
- 项目完成总结
- 经验教训记录
- 改进建议
- 交付确认

## 🎖️ 企业级标准

- **完整文档化**: 每个阶段都有详细文档
- **质量门控**: 严格的质量检查点
- **可追溯性**: 完整的变更记录
- **合规保证**: 满足企业级要求
"""
        
        with open(clinerules_dir / "complete_mode_guide.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_smart_mode_guide(self, clinerules_dir: Path):
        """创建smart模式指导"""
        content = """# AceFlow Smart模式流程指导

## 🎯 模式概述

Smart模式是AceFlow的AI驱动自适应工作流程，根据项目特点智能选择最适合的流程路径。

## 🧠 智能决策机制

### 复杂度评估
- **≤30分**: 自动采用minimal流程
- **31-70分**: 自动采用standard流程  
- **≥71分**: 自动采用complete流程

### 评估维度
1. **项目规模**: 功能复杂度、数据规模
2. **团队背景**: 人员规模、经验水平
3. **时间约束**: 紧急程度、里程碑要求
4. **质量要求**: 合规需求、稳定性要求
5. **风险评估**: 技术风险、业务风险

## 🔄 自适应流程

### 动态调整
- 项目进行中可重新评估
- 根据实际情况调整流程
- 保持灵活性和效率平衡

### AI建议
- 实时提供流程优化建议
- 识别潜在风险和瓶颈
- 推荐最佳实践

## 📊 智能监控

### 进度跟踪
- 自动识别延期风险
- 提供进度优化建议
- 智能资源调配

### 质量监控
- 持续质量评估
- 自动发现质量问题
- 提供改进路径

## 🎯 使用场景

- **新项目**: 不确定最佳流程时
- **混合团队**: 经验水平差异较大
- **变化需求**: 需求可能发生变化
- **学习优化**: 希望持续改进流程
"""
        
        with open(clinerules_dir / "smart_mode_guide.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def create_project_state(self, mode: str, project_name: str, project_dir: str):
        """创建项目状态文件"""
        self.logger.info("初始化项目状态...")
        
        aceflow_result_dir = Path(project_dir) / "aceflow_result"
        aceflow_result_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        first_stage = self._get_first_stage(mode)
        
        current_state = {
            "project": {
                "name": project_name,
                "mode": mode,
                "created_at": timestamp,
                "last_updated": timestamp,
                "version": VERSION
            },
            "flow": {
                "current_stage": "initialized",
                "completed_stages": [],
                "next_stage": first_stage,
                "progress_percentage": 0
            },
            "memory": {
                "enabled": True,
                "last_session": timestamp,
                "context_preserved": True
            },
            "quality": {
                "standards_applied": True,
                "compliance_checked": False,
                "last_validation": None
            }
        }
        
        with open(aceflow_result_dir / "current_state.json", 'w', encoding='utf-8') as f:
            json.dump(current_state, f, ensure_ascii=False, indent=2)
        
        # 创建阶段进度跟踪文件
        self._initialize_stage_progress(mode, aceflow_result_dir)
        
        self.logger.success("项目状态初始化完成")

    def _get_first_stage(self, mode: str) -> str:
        """获取第一个阶段"""
        stage_map = {
            "minimal": "analysis",
            "standard": "user_stories",
            "complete": "s1_user_story",
            "smart": "analysis"
        }
        return stage_map.get(mode, "analysis")

    def _initialize_stage_progress(self, mode: str, aceflow_result_dir: Path):
        """初始化阶段进度"""
        if mode == "standard":
            stages = {
                "user_stories": {"status": "pending", "progress": 0},
                "tasks_planning": {"status": "pending", "progress": 0},
                "test_design": {"status": "pending", "progress": 0},
                "implementation": {"status": "pending", "progress": 0},
                "testing": {"status": "pending", "progress": 0},
                "review": {"status": "pending", "progress": 0}
            }
        elif mode == "complete":
            stages = {
                "s1_user_story": {"status": "pending", "progress": 0},
                "s2_tasks_group": {"status": "pending", "progress": 0},
                "s3_testcases": {"status": "pending", "progress": 0},
                "s4_implementation": {"status": "pending", "progress": 0},
                "s5_test_report": {"status": "pending", "progress": 0},
                "s6_codereview": {"status": "pending", "progress": 0},
                "s7_demo_script": {"status": "pending", "progress": 0},
                "s8_summary_report": {"status": "pending", "progress": 0}
            }
        elif mode == "smart":
            stages = {
                "analysis": {"status": "pending", "progress": 0, "adaptive": True},
                "planning": {"status": "pending", "progress": 0, "adaptive": True},
                "implementation": {"status": "pending", "progress": 0, "adaptive": True},
                "validation": {"status": "pending", "progress": 0, "adaptive": True}
            }
        else:  # minimal
            stages = {
                "analysis": {"status": "pending", "progress": 0},
                "planning": {"status": "pending", "progress": 0},
                "implementation": {"status": "pending", "progress": 0},
                "validation": {"status": "pending", "progress": 0}
            }
        
        stage_progress = {"stages": stages}
        if mode == "smart":
            stage_progress["adaptive_mode"] = True
            stage_progress["recommended_flow"] = "standard"
        
        with open(aceflow_result_dir / "stage_progress.json", 'w', encoding='utf-8') as f:
            json.dump(stage_progress, f, ensure_ascii=False, indent=2)

    def copy_project_scripts(self, project_dir: str):
        """拷贝项目级工作脚本 (方案3实施)"""
        self.logger.info("拷贝项目级工作脚本...")
        
        project_scripts = [
            "aceflow-stage.py",
            "aceflow-validate.py", 
            "aceflow-templates.py"
        ]
        
        copied_count = 0
        script_source_dir = Path(ACEFLOW_HOME) / "scripts"
        
        # 检查源脚本目录
        if not script_source_dir.exists():
            self.logger.error(f"脚本源目录不存在: {script_source_dir}")
            return
        
        # 拷贝每个脚本
        for script in project_scripts:
            source_path = script_source_dir / script
            target_path = Path(project_dir) / script
            
            if source_path.exists():
                shutil.copy2(source_path, target_path)
                # 设置执行权限
                target_path.chmod(0o755)
                self.logger.success(f"✅ 已拷贝: {script}")
                copied_count += 1
            else:
                self.logger.warning(f"⚠️ 源脚本不存在: {source_path}")
        
        # 创建脚本使用说明
        scripts_readme_content = """# AceFlow 项目级脚本说明 (Python版本)

本项目包含以下AceFlow工作脚本，用于项目管理和状态控制：

## 🛠️ 可用脚本

### 1. aceflow-stage.py - 阶段管理
```bash
python aceflow-stage.py status          # 查看当前阶段状态
python aceflow-stage.py next            # 推进到下一阶段
python aceflow-stage.py list            # 列出所有阶段
python aceflow-stage.py reset           # 重置项目状态
```

### 2. aceflow-validate.py - 项目验证
```bash
python aceflow-validate.py              # 标准验证
python aceflow-validate.py --mode=complete --report  # 完整验证并生成报告
python aceflow-validate.py --fix        # 自动修复问题
```

### 3. aceflow-templates.py - 模板管理
```bash
python aceflow-templates.py list        # 列出可用模板
python aceflow-templates.py apply       # 应用模板
python aceflow-templates.py validate    # 验证模板
```

## 📋 使用建议

1. **AI Agent集成**: 这些脚本被设计为与AI Agent协同工作
2. **状态管理**: 使用 `aceflow-stage.py` 管理项目进度
3. **质量保证**: 定期运行 `aceflow-validate.py` 确保合规性
4. **模板利用**: 使用 `aceflow-templates.py` 标准化工作流程

## ⚠️ 重要提醒

- 这些脚本是项目级副本，与全局安装的Python CLI配合使用
- 脚本会自动识别项目结构和配置，无需额外设置
- 如需更新脚本，重新运行初始化命令即可

## 🌍 跨平台兼容性

- **Python版本**: 支持Python 3.7+
- **操作系统**: Windows、macOS、Linux
- **依赖**: 仅使用Python标准库，无额外依赖
"""
        
        with open(Path(project_dir) / "SCRIPTS_README.md", 'w', encoding='utf-8') as f:
            f.write(scripts_readme_content)
        
        self.logger.success(f"✅ 项目级脚本拷贝完成 ({copied_count}/3)")
        self.logger.info("📝 已创建脚本使用说明: SCRIPTS_README.md")

    def init_project_config(self, mode: str, project_name: str, project_dir: str) -> bool:
        """初始化项目配置"""
        self.logger.info("初始化项目配置...")
        
        # 创建必要目录
        aceflow_result_dir = Path(project_dir) / "aceflow_result"
        aceflow_config_dir = Path(project_dir) / ".aceflow"
        
        aceflow_result_dir.mkdir(exist_ok=True)
        aceflow_config_dir.mkdir(exist_ok=True)
        
        # 复制模板文件
        template_dir = Path(ACEFLOW_HOME) / "templates" / mode
        if template_dir.exists():
            self.logger.info(f"应用 {mode} 模式模板...")
            for item in template_dir.iterdir():
                if item.is_file():
                    target = aceflow_config_dir / item.name
                    shutil.copy2(item, target)
                    
                    # 替换模板中的占位符
                    if item.name == "template.yaml":
                        content = target.read_text(encoding='utf-8')
                        content = content.replace('name: "新建项目"', f'name: "{project_name}"')
                        target.write_text(content, encoding='utf-8')
        else:
            self.logger.error(f"模板目录不存在: {template_dir}")
            return False
        
        # 创建.clinerules目录 (AI Agent集成)
        self.create_clinerules(mode, project_dir, project_name)
        
        # 初始化项目状态文件
        self.create_project_state(mode, project_name, project_dir)
        
        # 拷贝项目级工作脚本 (方案3)
        self.copy_project_scripts(project_dir)
        
        self.logger.success("项目配置初始化完成")
        return True

    def show_result(self, mode: str, project_name: str, project_dir: str):
        """显示初始化结果"""
        print("")
        self.logger.success("🎉 AceFlow v3.0 项目初始化完成!")
        print("")
        print(f"{Colors.CYAN}项目信息:{Colors.NC}")
        print(f"  名称: {project_name}")
        print(f"  模式: {mode}")
        print(f"  目录: {project_dir}")
        print("")
        print(f"{Colors.CYAN}重要文件:{Colors.NC}")
        print("  📋 .clinerules               - AI Agent工作配置")
        print("  📊 aceflow_result/           - 项目输出目录")
        print("  ⚙️  .aceflow/                - 流程配置目录")
        print("  📝 SCRIPTS_README.md         - 脚本使用说明")
        print("")
        print(f"{Colors.CYAN}工具命令:{Colors.NC}")
        print("  🔍 python aceflow-validate.py   - 验证项目状态")
        print("  📋 python aceflow-stage.py      - 阶段管理")
        print("  🛠️  python aceflow-templates.py - 模板管理")
        print("")
        self.logger.success("现在您可以开始使用AI Agent进行开发了！")
        print(f"AI将按照 {Colors.BLUE}{mode}{Colors.NC} 模式的流程自动工作并保持状态连续性。")

    def run(self):
        """主运行函数"""
        parser = argparse.ArgumentParser(
            description="AceFlow v3.0 项目初始化脚本 (Python版本)",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument('-m', '--mode', 
                          choices=['minimal', 'standard', 'complete', 'smart'],
                          help='指定流程模式')
        parser.add_argument('-p', '--project', 
                          help='指定项目名称')
        parser.add_argument('-d', '--directory', 
                          default=os.getcwd(),
                          help='指定项目目录 (默认: 当前目录)')
        parser.add_argument('-i', '--interactive', 
                          action='store_true',
                          help='启用交互式配置')
        parser.add_argument('-f', '--force', 
                          action='store_true',
                          help='强制覆盖已存在的配置')
        parser.add_argument('-v', '--version', 
                          action='version',
                          version=f'AceFlow v{VERSION}')
        
        args = parser.parse_args()
        
        # 显示标题
        self.logger.header()
        
        # 检查依赖
        if not self.check_dependencies():
            return 1
        
        # 检测AI Agent环境
        if not self.detect_ai_agent():
            self.logger.warning("建议安装支持的AI Agent以获得最佳体验")
        
        mode = args.mode
        project_name = args.project
        
        # 交互式模式或智能模式的特殊处理
        if args.interactive or mode == 'smart':
            if not project_name:
                project_name = input("请输入项目名称: ").strip()
            
            if mode == 'smart':
                self.logger.info("启动Smart模式智能分析...")
                mode = self.ai_interview()
            elif not mode:
                print("请选择流程模式:")
                print("1) minimal  - 最简流程 (快速原型、小型项目)")
                print("2) standard - 标准流程 (中等规模团队项目)")
                print("3) complete - 完整流程 (企业级大型项目)")
                print("4) smart    - 智能流程 (AI驱动自适应)")
                choice = input("选择 (1-4): ").strip()
                mode_map = {"1": "minimal", "2": "standard", "3": "complete", "4": "smart"}
                mode = mode_map.get(choice)
                if not mode:
                    self.logger.error("无效选择")
                    return 1
                if mode == 'smart':
                    mode = self.ai_interview()
        
        # 参数验证
        if not mode:
            self.logger.error("请指定流程模式 (-m|--mode)")
            parser.print_help()
            return 1
        
        if not project_name:
            project_name = f"AceFlow项目-{datetime.now().strftime('%Y%m%d')}"
            self.logger.info(f"使用默认项目名称: {project_name}")
        
        # 检查项目目录
        project_dir = Path(args.directory).resolve()
        project_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"项目目录: {project_dir}")
        
        # 检查是否已存在配置
        clinerules_path = project_dir / ".clinerules"
        if clinerules_path.exists() and not args.force:
            self.logger.error("项目已存在AceFlow配置，使用 --force 强制覆盖")
            return 1
        
        # 执行初始化
        os.chdir(project_dir)
        if self.init_project_config(mode, project_name, str(project_dir)):
            # 显示结果
            self.show_result(mode, project_name, str(project_dir))
            return 0
        else:
            return 1

def main():
    """主函数"""
    try:
        app = AceFlowInit()
        return app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}操作被用户中断{Colors.NC}")
        return 1
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.NC} 发生未预期的错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())