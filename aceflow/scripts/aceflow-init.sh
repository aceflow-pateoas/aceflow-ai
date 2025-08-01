#!/bin/bash

# AceFlow v3.0 项目初始化脚本
# AI Agent 增强层初始化工具

set -e

# 脚本信息
SCRIPT_NAME="aceflow-init.sh"
VERSION="3.0.0"
ACEFLOW_HOME="${ACEFLOW_HOME:-/home/chenjing/AI/aceflow-ai/aceflow}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}
╔══════════════════════════════════════╗
║         AceFlow v3.0 初始化          ║
║       AI Agent 增强层配置工具        ║
╚══════════════════════════════════════╝${NC}"
}

# 帮助信息
show_help() {
    cat << EOF
AceFlow v3.0 项目初始化脚本

用法: $SCRIPT_NAME [选项]

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
  $SCRIPT_NAME --mode=smart --interactive
  $SCRIPT_NAME -m standard -p "我的项目" -d ./my-project
  $SCRIPT_NAME --force --mode=complete

EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查环境依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装Python 3.7+"
        exit 1
    fi
    
    # 检查AceFlow Python包
    if ! python3 -c "import aceflow" 2>/dev/null; then
        log_warning "AceFlow Python包未安装，将使用本地版本"
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        log_warning "Git未安装，某些功能可能受限"
    fi
    
    log_success "环境检查完成"
}

# 检测AI Agent环境
detect_ai_agent() {
    log_info "检测AI Agent环境..."
    
    local detected_agents=()
    
    # 检测Cline
    if command -v cline &> /dev/null || [ -f ".cline_project" ]; then
        detected_agents+=("Cline")
    fi
    
    # 检测Cursor
    if command -v cursor &> /dev/null || [ -f ".cursor" ]; then
        detected_agents+=("Cursor")
    fi
    
    # 检测Claude Code
    if command -v claude &> /dev/null || [ -n "$CLAUDE_CODE_API_KEY" ]; then
        detected_agents+=("Claude Code")
    fi
    
    if [ ${#detected_agents[@]} -eq 0 ]; then
        log_warning "未检测到支持的AI Agent环境"
        log_info "AceFlow支持: Cline, Cursor, Claude Code"
        return 1
    else
        log_success "检测到AI Agent: ${detected_agents[*]}"
        return 0
    fi
}

# AI智能访谈 (Smart模式专用)
ai_interview() {
    local project_data_file="aceflow_result/project_analysis.json"
    
    log_header
    echo -e "${CYAN}🧠 AI智能项目分析访谈${NC}"
    echo "AceFlow将通过几个问题了解您的项目，以提供最适合的配置建议。"
    echo ""
    
    # 创建临时文件存储答案
    local answers_file=$(mktemp)
    
    # 问题1: 项目性质和目标
    echo -e "${YELLOW}📋 问题1: 项目性质和目标${NC}"
    echo "请简要描述您的项目性质、主要目标和预期成果："
    read -p "> " project_nature
    echo "project_nature: $project_nature" >> "$answers_file"
    
    # 问题2: 团队背景
    echo -e "${YELLOW}👥 问题2: 团队背景${NC}"
    echo "请描述团队规模、成员经验水平和技术背景："
    echo "例如: 5人团队，2年经验，主要使用Python/React技术栈"
    read -p "> " team_context
    echo "team_context: $team_context" >> "$answers_file"
    
    # 问题3: 约束条件
    echo -e "${YELLOW}⏰ 问题3: 约束条件${NC}"
    echo "主要约束条件有哪些？(时间、预算、技术限制、合规要求等)"
    read -p "> " constraints
    echo "constraints: $constraints" >> "$answers_file"
    
    # 问题4: 成功标准
    echo -e "${YELLOW}🎯 问题4: 成功标准${NC}"
    echo "什么情况下您认为这个项目是成功的？关键指标是什么？"
    read -p "> " success_criteria  
    echo "success_criteria: $success_criteria" >> "$answers_file"
    
    # 问题5: 风险关注
    echo -e "${YELLOW}⚠️  问题5: 风险关注${NC}"
    echo "您最担心的风险点是什么？技术风险、进度风险还是质量风险？"
    read -p "> " risk_concerns
    echo "risk_concerns: $risk_concerns" >> "$answers_file"
    
    # AI分析 (模拟)
    echo ""
    log_info "AI正在分析您的回答..."
    sleep 2
    
    # 简单的智能分析逻辑
    local complexity_score=0
    local recommended_mode=""
    
    # 基于关键词的简单评分算法
    if echo "$project_nature $team_context" | grep -iE "(大型|企业级|复杂|银行|金融|医疗)" > /dev/null; then
        ((complexity_score += 30))
    fi
    
    if echo "$team_context" | grep -iE "([1-2]人|个人|新手)" > /dev/null; then
        ((complexity_score += 10))
    elif echo "$team_context" | grep -iE "([5-9]人|经验丰富)" > /dev/null; then
        ((complexity_score += 20))  
    elif echo "$team_context" | grep -iE "(10人以上|大团队)" > /dev/null; then
        ((complexity_score += 30))
    fi
    
    if echo "$constraints" | grep -iE "(合规|监管|严格)" > /dev/null; then
        ((complexity_score += 25))
    fi
    
    if echo "$constraints" | grep -iE "(紧急|快速|原型)" > /dev/null; then
        ((complexity_score -= 15))
    fi
    
    # 推荐模式
    if [ $complexity_score -le 30 ]; then
        recommended_mode="minimal"
    elif [ $complexity_score -le 70 ]; then
        recommended_mode="standard"
    else
        recommended_mode="complete"
    fi
    
    # 保存分析结果
    mkdir -p aceflow_result
    cat > "$project_data_file" << EOF
{
  "analysis_timestamp": "$(date -Iseconds)",
  "project_nature": "$project_nature",
  "team_context": "$team_context", 
  "constraints": "$constraints",
  "success_criteria": "$success_criteria",
  "risk_concerns": "$risk_concerns",
  "complexity_score": $complexity_score,
  "recommended_mode": "$recommended_mode",
  "ai_insights": {
    "primary_risks": ["基于输入识别的主要风险"],
    "technical_recommendations": ["建议的技术栈和工具"],
    "process_suggestions": ["流程优化建议"],
    "success_factors": ["关键成功因素"]
  }
}
EOF
    
    # 显示AI分析结果
    echo ""
    echo -e "${GREEN}🎯 AI分析结果${NC}"
    echo "─────────────────────────────"
    echo -e "复杂度评分: ${BLUE}$complexity_score分${NC}"
    echo -e "推荐模式: ${GREEN}$recommended_mode${NC}"
    echo ""
    
    case $recommended_mode in
        "minimal")
            echo "💡 建议理由: 项目相对简单，团队规模较小或时间紧迫，适合轻量级流程"
            ;;
        "standard")
            echo "💡 建议理由: 项目复杂度适中，团队有一定经验，标准流程能平衡效率和质量"
            ;;
        "complete")
            echo "💡 建议理由: 项目复杂度高，有严格质量要求或合规需求，需要完整流程保障"
            ;;
    esac
    
    echo ""
    read -p "是否接受推荐的模式? (Y/n): " accept_recommendation
    if [[ $accept_recommendation =~ ^[Nn]$ ]]; then
        echo "请选择您偏好的模式:"
        echo "1) minimal  - 最简流程"
        echo "2) standard - 标准流程"  
        echo "3) complete - 完整流程"
        read -p "选择 (1-3): " mode_choice
        case $mode_choice in
            1) recommended_mode="minimal" ;;
            2) recommended_mode="standard" ;;
            3) recommended_mode="complete" ;;
            *) log_warning "无效选择，使用推荐模式: $recommended_mode" ;;
        esac
    fi
    
    rm -f "$answers_file"
    echo "$recommended_mode"
}

# 初始化项目配置
init_project_config() {
    local mode=$1
    local project_name=$2
    local project_dir=$3
    
    log_info "初始化项目配置..."
    
    # 创建必要目录
    mkdir -p "$project_dir/aceflow_result"
    mkdir -p "$project_dir/.aceflow"
    
    # 复制模板文件 
    local template_dir="$ACEFLOW_HOME/templates/$mode"
    if [ -d "$template_dir" ]; then
        log_info "应用 $mode 模式模板..."
        cp -r "$template_dir"/* "$project_dir/.aceflow/"
        
        # 替换模板中的占位符
        if [ -f "$project_dir/.aceflow/template.yaml" ]; then
            sed -i "s/name: \"新建项目\"/name: \"$project_name\"/" "$project_dir/.aceflow/template.yaml"
        fi
    else
        log_error "模板目录不存在: $template_dir"
        return 1
    fi
    
    # 创建.clinerules目录 (AI Agent集成)
    create_clinerules "$mode" "$project_dir" "$project_name"
    
    # 初始化项目状态文件
    create_project_state "$mode" "$project_name" "$project_dir"
    
    # 拷贝项目级工作脚本 (方案3)
    copy_project_scripts "$project_dir"
    
    log_success "项目配置初始化完成"
}

# 创建.clinerules目录和系统提示词 (混合策略)
create_clinerules() {
    local mode=$1
    local project_dir=$2
    local project_name=${3:-"AceFlow项目"}
    
    log_info "创建AI Agent集成配置..."
    
    # 创建.clinerules目录
    mkdir -p "$project_dir/.clinerules"
    
    # 1. 固定产出文件 - README.md
    create_clinerules_readme "$project_dir"
    
    # 2. 固定产出文件 - system_prompt.md
    create_system_prompt "$project_dir" "$mode" "$project_name"
    
    # 3. 固定产出文件 - output_format_spec.md
    create_output_format_spec "$project_dir"
    
    # 4. 固定产出文件 - quality_standards.md
    create_quality_standards "$project_dir"
    
    # 5. 按模式生成 - [mode]_mode_guide.md
    create_mode_guide "$project_dir" "$mode"
    
    log_success "AI Agent集成配置已创建 (.clinerules目录)"
}

# 创建README.md (固定产出)
create_clinerules_readme() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/README.md" << 'EOF'
# .clinerules 目录说明

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
EOF
}

# 创建system_prompt.md (固定产出)
create_system_prompt() {
    local project_dir=$1
    local mode=$2
    local project_name=$3
    
    cat > "$project_dir/.clinerules/system_prompt.md" << EOF
# AceFlow 系统提示词 - 核心配置

你是一个集成了AceFlow v3.0工作流管理能力的AI助手。AceFlow是一个AI Agent增强层，旨在为你提供企业级的软件开发工作流管理能力。

## 🎯 你的核心使命

你不再是一个简单的代码助手，而是一个具备完整软件工程流程管理能力的专业开发伙伴。你需要：

1. **严格遵循流程规范** - 按照当前项目的流程模式执行工作
2. **维护项目状态** - 实时更新和跟踪项目进度
3. **标准化输出** - 所有工作产出都必须符合AceFlow规范
4. **保持工作连续性** - 跨对话保持项目上下文和状态

## 📋 当前项目信息

- **项目名称**: $project_name
- **流程模式**: $mode
- **输出目录**: aceflow_result/
- **配置目录**: .aceflow/

## 🔄 工作流程原则

### 1. 会话开始时必须执行
\`\`\`
1. 读取 aceflow_result/current_state.json 了解项目当前状态
2. 检查 aceflow_result/stage_progress.json 确定当前阶段进度
3. 根据当前阶段加载对应的工作指导
4. 向用户汇报当前项目状态和下一步工作计划
\`\`\`

### 2. 工作执行中必须遵循
\`\`\`
1. 严格按照当前阶段的要求和标准执行任务
2. 所有文档和代码输出必须保存到 aceflow_result/ 目录
3. 遵循统一的文件命名和格式规范
4. 实时更新项目状态和进度信息
\`\`\`

### 3. 阶段完成时必须执行
\`\`\`
1. 生成阶段完成总结和质量检查报告
2. 更新 aceflow_result/stage_progress.json 标记阶段完成
3. 更新 aceflow_result/current_state.json 准备进入下一阶段
4. 为下一阶段准备工作上下文和交接信息
\`\`\`

## 🛠️ 工具集成

你可以使用以下AceFlow工具来辅助工作：

- \`./aceflow-stage.sh status\` - 查看项目状态
- \`./aceflow-stage.sh next\` - 推进到下一阶段
- \`./aceflow-validate.sh\` - 验证项目合规性
- \`./aceflow-templates.sh\` - 管理流程模板

## ⚠️ 重要约束

1. **绝不能跳过阶段** - 必须按照定义的流程顺序执行
2. **绝不能随意修改状态** - 状态变更必须通过正确的流程
3. **绝不能忽略质量标准** - 所有输出都必须符合质量要求
4. **绝不能破坏输出规范** - 文件必须保存到正确的位置和格式

记住：你不仅仅是在写代码或文档，你是在管理一个完整的软件项目！
EOF
}

# 创建output_format_spec.md (固定产出)
create_output_format_spec() {
    local project_dir=$1
    local source_file="$ACEFLOW_HOME/../taskmaster-demo/.clinerules/output_format_spec.md"
    
    if [ -f "$source_file" ]; then
        cp "$source_file" "$project_dir/.clinerules/output_format_spec.md"
    else
        log_warning "源文件不存在，将创建基础版本: $source_file"
        create_basic_output_format_spec "$project_dir"
    fi
}

# 创建基础版本的output_format_spec.md
create_basic_output_format_spec() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/output_format_spec.md" << 'EOF'
# AceFlow 输出格式规范

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
EOF
}

# 创建quality_standards.md (固定产出) 
create_quality_standards() {
    local project_dir=$1
    local source_file="$ACEFLOW_HOME/../taskmaster-demo/.clinerules/quality_standards.md"
    
    if [ -f "$source_file" ]; then
        cp "$source_file" "$project_dir/.clinerules/quality_standards.md"
    else
        log_warning "源文件不存在，将创建基础版本: $source_file"
        create_basic_quality_standards "$project_dir"
    fi
}

# 创建基础版本的quality_standards.md
create_basic_quality_standards() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/quality_standards.md" << 'EOF'
# AceFlow 质量标准规范

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
EOF
}

# 创建模式指导文件 (按模式生成)
create_mode_guide() {
    local project_dir=$1
    local mode=$2
    
    case $mode in
        "standard")
            local source_file="$ACEFLOW_HOME/../taskmaster-demo/.clinerules/standard_mode_guide.md"
            if [ -f "$source_file" ]; then
                cp "$source_file" "$project_dir/.clinerules/standard_mode_guide.md"
            else
                log_warning "源文件不存在，将创建基础版本: $source_file"
                create_basic_standard_mode_guide "$project_dir"
            fi
            ;;
        "minimal")
            create_minimal_mode_guide "$project_dir"
            ;;
        "complete")
            create_complete_mode_guide "$project_dir"
            ;;
        "smart")
            create_smart_mode_guide "$project_dir"
            ;;
    esac
}

# 创建minimal模式指导
create_minimal_mode_guide() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/minimal_mode_guide.md" << 'EOF'
# AceFlow Minimal模式流程指导

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
EOF
}

# 创建complete模式指导
create_complete_mode_guide() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/complete_mode_guide.md" << 'EOF'
# AceFlow Complete模式流程指导

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
EOF
}

# 创建smart模式指导
create_smart_mode_guide() {
    local project_dir=$1
    
    cat > "$project_dir/.clinerules/smart_mode_guide.md" << 'EOF'
# AceFlow Smart模式流程指导

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
EOF
}

# 创建项目状态文件
create_project_state() {
    local mode=$1
    local project_name=$2
    local project_dir=$3
    
    log_info "初始化项目状态..."
    
    cat > "$project_dir/aceflow_result/current_state.json" << EOF
{
  "project": {
    "name": "$project_name",
    "mode": "$mode", 
    "created_at": "$(date -Iseconds)",
    "last_updated": "$(date -Iseconds)",
    "version": "3.0.0"
  },
  "flow": {
    "current_stage": "initialized",
    "completed_stages": [],
    "next_stage": "$(get_first_stage $mode)",
    "progress_percentage": 0
  },
  "memory": {
    "enabled": true,
    "last_session": "$(date -Iseconds)",
    "context_preserved": true
  },
  "quality": {
    "standards_applied": true,
    "compliance_checked": false,
    "last_validation": null
  }
}
EOF
    
    # 创建阶段进度跟踪文件
    initialize_stage_progress "$mode" "$project_dir"
    
    log_success "项目状态初始化完成"
}

# 获取第一个阶段
get_first_stage() {
    local mode=$1
    case $mode in
        "minimal") echo "analysis" ;;
        "standard") echo "user_stories" ;;
        "complete") echo "s1_user_story" ;;
        "smart") echo "analysis" ;;
        *) echo "analysis" ;;
    esac
}

# 初始化阶段进度
initialize_stage_progress() {
    local mode=$1
    local project_dir=$2
    
    case $mode in
        "minimal")
            cat > "$project_dir/aceflow_result/stage_progress.json" << EOF
{
  "stages": {
    "analysis": { "status": "pending", "progress": 0 },
    "planning": { "status": "pending", "progress": 0 },
    "implementation": { "status": "pending", "progress": 0 },
    "validation": { "status": "pending", "progress": 0 }
  }
}
EOF
            ;;
        "standard")
            cat > "$project_dir/aceflow_result/stage_progress.json" << EOF
{
  "stages": {
    "user_stories": { "status": "pending", "progress": 0 },
    "tasks_planning": { "status": "pending", "progress": 0 },
    "test_design": { "status": "pending", "progress": 0 },
    "implementation": { "status": "pending", "progress": 0 },
    "testing": { "status": "pending", "progress": 0 },
    "review": { "status": "pending", "progress": 0 }
  }
}
EOF
            ;;
        "complete")
            cat > "$project_dir/aceflow_result/stage_progress.json" << EOF
{
  "stages": {
    "s1_user_story": { "status": "pending", "progress": 0 },
    "s2_tasks_group": { "status": "pending", "progress": 0 },
    "s3_testcases": { "status": "pending", "progress": 0 },
    "s4_implementation": { "status": "pending", "progress": 0 },
    "s5_test_report": { "status": "pending", "progress": 0 },
    "s6_codereview": { "status": "pending", "progress": 0 },
    "s7_demo_script": { "status": "pending", "progress": 0 },
    "s8_summary_report": { "status": "pending", "progress": 0 }
  }
}
EOF
            ;;
        "smart")
            cat > "$project_dir/aceflow_result/stage_progress.json" << EOF
{
  "adaptive_mode": true,
  "recommended_flow": "standard",
  "stages": {
    "analysis": { "status": "pending", "progress": 0, "adaptive": true },
    "planning": { "status": "pending", "progress": 0, "adaptive": true },
    "implementation": { "status": "pending", "progress": 0, "adaptive": true },
    "validation": { "status": "pending", "progress": 0, "adaptive": true }
  }
}
EOF
            ;;
    esac
}

# 拷贝项目级工作脚本 (方案3实施)
copy_project_scripts() {
    local project_dir=$1
    
    log_info "拷贝项目级工作脚本..."
    
    # 定义需要拷贝的项目级脚本
    local project_scripts=(
        "aceflow-stage.sh"
        "aceflow-validate.sh" 
        "aceflow-templates.sh"
    )
    
    local copied_count=0
    local script_source_dir="$ACEFLOW_HOME/scripts"
    
    # 检查源脚本目录
    if [ ! -d "$script_source_dir" ]; then
        log_error "脚本源目录不存在: $script_source_dir"
        return 1
    fi
    
    # 拷贝每个脚本
    for script in "${project_scripts[@]}"; do
        local source_path="$script_source_dir/$script"
        local target_path="$project_dir/$script"
        
        if [ -f "$source_path" ]; then
            cp "$source_path" "$target_path"
            chmod +x "$target_path"
            log_success "✅ 已拷贝: $script"
            ((copied_count++))
        else
            log_warning "⚠️  源脚本不存在: $source_path"
        fi
    done
    
    # 创建脚本使用说明
    cat > "$project_dir/SCRIPTS_README.md" << 'EOF'
# AceFlow 项目级脚本说明

本项目包含以下AceFlow工作脚本，用于项目管理和状态控制：

## 🛠️ 可用脚本

### 1. aceflow-stage.sh - 阶段管理
```bash
./aceflow-stage.sh status          # 查看当前阶段状态
./aceflow-stage.sh next            # 推进到下一阶段
./aceflow-stage.sh list            # 列出所有阶段
./aceflow-stage.sh reset           # 重置项目状态
```

### 2. aceflow-validate.sh - 项目验证
```bash
./aceflow-validate.sh              # 标准验证
./aceflow-validate.sh --mode=complete --report  # 完整验证并生成报告
./aceflow-validate.sh --fix        # 自动修复问题
```

### 3. aceflow-templates.sh - 模板管理
```bash
./aceflow-templates.sh list        # 列出可用模板
./aceflow-templates.sh apply       # 应用模板
./aceflow-templates.sh validate    # 验证模板
```

## 📋 使用建议

1. **AI Agent集成**: 这些脚本被设计为与AI Agent协同工作
2. **状态管理**: 使用 `aceflow-stage.sh` 管理项目进度
3. **质量保证**: 定期运行 `aceflow-validate.sh` 确保合规性
4. **模板利用**: 使用 `aceflow-templates.sh` 标准化工作流程

## ⚠️ 重要提醒

- 这些脚本是项目级副本，与全局安装的 `aceflow-init.sh` 配合使用
- 脚本会自动识别项目结构和配置，无需额外设置
- 如需更新脚本，重新运行 `aceflow-init.sh --force` 即可
EOF
    
    log_success "✅ 项目级脚本拷贝完成 ($copied_count/3)"
    log_info "📝 已创建脚本使用说明: SCRIPTS_README.md"
}

# 项目初始化完成后的后续操作
post_init_setup() {
    local mode=$1
    local project_dir=$2
    
    log_info "执行初始化后续操作..."
    
    # 创建模式特定的提示文件
    case $mode in
        "smart")
            cat > "$project_dir/aceflow_result/next_steps.md" << EOF
# 🚀 AceFlow Smart模式 - 下一步操作

## 立即开始
您的项目已配置为智能自适应模式。AI将根据项目特点动态调整流程。

## 建议的开始方式
1. **查看AI分析结果**: \`cat aceflow_result/project_analysis.json\`
2. **开始第一阶段**: 向AI Agent说明需求，AI将自动按照配置的流程工作
3. **监控进度**: 使用 \`aceflow-validate.sh\` 检查项目状态

## 关键文件
- \`.clinerules\`: AI Agent工作指南
- \`aceflow_result/current_state.json\`: 项目状态
- \`.aceflow/template.yaml\`: 流程配置

记住: 所有工作产出都会保存在 aceflow_result/ 目录中。
EOF
            ;;
        *)
            cat > "$project_dir/aceflow_result/next_steps.md" << EOF
# 🚀 AceFlow $mode模式 - 下一步操作

## 立即开始
您的项目已配置为 $mode 模式。请按照以下步骤开始:

1. **查看流程配置**: \`cat .aceflow/template.yaml\`
2. **开始工作**: 向AI Agent描述需求，AI将按照配置的流程执行
3. **跟踪进度**: 检查 \`aceflow_result/current_state.json\`

## 关键文件
- \`.clinerules\`: AI Agent工作指南  
- \`aceflow_result/\`: 项目输出目录
- \`.aceflow/\`: 配置和模板目录

开始愉快的AI增强开发之旅吧！
EOF
            ;;
    esac
    
    # 设置权限
    chmod +x "$project_dir/.aceflow/"* 2>/dev/null || true
    
    log_success "初始化后续操作完成"
}

# 显示初始化结果
show_result() {
    local mode=$1
    local project_name=$2
    local project_dir=$3
    
    echo ""
    log_success "🎉 AceFlow v3.0 项目初始化完成!"
    echo ""
    echo -e "${CYAN}项目信息:${NC}"
    echo "  名称: $project_name"
    echo "  模式: $mode"
    echo "  目录: $project_dir"
    echo ""
    echo -e "${CYAN}重要文件:${NC}"
    echo "  📋 .clinerules               - AI Agent工作配置"
    echo "  📊 aceflow_result/           - 项目输出目录"
    echo "  ⚙️  .aceflow/                - 流程配置目录"
    echo "  📝 aceflow_result/next_steps.md - 下一步指南"
    echo ""
    echo -e "${CYAN}工具命令:${NC}" 
    echo "  🔍 ./aceflow-validate.sh     - 验证项目状态"
    echo "  📋 ./aceflow-stage.sh        - 阶段管理"
    echo "  🛠️  ./aceflow-templates.sh   - 模板管理"
    echo "  📚 SCRIPTS_README.md         - 脚本使用说明"
    echo ""
    echo -e "${GREEN}现在您可以开始使用AI Agent进行开发了！${NC}"
    echo -e "AI将按照 ${BLUE}$mode${NC} 模式的流程自动工作并保持状态连续性。"
}

# 主函数
main() {
    # 默认参数
    local mode=""
    local project_name=""
    local project_dir="$(pwd)"
    local interactive=false
    local force=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                mode="$2"
                shift 2
                ;;
            -p|--project)
                project_name="$2"
                shift 2
                ;;
            -d|--directory)
                project_dir="$2"
                shift 2
                ;;
            -i|--interactive)
                interactive=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "AceFlow v3.0.0"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示标题
    log_header
    
    # 检查依赖
    check_dependencies
    
    # 检测AI Agent环境
    if ! detect_ai_agent; then
        log_warning "建议安装支持的AI Agent以获得最佳体验"
    fi
    
    # 交互式模式或智能模式的特殊处理
    if [ "$interactive" = true ] || [ "$mode" = "smart" ]; then
        if [ -z "$project_name" ]; then
            read -p "请输入项目名称: " project_name
        fi
        
        if [ "$mode" = "smart" ]; then
            log_info "启动Smart模式智能分析..."
            mode=$(ai_interview)
        elif [ -z "$mode" ]; then
            echo "请选择流程模式:"
            echo "1) minimal  - 最简流程 (快速原型、小型项目)"
            echo "2) standard - 标准流程 (中等规模团队项目)"
            echo "3) complete - 完整流程 (企业级大型项目)"
            echo "4) smart    - 智能流程 (AI驱动自适应)"
            read -p "选择 (1-4): " mode_choice
            case $mode_choice in
                1) mode="minimal" ;;
                2) mode="standard" ;;
                3) mode="complete" ;;
                4) mode="smart"; mode=$(ai_interview) ;;
                *) log_error "无效选择"; exit 1 ;;
            esac
        fi
    fi
    
    # 参数验证
    if [ -z "$mode" ]; then
        log_error "请指定流程模式 (-m|--mode)"
        show_help
        exit 1
    fi
    
    if [[ ! "$mode" =~ ^(minimal|standard|complete|smart)$ ]]; then
        log_error "无效的流程模式: $mode"
        exit 1
    fi
    
    if [ -z "$project_name" ]; then
        project_name="AceFlow项目-$(date +%Y%m%d)"
        log_info "使用默认项目名称: $project_name"
    fi
    
    # 检查项目目录
    if [ ! -d "$project_dir" ]; then
        mkdir -p "$project_dir"
        log_info "创建项目目录: $project_dir"
    fi
    
    # 检查是否已存在配置
    if [ -f "$project_dir/.clinerules" ] && [ "$force" != true ]; then
        log_error "项目已存在AceFlow配置，使用 --force 强制覆盖"
        exit 1
    fi
    
    # 执行初始化
    cd "$project_dir"
    init_project_config "$mode" "$project_name" "$project_dir"
    post_init_setup "$mode" "$project_dir"
    
    # 显示结果
    show_result "$mode" "$project_name" "$project_dir"
}

# 执行主函数
main "$@"