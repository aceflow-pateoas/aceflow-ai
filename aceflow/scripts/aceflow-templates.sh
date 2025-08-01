#!/bin/bash

# AceFlow v3.0 模板管理脚本
# AI Agent 增强层模板系统工具

set -e

# 脚本信息
SCRIPT_NAME="aceflow-templates.sh"
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
║       AceFlow v3.0 模板管理          ║
║      AI Agent 增强层模板工具         ║
╚══════════════════════════════════════╝${NC}"
}

# 帮助信息
show_help() {
    cat << EOF
AceFlow v3.0 模板管理脚本

用法: $SCRIPT_NAME <command> [选项]

命令:
  list                     列出所有可用模板
  info MODE               显示指定模式的详细信息
  switch MODE             切换项目到指定模式
  backup                  备份当前模板配置
  restore BACKUP          从备份恢复模板配置
  validate MODE           验证模板配置
  customize MODE          自定义模板配置
  export MODE FILE        导出模板配置到文件
  import FILE             从文件导入模板配置

选项:
  -d, --directory DIR     指定项目目录 (默认: 当前目录)
  -f, --force             强制执行操作，跳过确认
  -v, --verbose           显示详细信息
  -o, --output DIR        指定输出目录
  -h, --help              显示此帮助信息
  --version               显示版本信息

模式类型:
  minimal     - 最简流程模式
  standard    - 标准流程模式
  complete    - 完整流程模式
  smart       - 智能自适应模式

示例:
  $SCRIPT_NAME list
  $SCRIPT_NAME info smart --verbose
  $SCRIPT_NAME switch complete --force
  $SCRIPT_NAME customize standard
  $SCRIPT_NAME export smart my-template.yaml

EOF
}

# 获取模板目录
get_template_dir() {
    echo "$ACEFLOW_HOME/templates"
}

# 验证模式是否存在
validate_mode() {
    local mode=$1
    local template_dir=$(get_template_dir)
    
    if [ -d "$template_dir/$mode" ]; then
        return 0
    else
        return 1
    fi
}

# 获取当前项目模式
get_current_mode() {
    if [ -f "aceflow_result/current_state.json" ]; then
        python3 -c "
import json
try:
    with open('aceflow_result/current_state.json', 'r') as f:
        data = json.load(f)
    print(data.get('project', {}).get('mode', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

# 列出所有可用模板
list_templates() {
    local verbose=$1
    local template_dir=$(get_template_dir)
    
    log_info "扫描模板目录: $template_dir"
    
    if [ ! -d "$template_dir" ]; then
        log_error "模板目录不存在: $template_dir"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}可用模板列表${NC}"
    echo "─────────────────────────────"
    
    local current_mode=$(get_current_mode)
    local template_count=0
    
    for mode_dir in "$template_dir"/*; do
        if [ -d "$mode_dir" ]; then
            local mode=$(basename "$mode_dir")
            local status=""
            local icon="📋"
            
            # 跳过特殊目录
            case $mode in
                "document_templates"|"s1_"*|"s2_"*|"s3_"*|"s4_"*|"s5_"*|"s6_"*|"s7_"*|"s8_"*)
                    continue
                    ;;
            esac
            
            if [[ "$mode" == "$current_mode" ]]; then
                status=" ${GREEN}(当前使用)${NC}"
                icon="📌"
            fi
            
            echo -e "  $icon ${BLUE}$mode${NC}$status"
            ((template_count++))
            
            if [ "$verbose" = true ]; then
                # 显示模板详细信息
                local template_file="$mode_dir/template.yaml"
                local readme_file="$mode_dir/README.md"
                
                if [ -f "$template_file" ]; then
                    local description=$(grep -E "^\s*description:" "$template_file" | cut -d: -f2- | sed 's/^[[:space:]]*//' | tr -d '"' 2>/dev/null || echo "无描述")
                    echo -e "    📝 描述: $description"
                fi
                
                if [ -f "$readme_file" ]; then
                    local first_line=$(head -n1 "$readme_file" | sed 's/^#[[:space:]]*//' 2>/dev/null || echo "")
                    if [ -n "$first_line" ]; then
                        echo -e "    📖 说明: $first_line"
                    fi
                fi
                
                # 显示文件统计
                local file_count=$(find "$mode_dir" -type f | wc -l)
                echo -e "    📁 文件数: $file_count"
                echo ""
            fi
        fi
    done
    
    if [ $template_count -eq 0 ]; then
        log_warning "未找到可用模板"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}模板统计${NC}"
    echo "─────────────────────────────"
    echo "可用模板数: $template_count"
    echo "当前模式: $current_mode"
}

# 显示模板详细信息
show_template_info() {
    local mode=$1
    local verbose=$2
    local template_dir=$(get_template_dir)
    
    if ! validate_mode "$mode"; then
        log_error "模板不存在: $mode"
        return 1
    fi
    
    local mode_dir="$template_dir/$mode"
    local template_file="$mode_dir/template.yaml"
    local readme_file="$mode_dir/README.md"
    
    echo ""
    echo -e "${CYAN}模板信息: $mode${NC}"
    echo "═══════════════════════════════════"
    
    # 基础信息
    if [ -f "$template_file" ]; then
        echo -e "${YELLOW}📋 配置信息${NC}"
        echo "─────────────────────────────"
        
        # 提取关键信息
        local description=$(grep -E "^\s*description:" "$template_file" | cut -d: -f2- | sed 's/^[[:space:]]*//' | tr -d '"' 2>/dev/null || echo "无描述")
        local team_size=$(grep -E "^\s*team_size:" "$template_file" | cut -d: -f2- | sed 's/^[[:space:]]*//' | tr -d '"' 2>/dev/null || echo "未指定")
        local duration=$(grep -E "^\s*estimated_duration:" "$template_file" | cut -d: -f2- | sed 's/^[[:space:]]*//' | tr -d '"' 2>/dev/null || echo "未指定")
        
        echo "描述: $description"
        echo "团队规模: $team_size"
        echo "预估时长: $duration"
        echo ""
    fi
    
    # README信息
    if [ -f "$readme_file" ]; then
        echo -e "${YELLOW}📖 使用说明${NC}"
        echo "─────────────────────────────"
        
        if [ "$verbose" = true ]; then
            # 显示完整README
            cat "$readme_file"
        else
            # 显示前几行
            head -n 10 "$readme_file"
            local total_lines=$(wc -l < "$readme_file")
            if [ $total_lines -gt 10 ]; then
                echo ""
                echo -e "${GRAY}... (还有 $((total_lines - 10)) 行，使用 --verbose 查看完整内容)${NC}"
            fi
        fi
        echo ""
    fi
    
    # 文件结构
    echo -e "${YELLOW}📁 文件结构${NC}"
    echo "─────────────────────────────"
    
    if command -v tree >/dev/null 2>&1; then
        tree "$mode_dir" -I '__pycache__|*.pyc'
    else
        find "$mode_dir" -type f | sed "s|$mode_dir/||" | sort | sed 's/^/  /'
    fi
    
    echo ""
    
    # 模板统计
    echo -e "${YELLOW}📊 统计信息${NC}"
    echo "─────────────────────────────"
    local file_count=$(find "$mode_dir" -type f | wc -l)
    local yaml_count=$(find "$mode_dir" -name "*.yaml" -o -name "*.yml" | wc -l)
    local md_count=$(find "$mode_dir" -name "*.md" | wc -l)
    
    echo "总文件数: $file_count"
    echo "YAML配置: $yaml_count"
    echo "Markdown文档: $md_count"
    
    # 最后修改时间
    local last_modified=$(find "$mode_dir" -type f -exec stat -c %Y {} \; | sort -n | tail -n1 | xargs -I {} date -d @{} "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知")
    echo "最后修改: $last_modified"
}

# 切换项目模式
switch_mode() {
    local target_mode=$1
    local force=$2
    local verbose=$3
    
    if ! validate_mode "$target_mode"; then
        log_error "模板不存在: $target_mode"
        return 1
    fi
    
    local current_mode=$(get_current_mode)
    
    if [[ "$target_mode" == "$current_mode" ]]; then
        log_info "项目已经使用模式: $target_mode"
        return 0
    fi
    
    # 检查项目是否已初始化
    if [ ! -f "aceflow_result/current_state.json" ]; then
        log_error "项目未初始化，请先运行 aceflow-init.sh"
        return 1
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将从 '$current_mode' 切换到 '$target_mode' 模式${NC}"
        echo -e "${RED}警告: 这将重置项目状态和进度${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    log_info "备份当前配置..."
    backup_current_config
    
    log_info "应用新模板..."
    local template_dir=$(get_template_dir)
    
    # 清理并重新创建配置目录
    rm -rf ".aceflow"
    mkdir -p ".aceflow"
    
    # 复制新模板
    cp -r "$template_dir/$target_mode"/* ".aceflow/"
    
    # 更新项目状态
    update_project_mode "$target_mode"
    
    # 重新生成.clinerules
    generate_clinerules "$target_mode"
    
    log_success "已切换到模式: $target_mode"
    
    if [ "$verbose" = true ]; then
        show_template_info "$target_mode" false
    fi
}

# 备份当前配置
backup_current_config() {
    local backup_dir="aceflow_result/backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="config_backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # 备份配置目录
    if [ -d ".aceflow" ]; then
        cp -r ".aceflow" "$backup_dir/$backup_name"
        log_success "配置已备份到: $backup_dir/$backup_name"
    fi
    
    # 备份状态文件
    if [ -f "aceflow_result/current_state.json" ]; then
        cp "aceflow_result/current_state.json" "$backup_dir/${backup_name}_state.json"
    fi
    
    if [ -f ".clinerules" ]; then
        cp ".clinerules" "$backup_dir/${backup_name}_clinerules"
    fi
}

# 从备份恢复配置
restore_from_backup() {
    local backup_name=$1
    local force=$2
    
    local backup_dir="aceflow_result/backups"
    local backup_path="$backup_dir/$backup_name"
    
    if [ ! -d "$backup_path" ]; then
        log_error "备份不存在: $backup_name"
        log_info "可用备份:"
        ls -1 "$backup_dir" 2>/dev/null | grep -E "^config_backup_" | sed 's/^/  /' || echo "  (无备份)"
        return 1
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将从备份恢复配置: $backup_name${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 恢复配置目录
    rm -rf ".aceflow"
    cp -r "$backup_path" ".aceflow"
    
    # 恢复状态文件
    if [ -f "$backup_dir/${backup_name}_state.json" ]; then
        cp "$backup_dir/${backup_name}_state.json" "aceflow_result/current_state.json"
    fi
    
    # 恢复.clinerules
    if [ -f "$backup_dir/${backup_name}_clinerules" ]; then
        cp "$backup_dir/${backup_name}_clinerules" ".clinerules"
    fi
    
    log_success "配置已从备份恢复: $backup_name"
}

# 验证模板配置
validate_template() {
    local mode=$1
    local template_dir=$(get_template_dir)
    
    if ! validate_mode "$mode"; then
        log_error "模板不存在: $mode"
        return 1
    fi
    
    local mode_dir="$template_dir/$mode"
    local template_file="$mode_dir/template.yaml"
    local readme_file="$mode_dir/README.md"
    
    local validation_errors=0
    
    echo -e "${CYAN}验证模板: $mode${NC}"
    echo "─────────────────────────────"
    
    # 检查必需文件
    if [ -f "$template_file" ]; then
        log_success "模板配置文件存在"
        
        # 验证YAML格式
        if python3 -c "import yaml; yaml.safe_load(open('$template_file'))" 2>/dev/null; then
            log_success "YAML格式正确"
        else
            log_error "YAML格式错误"
            ((validation_errors++))
        fi
        
        # 检查必需字段
        local required_fields=("project" "flow")
        for field in "${required_fields[@]}"; do
            if grep -q "^$field:" "$template_file"; then
                log_success "包含必需字段: $field"
            else
                log_error "缺少必需字段: $field"
                ((validation_errors++))
            fi
        done
    else
        log_error "模板配置文件不存在: template.yaml"
        ((validation_errors++))
    fi
    
    if [ -f "$readme_file" ]; then
        log_success "README文档存在"
    else
        log_warning "README文档不存在"
    fi
    
    # 验证模式特定要求
    case $mode in
        "complete")
            local stage_files=("s1_user_story" "s2_tasks_group" "s3_testcases" "s4_implementation" "s5_test_report" "s6_codereview" "s7_demo_script" "s8_summary_report")
            for stage in "${stage_files[@]}"; do
                if grep -q "$stage" "$template_file" 2>/dev/null; then
                    log_success "包含完整模式阶段: $stage"
                else
                    log_warning "完整模式可能缺少阶段: $stage"
                fi
            done
            ;;
        "smart")
            if grep -q "smart_features" "$template_file" 2>/dev/null; then
                log_success "包含智能特性配置"
            else
                log_error "智能模式缺少智能特性配置"
                ((validation_errors++))
            fi
            ;;
    esac
    
    echo ""
    if [ $validation_errors -eq 0 ]; then
        log_success "模板验证通过"
        return 0
    else
        log_error "模板验证失败，发现 $validation_errors 个错误"
        return 1
    fi
}

# 自定义模板配置
customize_template() {
    local mode=$1
    local template_dir=$(get_template_dir)
    
    if ! validate_mode "$mode"; then
        log_error "模板不存在: $mode"
        return 1
    fi
    
    echo -e "${CYAN}自定义模板配置: $mode${NC}"
    echo "─────────────────────────────"
    
    # 创建自定义配置目录
    local custom_dir=".aceflow/custom"
    mkdir -p "$custom_dir"
    
    # 复制原始模板
    cp -r "$template_dir/$mode"/* "$custom_dir/"
    
    log_info "模板已复制到自定义目录: $custom_dir"
    echo ""
    
    # 提供自定义选项
    echo "可自定义选项:"
    echo "1. 修改项目信息 (项目名称、描述等)"
    echo "2. 调整质量标准 (覆盖率、通过率等)"
    echo "3. 自定义阶段配置 (添加或删除阶段)"
    echo "4. 修改输出格式 (文档模板、命名规则等)"
    echo "5. 集成工具配置 (CI/CD、测试工具等)"
    echo ""
    
    read -p "选择要自定义的选项 (1-5): " custom_choice
    
    case $custom_choice in
        1)
            customize_project_info "$custom_dir"
            ;;
        2)
            customize_quality_standards "$custom_dir"
            ;;
        3)
            customize_stage_config "$custom_dir"
            ;;
        4)
            customize_output_format "$custom_dir"
            ;;
        5)
            customize_tool_integration "$custom_dir"
            ;;
        *)
            log_info "无效选择，打开编辑器进行手动自定义"
            ${EDITOR:-nano} "$custom_dir/template.yaml"
            ;;
    esac
    
    log_success "自定义配置完成"
    echo "自定义文件位置: $custom_dir"
    echo "使用 'aceflow-templates.sh import $custom_dir/template.yaml' 应用自定义配置"
}

# 自定义项目信息
customize_project_info() {
    local custom_dir=$1
    local template_file="$custom_dir/template.yaml"
    
    echo "自定义项目信息:"
    
    read -p "项目名称: " project_name
    read -p "项目描述: " project_desc
    read -p "团队规模: " team_size
    read -p "预估时长: " duration
    
    # 使用Python更新YAML文件
    python3 << EOF
import yaml

try:
    with open('$template_file', 'r') as f:
        data = yaml.safe_load(f)
    
    if 'project' not in data:
        data['project'] = {}
    
    data['project']['name'] = '$project_name' if '$project_name' else data['project'].get('name', '新建项目')
    data['project']['description'] = '$project_desc' if '$project_desc' else data['project'].get('description', '项目描述')
    data['project']['team_size'] = '$team_size' if '$team_size' else data['project'].get('team_size', '小团队')
    data['project']['estimated_duration'] = '$duration' if '$duration' else data['project'].get('estimated_duration', '2-4周')
    
    with open('$template_file', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    print("项目信息已更新")
    
except Exception as e:
    print(f"更新失败: {e}")
EOF
}

# 导出模板配置
export_template() {
    local mode=$1
    local output_file=$2
    local template_dir=$(get_template_dir)
    
    if ! validate_mode "$mode"; then
        log_error "模板不存在: $mode"
        return 1
    fi
    
    local template_file="$template_dir/$mode/template.yaml"
    
    if [ ! -f "$template_file" ]; then
        log_error "模板配置文件不存在"
        return 1
    fi
    
    # 复制模板文件
    cp "$template_file" "$output_file"
    
    log_success "模板已导出到: $output_file"
}

# 导入模板配置
import_template() {
    local import_file=$1
    local force=$2
    
    if [ ! -f "$import_file" ]; then
        log_error "导入文件不存在: $import_file"
        return 1
    fi
    
    # 验证导入文件格式
    if ! python3 -c "import yaml; yaml.safe_load(open('$import_file'))" 2>/dev/null; then
        log_error "导入文件格式错误"
        return 1
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将导入模板配置: $import_file${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 备份当前配置
    backup_current_config
    
    # 应用导入的配置
    mkdir -p ".aceflow"
    cp "$import_file" ".aceflow/template.yaml"
    
    # 更新项目状态
    local imported_mode=$(python3 -c "
import yaml
try:
    with open('$import_file', 'r') as f:
        data = yaml.safe_load(f)
    print(data.get('flow', {}).get('mode', 'standard'))
except Exception:
    print('standard')
" 2>/dev/null || echo "standard")
    
    update_project_mode "$imported_mode"
    generate_clinerules "$imported_mode"
    
    log_success "模板配置已导入"
}

# 更新项目模式
update_project_mode() {
    local new_mode=$1
    
    if [ -f "aceflow_result/current_state.json" ]; then
        python3 << EOF
import json
from datetime import datetime

try:
    with open('aceflow_result/current_state.json', 'r') as f:
        data = json.load(f)
    
    data['project']['mode'] = '$new_mode'
    data['project']['last_updated'] = datetime.now().isoformat()
    data['flow']['current_stage'] = 'initialized'
    data['flow']['completed_stages'] = []
    data['flow']['progress_percentage'] = 0
    
    with open('aceflow_result/current_state.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Project mode updated successfully")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOF
    fi
}

# 生成.clinerules文件
generate_clinerules() {
    local mode=$1
    
    cat > ".clinerules" << EOF
# AceFlow v3.0 - AI Agent 集成配置
# 模式: $mode

## 工作模式配置
AceFlow模式: $mode
输出目录: aceflow_result/
配置目录: .aceflow/
模板文件: .aceflow/template.yaml

## 核心工作原则
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 工具集成命令
- aceflow-validate.sh: 验证项目状态和合规性
- aceflow-stage.sh: 管理项目阶段和进度
- aceflow-templates.sh: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
EOF
}

# 主函数
main() {
    local command=""
    local project_dir="$(pwd)"
    local force=false
    local verbose=false
    local output_dir=""
    local mode_arg=""
    local file_arg=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            list|backup)
                command="$1"
                shift
                ;;
            info|switch|validate|customize|export)
                command="$1"
                mode_arg="$2"
                shift 2
                ;;
            restore|import)
                command="$1"
                file_arg="$2"
                shift 2
                ;;
            -d|--directory)
                project_dir="$2"
                shift 2
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "AceFlow Template Manager v$VERSION"
                exit 0
                ;;
            *)
                # 处理export命令的第二个参数
                if [[ "$command" == "export" && -z "$file_arg" ]]; then
                    file_arg="$1"
                    shift
                else
                    log_error "未知参数: $1"
                    show_help
                    exit 1
                fi
                ;;
        esac
    done
    
    # 验证命令
    if [ -z "$command" ]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    # 切换到项目目录
    if [ ! -d "$project_dir" ]; then
        log_error "项目目录不存在: $project_dir"
        exit 1
    fi
    
    cd "$project_dir"
    
    # 显示标题
    log_header
    
    # 执行对应命令
    case $command in
        "list")
            list_templates $verbose
            ;;
        "info")
            if [ -z "$mode_arg" ]; then
                log_error "请指定模式名称"
                exit 1
            fi
            show_template_info "$mode_arg" $verbose
            ;;
        "switch")
            if [ -z "$mode_arg" ]; then
                log_error "请指定目标模式"
                exit 1
            fi
            switch_mode "$mode_arg" $force $verbose
            ;;
        "backup")
            backup_current_config
            ;;
        "restore")
            if [ -z "$file_arg" ]; then
                log_error "请指定备份名称"
                exit 1
            fi
            restore_from_backup "$file_arg" $force
            ;;
        "validate")
            if [ -z "$mode_arg" ]; then
                log_error "请指定模式名称"
                exit 1
            fi
            validate_template "$mode_arg"
            ;;
        "customize")
            if [ -z "$mode_arg" ]; then
                log_error "请指定模式名称"
                exit 1
            fi
            customize_template "$mode_arg"
            ;;
        "export")
            if [ -z "$mode_arg" ] || [ -z "$file_arg" ]; then
                log_error "请指定模式名称和输出文件"
                exit 1
            fi
            export_template "$mode_arg" "$file_arg"
            ;;
        "import")
            if [ -z "$file_arg" ]; then
                log_error "请指定导入文件"
                exit 1
            fi
            import_template "$file_arg" $force
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"