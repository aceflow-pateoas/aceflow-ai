#!/bin/bash

# AceFlow v3.0 阶段管理脚本
# AI Agent 工作流阶段控制工具

set -e

# 脚本信息
SCRIPT_NAME="aceflow-stage.sh"
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
║       AceFlow v3.0 阶段管理          ║
║      AI Agent 工作流控制工具         ║
╚══════════════════════════════════════╝${NC}"
}

# 帮助信息
show_help() {
    cat << EOF
AceFlow v3.0 阶段管理脚本

用法: $SCRIPT_NAME <command> [选项]

命令:
  status                    显示当前阶段状态
  list                     列出所有可用阶段
  next                     推进到下一阶段
  prev                     回退到上一阶段
  goto STAGE               跳转到指定阶段
  reset STAGE              重置到指定阶段 (清除后续进度)
  complete STAGE           标记指定阶段为完成
  rollback STAGE           回滚到指定阶段 (保留记录)

选项:
  -d, --directory DIR      指定项目目录 (默认: 当前目录)
  -f, --force              强制执行操作，跳过确认
  -v, --verbose            显示详细信息
  -h, --help               显示此帮助信息
  --version                显示版本信息

示例:
  $SCRIPT_NAME status
  $SCRIPT_NAME next --verbose
  $SCRIPT_NAME goto s3_testcases
  $SCRIPT_NAME reset s2_tasks_group --force

EOF
}

# 获取项目模式
get_project_mode() {
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

# 获取当前阶段
get_current_stage() {
    if [ -f "aceflow_result/current_state.json" ]; then
        python3 -c "
import json
try:
    with open('aceflow_result/current_state.json', 'r') as f:
        data = json.load(f)
    print(data.get('flow', {}).get('current_stage', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

# 获取已完成阶段
get_completed_stages() {
    if [ -f "aceflow_result/current_state.json" ]; then
        python3 -c "
import json
try:
    with open('aceflow_result/current_state.json', 'r') as f:
        data = json.load(f)
    stages = data.get('flow', {}).get('completed_stages', [])
    print(' '.join(stages))
except Exception:
    print('')
" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# 根据模式获取阶段列表
get_stage_list() {
    local mode=$1
    case $mode in
        "minimal")
            echo "analysis planning implementation validation"
            ;;
        "standard")
            echo "user_stories tasks_planning test_design implementation testing review"
            ;;
        "complete")
            echo "s1_user_story s2_tasks_group s3_testcases s4_implementation s5_test_report s6_codereview s7_demo_script s8_summary_report"
            ;;
        "smart")
            # Smart模式的阶段是动态的，从状态文件中读取
            if [ -f "aceflow_result/stage_progress.json" ]; then
                python3 -c "
import json
try:
    with open('aceflow_result/stage_progress.json', 'r') as f:
        data = json.load(f)
    stages = list(data.get('stages', {}).keys())
    print(' '.join(stages))
except Exception:
    print('analysis planning implementation validation')
" 2>/dev/null || echo "analysis planning implementation validation"
            else
                echo "analysis planning implementation validation"
            fi
            ;;
        *)
            echo ""
            ;;
    esac
}

# 获取阶段索引
get_stage_index() {
    local stage=$1
    local mode=$2
    local stages=($(get_stage_list $mode))
    
    for i in "${!stages[@]}"; do
        if [[ "${stages[$i]}" == "$stage" ]]; then
            echo $i
            return 0
        fi
    done
    echo -1
}

# 获取阶段名称（通过索引）
get_stage_name() {
    local index=$1
    local mode=$2
    local stages=($(get_stage_list $mode))
    
    if [ $index -ge 0 ] && [ $index -lt ${#stages[@]} ]; then
        echo "${stages[$index]}"
    else
        echo ""
    fi
}

# 验证阶段是否存在
validate_stage() {
    local stage=$1
    local mode=$2
    local stages=($(get_stage_list $mode))
    
    for s in "${stages[@]}"; do
        if [[ "$s" == "$stage" ]]; then
            return 0
        fi
    done
    return 1
}

# 更新项目状态
update_project_state() {
    local new_stage=$1
    local operation=$2
    
    if [ ! -f "aceflow_result/current_state.json" ]; then
        log_error "项目状态文件不存在"
        return 1
    fi
    
    # 创建临时文件进行更新
    local temp_file=$(mktemp)
    
    python3 << EOF > "$temp_file"
import json
from datetime import datetime

try:
    with open('aceflow_result/current_state.json', 'r') as f:
        data = json.load(f)
    
    # 更新当前阶段
    data['flow']['current_stage'] = '$new_stage'
    data['project']['last_updated'] = datetime.now().isoformat()
    
    # 根据操作类型更新完成阶段列表
    completed_stages = data['flow'].get('completed_stages', [])
    
    if '$operation' == 'complete':
        if '$new_stage' not in completed_stages:
            completed_stages.append('$new_stage')
    elif '$operation' == 'reset':
        # 重置时清除指定阶段之后的所有完成记录
        mode = data.get('project', {}).get('mode', 'standard')
        # 这里需要获取阶段列表并进行清理，简化实现
        pass
    
    data['flow']['completed_stages'] = completed_stages
    
    # 计算进度百分比
    mode = data.get('project', {}).get('mode', 'standard')    
    stage_counts = {
        'minimal': 4,
        'standard': 6, 
        'complete': 8,
        'smart': 4
    }
    total_stages = stage_counts.get(mode, 4)
    progress = len(completed_stages) * 100 // total_stages
    data['flow']['progress_percentage'] = progress
    
    with open('aceflow_result/current_state.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("success")
    
except Exception as e:
    print(f"error: {e}")
EOF
    
    local result=$(cat "$temp_file")
    rm -f "$temp_file"
    
    if [[ "$result" == "success" ]]; then
        return 0
    else
        log_error "状态更新失败: $result"
        return 1
    fi
}

# 更新阶段进度
update_stage_progress() {
    local stage=$1
    local status=$2
    local progress=${3:-0}
    
    if [ ! -f "aceflow_result/stage_progress.json" ]; then
        log_warning "阶段进度文件不存在，将创建新文件"
        echo '{"stages": {}}' > "aceflow_result/stage_progress.json"
    fi
    
    python3 << EOF
import json

try:
    with open('aceflow_result/stage_progress.json', 'r') as f:
        data = json.load(f)
    
    if 'stages' not in data:
        data['stages'] = {}
    
    data['stages']['$stage'] = {
        'status': '$status',
        'progress': $progress,
        'last_updated': '$(date -Iseconds)'
    }
    
    with open('aceflow_result/stage_progress.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Stage progress updated successfully")
    
except Exception as e:
    print(f"Error updating stage progress: {e}")
    exit(1)
EOF
}

# 显示阶段状态
show_status() {
    local verbose=$1
    
    log_info "检查项目状态..."
    
    # 检查项目是否已初始化
    if [ ! -f "aceflow_result/current_state.json" ]; then
        log_error "项目未初始化，请先运行 aceflow-init.sh"
        return 1
    fi
    
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    local completed_stages=($(get_completed_stages))
    
    echo ""
    echo -e "${CYAN}项目状态概览${NC}"
    echo "─────────────────────────────"
    echo -e "模式: ${BLUE}$mode${NC}"
    echo -e "当前阶段: ${GREEN}$current_stage${NC}"
    echo -e "已完成阶段: ${YELLOW}${#completed_stages[@]}${NC}"
    
    if [ "$verbose" = true ]; then
        echo ""
        echo -e "${CYAN}详细阶段信息${NC}"
        echo "─────────────────────────────"
        
        local stages=($(get_stage_list $mode))
        for stage in "${stages[@]}"; do
            local status="⭕ 待处理"
            local color=$NC
            
            # 检查是否为当前阶段
            if [[ "$stage" == "$current_stage" ]]; then
                status="🔄 进行中"
                color=$BLUE
            else
                # 检查是否已完成
                for completed in "${completed_stages[@]}"; do
                    if [[ "$completed" == "$stage" ]]; then
                        status="✅ 已完成"
                        color=$GREEN
                        break
                    fi
                done
            fi
            
            echo -e "  ${color}$stage${NC}: $status"
        done
        
        # 显示进度信息
        if [ -f "aceflow_result/stage_progress.json" ]; then
            echo ""
            echo -e "${CYAN}阶段进度详情${NC}"
            echo "─────────────────────────────"
            
            python3 << EOF
import json

try:
    with open('aceflow_result/stage_progress.json', 'r') as f:
        data = json.load(f)
    
    stages = data.get('stages', {})
    for stage_name, stage_info in stages.items():
        status = stage_info.get('status', 'unknown')
        progress = stage_info.get('progress', 0)
        last_updated = stage_info.get('last_updated', 'unknown')
        
        status_icon = {
            'pending': '⭕',
            'in_progress': '🔄', 
            'completed': '✅',
            'failed': '❌'
        }.get(status, '❓')
        
        print(f"  {status_icon} {stage_name}: {progress}% ({status})")
        if '$verbose' == 'true':
            print(f"    更新时间: {last_updated}")

except Exception as e:
    print(f"无法读取阶段进度: {e}")
EOF
        fi
    fi
    
    # 显示项目统计
    local total_stages=${#stages[@]}
    local completed_count=${#completed_stages[@]}
    local progress_percentage=0
    if [ $total_stages -gt 0 ]; then
        progress_percentage=$((completed_count * 100 / total_stages))
    fi
    
    echo ""
    echo -e "${CYAN}项目进度${NC}"
    echo "─────────────────────────────"
    echo -e "总体进度: ${BLUE}$progress_percentage%${NC} ($completed_count/$total_stages)"
    
    # 绘制进度条
    local bar_length=20
    local filled_length=$((progress_percentage * bar_length / 100))
    local bar=""
    for ((i=0; i<bar_length; i++)); do
        if [ $i -lt $filled_length ]; then
            bar+="█"
        else
            bar+="░"
        fi
    done
    echo -e "进度条: ${GREEN}$bar${NC} $progress_percentage%"
}

# 列出所有阶段
list_stages() {
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    local completed_stages=($(get_completed_stages))
    
    echo -e "${CYAN}可用阶段列表 (模式: $mode)${NC}"
    echo "─────────────────────────────"
    
    local stages=($(get_stage_list $mode))
    for i in "${!stages[@]}"; do
        local stage="${stages[$i]}"
        local status="待处理"
        local icon="⭕"
        local color=$NC
        
        if [[ "$stage" == "$current_stage" ]]; then
            status="当前阶段"
            icon="🔄"
            color=$BLUE
        else
            for completed in "${completed_stages[@]}"; do
                if [[ "$completed" == "$stage" ]]; then
                    status="已完成"
                    icon="✅"
                    color=$GREEN
                    break
                fi
            done
        fi
        
        echo -e "  ${color}$(($i + 1)). $stage${NC} - $icon $status"
    done
}

# 推进到下一阶段
goto_next_stage() {
    local force=$1
    local verbose=$2
    
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    local current_index=$(get_stage_index "$current_stage" "$mode")
    
    if [ $current_index -eq -1 ]; then
        log_error "无法确定当前阶段位置"
        return 1
    fi
    
    local next_index=$((current_index + 1))
    local next_stage=$(get_stage_name $next_index "$mode")
    
    if [ -z "$next_stage" ]; then
        log_warning "已经是最后一个阶段"
        return 0
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将从 '$current_stage' 推进到 '$next_stage'${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 标记当前阶段为完成
    update_stage_progress "$current_stage" "completed" 100
    update_project_state "$next_stage" "complete"
    update_stage_progress "$next_stage" "in_progress" 0
    
    log_success "已推进到阶段: $next_stage"
    
    if [ "$verbose" = true ]; then
        show_status true
    fi
}

# 回退到上一阶段
goto_prev_stage() {
    local force=$1
    local verbose=$2
    
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    local current_index=$(get_stage_index "$current_stage" "$mode")
    
    if [ $current_index -eq -1 ]; then
        log_error "无法确定当前阶段位置"
        return 1
    fi
    
    if [ $current_index -eq 0 ]; then
        log_warning "已经是第一个阶段"
        return 0
    fi
    
    local prev_index=$((current_index - 1))
    local prev_stage=$(get_stage_name $prev_index "$mode")
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将从 '$current_stage' 回退到 '$prev_stage'${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 更新状态
    update_stage_progress "$current_stage" "pending" 0
    update_project_state "$prev_stage" "rollback"
    update_stage_progress "$prev_stage" "in_progress" 50
    
    log_success "已回退到阶段: $prev_stage"
    
    if [ "$verbose" = true ]; then
        show_status true
    fi
}

# 跳转到指定阶段
goto_stage() {
    local target_stage=$1
    local force=$2
    local verbose=$3
    
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    
    # 验证目标阶段是否存在
    if ! validate_stage "$target_stage" "$mode"; then
        log_error "无效的阶段名称: $target_stage"
        log_info "可用阶段: $(get_stage_list $mode)"
        return 1
    fi
    
    if [[ "$target_stage" == "$current_stage" ]]; then
        log_info "已经在目标阶段: $target_stage"
        return 0
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将从 '$current_stage' 跳转到 '$target_stage'${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 更新状态
    update_stage_progress "$current_stage" "pending" 0
    update_project_state "$target_stage" "goto"
    update_stage_progress "$target_stage" "in_progress" 0
    
    log_success "已跳转到阶段: $target_stage"
    
    if [ "$verbose" = true ]; then
        show_status true
    fi
}

# 重置到指定阶段
reset_to_stage() {
    local target_stage=$1
    local force=$2
    local verbose=$3
    
    local mode=$(get_project_mode)
    local current_stage=$(get_current_stage)
    
    # 验证目标阶段
    if ! validate_stage "$target_stage" "$mode"; then
        log_error "无效的阶段名称: $target_stage"
        return 1
    fi
    
    if [ "$force" != true ]; then
        echo -e "${RED}警告: 重置操作将清除 '$target_stage' 之后的所有进度${NC}"
        echo -e "${YELLOW}即将重置到阶段: $target_stage${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 执行重置
    update_project_state "$target_stage" "reset"
    update_stage_progress "$target_stage" "in_progress" 0
    
    # 清除后续阶段的进度
    local stages=($(get_stage_list $mode))
    local target_index=$(get_stage_index "$target_stage" "$mode")
    local should_clear=false
    
    for i in "${!stages[@]}"; do
        if [ $i -gt $target_index ]; then
            update_stage_progress "${stages[$i]}" "pending" 0
        fi
    done
    
    log_success "已重置到阶段: $target_stage"
    
    if [ "$verbose" = true ]; then
        show_status true
    fi
}

# 标记阶段完成
complete_stage() {
    local target_stage=$1
    local force=$2
    local verbose=$3
    
    local mode=$(get_project_mode)
    
    # 验证目标阶段
    if ! validate_stage "$target_stage" "$mode"; then
        log_error "无效的阶段名称: $target_stage"
        return 1
    fi
    
    if [ "$force" != true ]; then
        echo -e "${YELLOW}即将标记阶段 '$target_stage' 为完成状态${NC}"
        read -p "确认继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            return 0
        fi
    fi
    
    # 标记完成
    update_stage_progress "$target_stage" "completed" 100
    
    log_success "已标记阶段完成: $target_stage"
    
    if [ "$verbose" = true ]; then
        show_status true
    fi
}

# 主函数
main() {
    local command=""
    local project_dir="$(pwd)"
    local force=false
    local verbose=false
    local stage_arg=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            status|list|next|prev)
                command="$1"
                shift
                ;;
            goto|reset|complete|rollback)
                command="$1"
                stage_arg="$2"
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
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "AceFlow Stage Manager v$VERSION"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
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
    if [ "$command" != "status" ] || [ "$verbose" = true ]; then
        log_header
    fi
    
    # 执行对应命令
    case $command in
        "status")
            show_status $verbose
            ;;
        "list")
            list_stages
            ;;
        "next")
            goto_next_stage $force $verbose
            ;;
        "prev")
            goto_prev_stage $force $verbose
            ;;
        "goto")
            if [ -z "$stage_arg" ]; then
                log_error "请指定目标阶段"
                exit 1
            fi
            goto_stage "$stage_arg" $force $verbose
            ;;
        "reset")
            if [ -z "$stage_arg" ]; then
                log_error "请指定目标阶段"
                exit 1
            fi
            reset_to_stage "$stage_arg" $force $verbose
            ;;
        "complete")
            if [ -z "$stage_arg" ]; then
                log_error "请指定目标阶段"
                exit 1
            fi
            complete_stage "$stage_arg" $force $verbose
            ;;
        "rollback")
            if [ -z "$stage_arg" ]; then
                log_error "请指定目标阶段"
                exit 1
            fi
            goto_stage "$stage_arg" $force $verbose
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