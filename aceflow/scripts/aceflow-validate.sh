#!/bin/bash

# AceFlow v3.0 项目验证脚本
# AI Agent 增强层合规性检查工具

set -e

# 脚本信息
SCRIPT_NAME="aceflow-validate.sh"
VERSION="3.0.0"
ACEFLOW_HOME="${ACEFLOW_HOME:-$(dirname $(dirname $(realpath $0)))}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 验证结果计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_header() {
    echo -e "${PURPLE}
╔══════════════════════════════════════╗
║       AceFlow v3.0 项目验证          ║
║      AI Agent 增强层合规检查         ║
╚══════════════════════════════════════╝${NC}"
}

# 帮助信息
show_help() {
    cat << EOF
AceFlow v3.0 项目验证脚本

用法: $SCRIPT_NAME [选项]

选项:
  -d, --directory DIR   指定项目目录 (默认: 当前目录)
  -m, --mode MODE      指定检查模式 (quick|standard|complete)
  -f, --fix            自动修复发现的问题
  -r, --report         生成详细验证报告
  -s, --silent         静默模式，只显示结果
  -h, --help           显示此帮助信息
  -v, --version        显示版本信息

检查模式:
  quick     - 快速检查 (基础文件结构)
  standard  - 标准检查 (文件结构 + 内容格式)
  complete  - 完整检查 (全面合规性验证)

示例:
  $SCRIPT_NAME --mode=complete --report
  $SCRIPT_NAME -d ./my-project --fix
  $SCRIPT_NAME --silent

EOF
}

# 检查项目基础结构
check_basic_structure() {
    log_info "检查项目基础结构..."
    
    # 检查.clinerules文件
    if [ -f ".clinerules" ]; then
        log_success "AI Agent配置文件 (.clinerules) 存在"
        
        # 检查内容完整性
        if grep -q "AceFlow" ".clinerules" && grep -q "aceflow_result" ".clinerules"; then
            log_success ".clinerules 包含必要的AceFlow配置"
        else
            log_error ".clinerules 缺少必要的AceFlow配置"
        fi
    else
        log_error "AI Agent配置文件 (.clinerules) 不存在"
        return 1
    fi
    
    # 检查aceflow_result目录
    if [ -d "aceflow_result" ]; then
        log_success "项目输出目录 (aceflow_result/) 存在"
    else
        log_error "项目输出目录 (aceflow_result/) 不存在"
    fi
    
    # 检查.aceflow配置目录
    if [ -d ".aceflow" ]; then
        log_success "配置目录 (.aceflow/) 存在"
        
        # 检查模板文件
        if [ -f ".aceflow/template.yaml" ]; then
            log_success "流程模板文件存在"
        else
            log_warning "流程模板文件不存在"
        fi
    else
        log_warning "配置目录 (.aceflow/) 不存在"
    fi
}

# 检查项目状态文件
check_state_files() {
    log_info "检查项目状态文件..."
    
    # 检查主状态文件
    if [ -f "aceflow_result/current_state.json" ]; then
        log_success "项目状态文件存在"
        
        # 验证JSON格式
        if python3 -c "import json; json.load(open('aceflow_result/current_state.json'))" 2>/dev/null; then
            log_success "项目状态文件格式正确"
            
            # 检查必要字段
            local required_fields=("project" "flow" "memory" "quality")
            for field in "${required_fields[@]}"; do
                if python3 -c "import json; data=json.load(open('aceflow_result/current_state.json')); exit(0 if '$field' in data else 1)" 2>/dev/null; then
                    log_success "状态文件包含字段: $field"
                else
                    log_error "状态文件缺少字段: $field"
                fi
            done
        else
            log_error "项目状态文件JSON格式错误"
        fi
    else
        log_error "项目状态文件不存在"
    fi
    
    # 检查阶段进度文件
    if [ -f "aceflow_result/stage_progress.json" ]; then
        log_success "阶段进度文件存在"
        
        if python3 -c "import json; json.load(open('aceflow_result/stage_progress.json'))" 2>/dev/null; then
            log_success "阶段进度文件格式正确"
        else
            log_error "阶段进度文件JSON格式错误"
        fi
    else
        log_warning "阶段进度文件不存在"
    fi
}

# 检查模式一致性
check_mode_consistency() {
    log_info "检查流程模式一致性..."
    
    local mode_from_state=""
    local mode_from_clinerules=""
    local mode_from_template=""
    
    # 从状态文件获取模式
    if [ -f "aceflow_result/current_state.json" ]; then
        mode_from_state=$(python3 -c "import json; data=json.load(open('aceflow_result/current_state.json')); print(data.get('project', {}).get('mode', ''))" 2>/dev/null || echo "")
    fi
    
    # 从.clinerules获取模式
    if [ -f ".clinerules" ]; then
        mode_from_clinerules=$(grep "AceFlow模式:" ".clinerules" | cut -d: -f2 | tr -d ' ' || echo "")
    fi
    
    # 从模板文件获取模式  
    if [ -f ".aceflow/template.yaml" ]; then
        mode_from_template=$(grep "mode:" ".aceflow/template.yaml" | head -1 | cut -d: -f2 | tr -d ' "' || echo "")
    fi
    
    # 比较模式一致性
    if [ -n "$mode_from_state" ] && [ -n "$mode_from_clinerules" ] && [ -n "$mode_from_template" ]; then
        if [ "$mode_from_state" = "$mode_from_clinerules" ] && [ "$mode_from_state" = "$mode_from_template" ]; then
            log_success "流程模式一致: $mode_from_state"
            echo "$mode_from_state"
        else
            log_error "流程模式不一致: 状态($mode_from_state) vs 配置($mode_from_clinerules) vs 模板($mode_from_template)"
            echo "inconsistent"
        fi
    else
        log_warning "无法确定流程模式一致性"
        echo "unknown"
    fi
}

# 检查输出文件合规性
check_output_compliance() {
    local mode=$1
    log_info "检查输出文件合规性 (模式: $mode)..."
    
    if [ ! -d "aceflow_result" ]; then
        log_error "输出目录不存在，跳过合规性检查"
        return 1
    fi
    
    # 检查基础文件结构
    local expected_files=()
    case $mode in
        "minimal")
            expected_files=("current_state.json" "stage_progress.json")
            ;;
        "standard")
            expected_files=("current_state.json" "stage_progress.json" "user_stories.md" "tasks_planning.md")
            ;;
        "complete")
            expected_files=("current_state.json" "stage_progress.json" "s1_user_story.md" "s2_tasks_group.md")
            ;;
        "smart")
            expected_files=("current_state.json" "stage_progress.json" "project_analysis.json")
            ;;
        *)
            log_warning "未知模式，跳过特定文件检查"
            return 0
            ;;
    esac
    
    # 检查预期文件
    for file in "${expected_files[@]}"; do
        if [ -f "aceflow_result/$file" ]; then
            log_success "预期文件存在: $file"
        else
            log_warning "预期文件不存在: $file"
        fi
    done
    
    # 检查文件命名规范
    local non_compliant_files=()
    while IFS= read -r -d '' file; do
        local basename=$(basename "$file")
        # AceFlow命名规范: 只允许字母、数字、下划线、连字符和点
        if [[ ! "$basename" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
            non_compliant_files+=("$basename")
        fi
    done < <(find aceflow_result -type f -print0 2>/dev/null)
    
    if [ ${#non_compliant_files[@]} -eq 0 ]; then
        log_success "所有文件命名符合规范"
    else
        log_warning "发现不符合命名规范的文件: ${non_compliant_files[*]}"
    fi
}

# 检查记忆系统状态
check_memory_system() {
    log_info "检查记忆系统状态..." 
    
    # 检查记忆状态文件
    if [ -f "aceflow_result/memory_state.json" ]; then
        log_success "记忆状态文件存在"
        
        if python3 -c "import json; json.load(open('aceflow_result/memory_state.json'))" 2>/dev/null; then
            log_success "记忆状态文件格式正确"
        else
            log_error "记忆状态文件JSON格式错误"
        fi
    else
        log_warning "记忆状态文件不存在 (首次运行时正常)"
    fi
    
    # 检查记忆持久化配置
    if [ -f "aceflow_result/current_state.json" ]; then
        local memory_enabled=$(python3 -c "import json; data=json.load(open('aceflow_result/current_state.json')); print(data.get('memory', {}).get('enabled', False))" 2>/dev/null || echo "false")
        
        if [ "$memory_enabled" = "True" ]; then
            log_success "记忆系统已启用"
        else
            log_warning "记忆系统未启用"
        fi
    fi
    
    # 检查PATEOAS集成
    if python3 -c "import aceflow.pateoas" 2>/dev/null; then
        log_success "PATEOAS记忆系统集成正常"
    else
        log_warning "PATEOAS记忆系统未正确集成"
    fi
}

# 检查质量标准
check_quality_standards() {
    local mode=$1
    log_info "检查质量标准 (模式: $mode)..."
    
    # 获取质量配置
    local quality_config=""
    if [ -f ".aceflow/template.yaml" ]; then
        # 检查是否定义了质量标准
        if grep -q "quality" ".aceflow/template.yaml"; then
            log_success "模板定义了质量标准"
            quality_config="defined"
        else
            log_warning "模板未定义质量标准"
            quality_config="undefined"
        fi
    fi
    
    # 根据模式检查特定质量要求
    case $mode in
        "complete")
            # Complete模式需要严格的质量标准
            if [ -f "aceflow_result/s6_codereview.md" ]; then
                log_success "Complete模式包含代码评审文档"
            else
                log_warning "Complete模式缺少代码评审文档"
            fi
            ;;
        "smart")
            # Smart模式需要质量指标跟踪
            if [ -f "aceflow_result/project_analysis.json" ]; then
                local has_quality_metrics=$(python3 -c "
import json
try:
    data=json.load(open('aceflow_result/project_analysis.json'))
    print('yes' if 'quality' in str(data) else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")
                
                if [ "$has_quality_metrics" = "yes" ]; then
                    log_success "Smart模式包含质量指标跟踪"
                else
                    log_warning "Smart模式缺少质量指标跟踪"
                fi
            fi
            ;;
    esac
}

# 生成验证报告
generate_report() {
    local project_dir=$1
    local mode=$2
    local timestamp=$(date -Iseconds)
    local report_file="aceflow_result/validation_report_$(date +%Y%m%d_%H%M%S).json"
    
    log_info "生成验证报告..."
    
    # 收集系统信息
    local git_status="unknown"
    if command -v git &> /dev/null && git rev-parse --is-inside-work-tree &> /dev/null; then
        git_status="$(git status --porcelain | wc -l) files changed"
    fi
    
    # 生成报告
    cat > "$report_file" << EOF
{
  "validation": {
    "timestamp": "$timestamp",
    "script_version": "$VERSION",
    "project_directory": "$project_dir",
    "detected_mode": "$mode"
  },
  "results": {
    "total_checks": $TOTAL_CHECKS,
    "passed_checks": $PASSED_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "warning_checks": $WARNING_CHECKS,
    "success_rate": $(echo "scale=2; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l 2>/dev/null || echo "0.00")
  },
  "environment": {
    "aceflow_home": "$ACEFLOW_HOME",
    "python_version": "$(python3 --version 2>/dev/null || echo 'Not installed')",
    "git_status": "$git_status",
    "working_directory": "$(pwd)"
  },
  "recommendations": [
$([ $FAILED_CHECKS -gt 0 ] && echo '    "修复失败的检查项以确保项目合规性",' || echo '')
$([ $WARNING_CHECKS -gt 0 ] && echo '    "关注警告项以提高项目质量",' || echo '')
$([ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ] && echo '    "项目验证通过，可以正常使用AceFlow功能"' || echo '    "建议解决发现的问题后重新验证"')
  ]
}
EOF
    
    log_success "验证报告已生成: $report_file"
}

# 自动修复功能
auto_fix_issues() {
    log_info "尝试自动修复发现的问题..."
    
    local fixed_count=0
    
    # 修复缺失的目录
    if [ ! -d "aceflow_result" ]; then
        mkdir -p "aceflow_result"
        log_success "已创建 aceflow_result/ 目录"
        ((fixed_count++))
    fi
    
    if [ ! -d ".aceflow" ]; then
        mkdir -p ".aceflow"
        log_success "已创建 .aceflow/ 配置目录"
        ((fixed_count++))
    fi
    
    # 修复缺失的基础状态文件
    if [ ! -f "aceflow_result/current_state.json" ]; then
        cat > "aceflow_result/current_state.json" << EOF
{
  "project": {
    "name": "修复的项目",
    "mode": "standard",
    "created_at": "$(date -Iseconds)",
    "last_updated": "$(date -Iseconds)",
    "version": "3.0.0"
  },
  "flow": {
    "current_stage": "initialized",
    "completed_stages": [],
    "progress_percentage": 0
  },
  "memory": {
    "enabled": true,
    "last_session": "$(date -Iseconds)",
    "context_preserved": false
  },
  "quality": {
    "standards_applied": false,
    "compliance_checked": true,
    "last_validation": "$(date -Iseconds)"
  }
}
EOF
        log_success "已创建基础项目状态文件"
        ((fixed_count++))
    fi
    
    # 修复缺失的.clinerules文件
    if [ ! -f ".clinerules" ]; then
        cat > ".clinerules" << EOF
# AceFlow v3.0 - AI Agent 集成配置
# 自动修复生成

## 工作模式配置
AceFlow模式: standard
输出目录: aceflow_result/
配置目录: .aceflow/

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
EOF
        log_success "已创建基础 .clinerules 配置文件"
        ((fixed_count++))
    fi
    
    if [ $fixed_count -gt 0 ]; then
        log_success "自动修复完成，共修复 $fixed_count 个问题"
    else
        log_info "没有发现可自动修复的问题"
    fi
}

# 显示验证结果摘要
show_summary() {
    local mode=$1
    
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════╗"
    echo -e "║           验证结果摘要               ║"
    echo -e "╚══════════════════════════════════════╝${NC}"
    echo ""
    
    # 结果统计
    echo -e "${CYAN}检查统计:${NC}"
    echo "  总检查项: $TOTAL_CHECKS"
    echo -e "  通过: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "  失败: ${RED}$FAILED_CHECKS${NC}"
    echo -e "  警告: ${YELLOW}$WARNING_CHECKS${NC}"
    
    # 成功率计算
    local success_rate=0
    if [ $TOTAL_CHECKS -gt 0 ]; then
        success_rate=$(echo "scale=1; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l 2>/dev/null || echo "0.0")
    fi
    echo -e "  成功率: ${BLUE}$success_rate%${NC}"
    echo ""
    
    # 总体评估
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
            echo -e "${GREEN}✅ 项目验证完全通过！${NC}"
            echo "您可以安全地使用AceFlow的所有功能。"
        else
            echo -e "${YELLOW}⚠️  项目验证基本通过，但有警告项${NC}"
            echo "建议查看警告信息并考虑改进。"
        fi
    else
        echo -e "${RED}❌ 项目验证失败${NC}"
        echo "请修复失败的检查项后重新验证。"
    fi
    
    echo ""
    echo -e "${CYAN}模式信息:${NC} $mode"
    echo -e "${CYAN}项目目录:${NC} $(pwd)"
}

# 主函数
main() {
    # 默认参数
    local project_dir="$(pwd)"
    local check_mode="standard"
    local auto_fix=false
    local generate_report_flag=false
    local silent_mode=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--directory)
                project_dir="$2"
                shift 2
                ;;
            -m|--mode)
                check_mode="$2"
                shift 2
                ;;
            -f|--fix)
                auto_fix=true
                shift
                ;;
            -r|--report)
                generate_report_flag=true
                shift
                ;;
            -s|--silent)
                silent_mode=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "AceFlow Validator v$VERSION"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证检查模式
    if [[ ! "$check_mode" =~ ^(quick|standard|complete)$ ]]; then
        log_error "无效的检查模式: $check_mode"
        exit 1
    fi
    
    # 切换到项目目录
    if [ ! -d "$project_dir" ]; then
        log_error "项目目录不存在: $project_dir"
        exit 1
    fi
    
    cd "$project_dir"
    
    # 显示标题 (非静默模式)
    if [ "$silent_mode" != true ]; then
        log_header
        echo -e "${CYAN}检查目录:${NC} $project_dir"
        echo -e "${CYAN}检查模式:${NC} $check_mode"
        echo ""
    fi
    
    # 执行基础检查
    check_basic_structure
    
    # 根据检查模式执行相应的验证
    case $check_mode in
        "quick")
            # 快速检查只验证基础结构
            ;;
        "standard"|"complete")
            check_state_files
            local detected_mode=$(check_mode_consistency)
            
            if [ "$detected_mode" != "unknown" ] && [ "$detected_mode" != "inconsistent" ]; then
                check_output_compliance "$detected_mode"
                check_quality_standards "$detected_mode"
            fi
            
            if [ "$check_mode" = "complete" ]; then
                check_memory_system
            fi
            ;;
    esac
    
    # 自动修复
    if [ "$auto_fix" = true ] && [ $FAILED_CHECKS -gt 0 ]; then
        auto_fix_issues
    fi
    
    # 生成报告
    if [ "$generate_report_flag" = true ]; then
        local detected_mode=$(check_mode_consistency)
        generate_report "$project_dir" "$detected_mode"
    fi
    
    # 显示摘要
    if [ "$silent_mode" != true ]; then
        local detected_mode=$(check_mode_consistency)
        show_summary "$detected_mode"
    fi
    
    # 设置退出码
    if [ $FAILED_CHECKS -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# 执行主函数
main "$@"