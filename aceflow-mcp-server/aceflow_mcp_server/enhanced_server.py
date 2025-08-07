"""
Enhanced AceFlow MCP Server with AI-Human Collaborative Workflow
增强版AceFlow MCP服务器，集成AI-人协同工作流功能
"""

import click
from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

# Create enhanced FastMCP instance
mcp = FastMCP("AceFlow-Enhanced")

# Import enhanced components
def get_enhanced_tools():
    from .enhanced_tools import EnhancedAceFlowTools
    return EnhancedAceFlowTools()

def get_enhanced_resources():
    from .enhanced_resources import EnhancedAceFlowResources
    return EnhancedAceFlowResources()

def get_validation_engine():
    from .core.validation_engine import ValidationEngine, ValidationLevel
    return ValidationEngine(ValidationLevel.STANDARD)

def get_state_manager():
    from .core.enhanced_state_manager import EnhancedStateManager
    return EnhancedStateManager()

# Enhanced Tools with AI-Human Collaboration
@mcp.tool
def aceflow_stage_collaborative(
    action: str,
    stage: Optional[str] = None,
    user_input: Optional[str] = None,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """🤝 Enhanced stage management with AI-Human collaboration.
    
    This tool provides intelligent stage management with AI-human collaboration features:
    - Automatic intent recognition from user input
    - Proactive collaboration requests at key decision points
    - Task-level collaborative execution
    - Real-time progress tracking and user confirmation
    
    Use this tool when:
    - User provides natural language input about development needs
    - You need to execute stages with user collaboration
    - Managing workflow progression with user confirmation
    - Implementing task-level collaborative development
    
    Parameters:
    - action: Stage action ('status', 'next', 'execute', 'collaborative_execute')
    - stage: Optional target stage name
    - user_input: User's natural language input for intent recognition
    - auto_confirm: Skip user interaction for testing (default: False)
    
    Examples:
    - "这是PRD文档，开始开发" → aceflow_stage_collaborative(action="status", user_input="这是PRD文档，开始开发")
    - "继续下一阶段" → aceflow_stage_collaborative(action="collaborative_next")
    - "开始编码实现" → aceflow_stage_collaborative(action="collaborative_execute")
    """
    tools = get_enhanced_tools()
    return tools.aceflow_stage_collaborative(action, stage, user_input, auto_confirm)

@mcp.tool
def aceflow_task_execute(
    task_id: Optional[str] = None,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """📋 Execute tasks with collaborative confirmation.
    
    This tool enables task-level collaborative execution:
    - Parse task breakdown documents automatically
    - Execute tasks one by one with user confirmation
    - Track task progress and dependencies
    - Generate execution reports and progress updates
    
    Use this tool for:
    - Task-level collaborative development
    - Step-by-step implementation with user oversight
    - Progress tracking and confirmation
    - Detailed task execution management
    
    Parameters:
    - task_id: Specific task ID to execute (optional, will pick next available)
    - auto_confirm: Skip user confirmation for automated execution
    
    Examples:
    - "执行下一个任务" → aceflow_task_execute()
    - "执行特定任务" → aceflow_task_execute(task_id="T001")
    """
    tools = get_enhanced_tools()
    return tools.aceflow_task_execute(task_id, auto_confirm)

@mcp.tool
def aceflow_respond(
    request_id: str,
    response: str,
    user_id: str = "user"
) -> Dict[str, Any]:
    """💬 Respond to collaboration requests.
    
    This tool handles user responses to AI collaboration requests:
    - Respond to confirmation requests
    - Provide input for collaboration prompts
    - Continue or pause workflow based on user decisions
    - Maintain collaboration history and context
    
    Use this tool when:
    - User responds to AI collaboration requests
    - Confirming or rejecting AI suggestions
    - Providing input for collaborative decisions
    - Managing workflow continuation
    
    Parameters:
    - request_id: The collaboration request ID to respond to
    - response: User's response (e.g., "yes", "no", "continue", "pause")
    - user_id: User identifier (default: "user")
    
    Examples:
    - User confirms: aceflow_respond(request_id="req_123", response="yes")
    - User pauses: aceflow_respond(request_id="req_123", response="pause")
    """
    tools = get_enhanced_tools()
    return tools.aceflow_respond(request_id, response, user_id)

@mcp.tool
def aceflow_collaboration_status(
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """📊 Get collaboration status and active requests.
    
    This tool provides comprehensive collaboration status information:
    - List active collaboration requests
    - Show collaboration history and patterns
    - Display project collaboration metrics
    - Provide collaboration insights and suggestions
    
    Use this tool to:
    - Check pending collaboration requests
    - Monitor collaboration effectiveness
    - Get collaboration insights and improvements
    - Track collaboration history and patterns
    
    Parameters:
    - project_id: Optional project ID to filter results
    
    Examples:
    - "查看协作状态" → aceflow_collaboration_status()
    - "检查待处理请求" → aceflow_collaboration_status(project_id="my-project")
    """
    tools = get_enhanced_tools()
    return tools.aceflow_collaboration_status(project_id)

@mcp.tool
def aceflow_validate_quality(
    validation_level: str = "standard",
    generate_report: bool = True
) -> Dict[str, Any]:
    """🔍 Validate project quality with comprehensive checks.
    
    This tool provides multi-level quality validation:
    - Input/output validation for all stages
    - Quality scoring and improvement suggestions
    - Comprehensive quality reports
    - Stage transition validation
    
    Use this tool for:
    - Quality assurance and control
    - Pre-stage transition validation
    - Comprehensive project quality assessment
    - Quality improvement recommendations
    
    Parameters:
    - validation_level: Validation strictness ('basic', 'standard', 'strict')
    - generate_report: Whether to generate detailed quality report
    
    Examples:
    - "验证项目质量" → aceflow_validate_quality()
    - "严格质量检查" → aceflow_validate_quality(validation_level="strict")
    """
    validation_engine = get_validation_engine()
    
    try:
        # Generate comprehensive quality report
        quality_report = validation_engine.generate_quality_report()
        
        if generate_report and quality_report.get("success"):
            return {
                "success": True,
                "validation_level": validation_level,
                "quality_report": quality_report,
                "message": f"Quality validation completed with {validation_level} level"
            }
        else:
            return quality_report
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to validate project quality"
        }

# Enhanced Resources with Intelligence
@mcp.resource("aceflow://project/intelligent-state/{project_id}")
def get_intelligent_project_state(project_id: str = "default") -> str:
    """Get intelligent project state with collaboration info and recommendations."""
    resources = get_enhanced_resources()
    state_result = resources.get_intelligent_project_state(project_id)
    return json.dumps(state_result, indent=2, ensure_ascii=False)

@mcp.resource("aceflow://stage/adaptive-guide/{stage_id}")
def get_adaptive_stage_guide(stage_id: str) -> str:
    """Get adaptive stage guidance based on user patterns and project context."""
    resources = get_enhanced_resources()
    guide_result = resources.get_adaptive_stage_guide(stage_id)
    return json.dumps(guide_result, indent=2, ensure_ascii=False)

@mcp.resource("aceflow://collaboration/insights/{project_id}")
def get_collaboration_insights(project_id: str = "default") -> str:
    """Get collaboration insights and effectiveness analysis."""
    resources = get_enhanced_resources()
    insights_result = resources.get_collaboration_insights(project_id)
    return json.dumps(insights_result, indent=2, ensure_ascii=False)

@mcp.resource("aceflow://workflow/dynamic-config/{mode}")
def get_dynamic_workflow_config(mode: str) -> str:
    """Get dynamic workflow configuration optimized for project characteristics."""
    resources = get_enhanced_resources()
    config_result = resources.get_dynamic_workflow_config(mode)
    return json.dumps(config_result, indent=2, ensure_ascii=False)

@mcp.resource("aceflow://state/history/{project_id}")
def get_state_history(project_id: str = "default") -> str:
    """Get comprehensive state change history and analytics."""
    state_manager = get_state_manager()
    
    try:
        # Get state history
        history = state_manager.get_state_history(project_id, limit=20)
        
        # Get state analytics
        analytics = state_manager.get_state_analytics(project_id)
        
        result = {
            "success": True,
            "history": [
                {
                    "event_id": event.event_id,
                    "change_type": event.change_type.value,
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat(),
                    "triggered_by": event.triggered_by
                }
                for event in history
            ],
            "analytics": analytics.get("analytics", {}) if analytics.get("success") else {}
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to get state history"
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)

# Enhanced Prompts for AI-Human Collaboration
@mcp.prompt
def collaboration_workflow_assistant(
    user_input: str,
    current_stage: Optional[str] = None,
    project_context: Optional[str] = None
) -> str:
    """AI-Human Collaboration Workflow Assistant
    
    This prompt helps AI agents understand and respond to user inputs in the context
    of AceFlow collaborative workflows. It provides intelligent suggestions for
    workflow actions based on user intent and project state.
    
    Use this prompt when:
    - User provides natural language input about development needs
    - Need to understand user intent and suggest appropriate actions
    - Managing collaborative workflow interactions
    - Providing context-aware assistance
    """
    
    prompt = f"""# AceFlow AI-Human Collaboration Assistant

## Context
- Current Stage: {current_stage or 'Unknown'}
- Project Context: {project_context or 'Not provided'}
- User Input: "{user_input}"

## Your Role
You are an AI assistant specialized in AceFlow collaborative workflows. Your job is to:

1. **Understand User Intent**: Analyze the user input to determine what they want to accomplish
2. **Suggest Actions**: Recommend appropriate AceFlow tools and actions
3. **Facilitate Collaboration**: Guide the user through collaborative workflow steps
4. **Provide Context**: Explain what will happen and why

## Available Actions
- `aceflow_stage_collaborative()` - For stage management with collaboration
- `aceflow_task_execute()` - For task-level collaborative execution
- `aceflow_respond()` - For responding to collaboration requests
- `aceflow_collaboration_status()` - For checking collaboration status
- `aceflow_validate_quality()` - For quality validation

## Response Guidelines
1. First, interpret the user's intent
2. Suggest the most appropriate action
3. Explain what the action will do
4. If collaboration is needed, explain the process
5. Be proactive in suggesting next steps

## Example Responses
- If user mentions PRD/requirements: Suggest starting workflow with `aceflow_stage_collaborative()`
- If user wants to continue: Suggest advancing stages or executing tasks
- If user asks about status: Use `aceflow_collaboration_status()` or intelligent state resources
- If user wants to implement: Use `aceflow_task_execute()` for collaborative implementation

Please analyze the user input and provide helpful guidance for their AceFlow workflow needs.
"""
    
    return prompt

@mcp.prompt
def stage_collaboration_guide(
    stage_id: str,
    collaboration_style: str = "balanced",
    user_experience: str = "intermediate"
) -> str:
    """Stage-specific collaboration guidance for AI agents.
    
    This prompt provides detailed guidance for managing specific workflow stages
    with appropriate collaboration patterns based on user preferences and experience.
    """
    
    prompt = f"""# AceFlow Stage Collaboration Guide

## Stage: {stage_id}
## Collaboration Style: {collaboration_style}
## User Experience Level: {user_experience}

## Stage-Specific Guidance

### Collaboration Approach
Based on the user's experience level ({user_experience}) and preferred collaboration style ({collaboration_style}), adjust your interaction pattern:

- **Beginner**: Provide detailed explanations, ask for confirmation frequently, offer guidance
- **Intermediate**: Balance automation with key decision points, explain important choices
- **Advanced**: Minimize interruptions, focus on critical decisions, provide summaries

### Key Collaboration Points for {stage_id}
1. **Input Validation**: Ensure all required inputs are available and valid
2. **Execution Confirmation**: Confirm before starting stage execution
3. **Quality Check**: Validate outputs meet quality standards
4. **Next Steps**: Discuss progression to next stage

### Recommended Tools
- Use `aceflow_stage_collaborative()` for stage management
- Use quality validation tools before stage completion
- Leverage adaptive resources for personalized guidance

### Communication Style
- Be clear about what you're doing and why
- Ask for confirmation at key decision points
- Provide progress updates and next step suggestions
- Explain any issues or blockers clearly

Please use this guidance to provide appropriate collaboration for the {stage_id} stage.
"""
    
    return prompt

# CLI interface for enhanced server
@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--log-level", default="INFO", help="Log level")
def main(host: str, port: int, log_level: str):
    """Start the Enhanced AceFlow MCP Server with AI-Human Collaboration."""
    print("🚀 Starting Enhanced AceFlow MCP Server with AI-Human Collaboration...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Log Level: {log_level}")
    print()
    print("🤝 Enhanced Features:")
    print("   - Intelligent intent recognition")
    print("   - Proactive collaboration requests")
    print("   - Task-level collaborative execution")
    print("   - Multi-level quality validation")
    print("   - Adaptive workflow guidance")
    print("   - Comprehensive state management")
    print()
    
    # Run the FastMCP server
    mcp.run(host=host, port=port)

if __name__ == "__main__":
    main()