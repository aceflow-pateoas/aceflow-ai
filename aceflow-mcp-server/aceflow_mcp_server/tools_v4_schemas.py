"""
v4.0 Tool Schemas for MCP Server

This module defines all MCP schemas for AceFlow v4.0 tools with enhanced descriptions
that include keyword mapping for better AI tool selection.
"""

from typing import Dict, List, Any


def get_v4_tool_schemas() -> List[Dict[str, Any]]:
    """Get all v4.0 tool schemas for MCP server.

    Returns:
        List of tool schemas with enhanced descriptions
    """
    return [
        # ==================== 工作流管理工具 ====================

        {
            "name": "aceflow_v4_start_work_item",
            "description": """🚀 启动AceFlow工作流 - AI驱动的软件开发流程管理

⚡️ 触发关键词识别（当用户说以下任何表达时，使用此工具）:

📌 Bug修复类 → type='bugfix':
  • '修bug' / 'bug修复' / '修复问题' / '修复这个bug'
  • 'aceflow修复bug' / 'aceflow bugfix' / 'bugfix工作流'
  • 'fix bug' / 'fix issue' / '解决问题'

📌 功能开发类 → type='feature':
  • '新功能' / '功能开发' / '开发功能' / '开发新特性'
  • 'aceflow开发' / 'aceflow feature' / 'feature工作流'
  • 'new feature' / 'add feature' / '添加功能'

📌 代码重构类 → type='refactor':
  • '重构' / '重构代码' / '代码优化' / '优化代码结构'
  • 'aceflow重构' / 'aceflow refactor' / 'refactor工作流'
  • 'refactoring' / 'code cleanup' / '清理代码'

📌 代码审查类 → type='review':
  • '代码审查' / 'code review' / 'review代码' / '审查代码'
  • 'aceflow review' / 'review工作流'
  • 'PR review' / '审核代码'

📌 文档编写类 → type='documentation':
  • '写文档' / '文档编写' / '编写文档' / '写doc'
  • 'aceflow文档' / 'aceflow documentation' / 'documentation工作流'
  • 'write docs' / '文档化' / '补充文档'

📌 性能优化类 → type='performance':
  • '性能优化' / '优化性能' / '提升性能' / '性能改进'
  • 'aceflow性能' / 'aceflow performance' / 'performance工作流'
  • 'optimize' / 'speed up' / '加速'

📋 工作流特点:
  • bugfix: 5阶段，快速修复流程（不支持子任务）
  • feature: 5阶段，标准开发流程（支持子任务）
  • refactor: 5阶段，重构优化流程（支持子任务）
  • review: 4阶段，代码审查流程
  • documentation: 4阶段，文档编写流程
  • performance: 4阶段，性能优化流程

⚠️ 使用后续步骤:
1. 工具会返回当前阶段的任务清单
2. 完成所有任务后，调用 aceflow_v4_complete_stage() 进入下一阶段
3. 可随时调用 aceflow_v4_get_current_work_item() 查看当前状态""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["feature", "bugfix", "refactor", "review", "documentation", "performance"],
                        "description": "工作流类型。根据用户意图选择：修bug→bugfix，开发功能→feature，重构→refactor，审查→review，写文档→documentation，优化性能→performance"
                    },
                    "title": {
                        "type": "string",
                        "description": "工作项标题，简短描述工作内容"
                    },
                    "description": {
                        "type": "string",
                        "description": "工作项详细描述（可选）"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "附加元数据，如优先级、标签等（可选）"
                    }
                },
                "required": ["type", "title"]
            }
        },

        {
            "name": "aceflow_v4_get_current_work_item",
            "description": "📊 获取当前活跃的工作项。返回当前工作项的详细信息，包括当前阶段、进度、任务列表等。如果没有活跃工作项则返回None。",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },

        {
            "name": "aceflow_v4_list_work_items",
            "description": "📋 列出所有工作项。可选择性按状态筛选（pending/in_progress/completed/cancelled/blocked）。返回工作项列表，包含ID、标题、类型、状态、进度等信息。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled", "blocked"],
                        "description": "按状态筛选（可选）"
                    }
                },
                "required": []
            }
        },

        {
            "name": "aceflow_v4_complete_stage",
            "description": "✅ 完成当前阶段并推进到下一阶段。当完成当前阶段的所有任务后调用此工具。系统会自动将当前阶段标记为完成，并激活下一个阶段。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "stage_id": {
                        "type": "string",
                        "description": "当前阶段ID"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "阶段完成元数据（可选）"
                    }
                },
                "required": ["work_item_id", "stage_id"]
            }
        },

        # ==================== 任务管理工具 ====================

        {
            "name": "aceflow_v4_add_task",
            "description": "➕ 添加新任务到当前工作项。用于手动添加任务到当前阶段。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "task_title": {
                        "type": "string",
                        "description": "任务标题"
                    },
                    "task_description": {
                        "type": "string",
                        "description": "任务描述（可选）"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "任务优先级（可选，默认medium）"
                    }
                },
                "required": ["work_item_id", "task_title"]
            }
        },

        {
            "name": "aceflow_v4_update_task_status",
            "description": "🔄 更新任务状态。用于标记任务为进行中、已完成或阻塞等状态。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "blocked"],
                        "description": "新状态"
                    }
                },
                "required": ["work_item_id", "task_id", "status"]
            }
        },

        {
            "name": "aceflow_v4_suggest_tasks",
            "description": "💡 AI智能建议任务。基于当前工作项的上下文，AI自动建议应该执行的任务。返回建议的任务列表及原因。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "context": {
                        "type": "string",
                        "description": "额外上下文信息（可选）"
                    }
                },
                "required": ["work_item_id"]
            }
        },

        {
            "name": "aceflow_v4_create_tasks",
            "description": "📝 批量创建任务。从任务建议列表中批量创建任务。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "suggestions": {
                        "type": "array",
                        "description": "任务建议列表（从suggest_tasks获取）",
                        "items": {"type": "object"}
                    }
                },
                "required": ["work_item_id", "suggestions"]
            }
        },

        {
            "name": "aceflow_v4_get_task_context",
            "description": "📖 获取任务上下文。获取任务的详细信息、相关文件、依赖关系等上下文。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    }
                },
                "required": ["work_item_id", "task_id"]
            }
        },

        {
            "name": "aceflow_v4_get_pending_tasks",
            "description": "📌 获取待办任务列表。返回所有pending状态的任务。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    }
                },
                "required": ["work_item_id"]
            }
        },

        {
            "name": "aceflow_v4_get_next_task",
            "description": "⏭️ 获取下一个应该执行的任务。基于优先级和依赖关系，返回建议的下一个任务。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    }
                },
                "required": ["work_item_id"]
            }
        },

        # ==================== 代码生成工具 ====================

        {
            "name": "aceflow_v4_request_code_generation",
            "description": "🤖 AI代码骨架生成。基于需求自动生成代码骨架、类结构、函数签名等。支持多种编程语言。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "requirement": {
                        "type": "string",
                        "description": "代码需求描述"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go"],
                        "description": "编程语言"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "medium", "complex"],
                        "description": "代码复杂度（可选，默认medium）"
                    }
                },
                "required": ["work_item_id", "requirement", "language"]
            }
        },

        # ==================== 记忆系统工具 ====================

        {
            "name": "aceflow_v4_extract_memories",
            "description": "🧠 从阶段输出中自动提取记忆。AI自动从阶段输出文本中识别技术决策和经验教训。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "stage_id": {
                        "type": "string",
                        "description": "阶段ID"
                    },
                    "stage_output": {
                        "type": "string",
                        "description": "阶段输出内容"
                    }
                },
                "required": ["work_item_id", "stage_id", "stage_output"]
            }
        },

        {
            "name": "aceflow_v4_confirm_decision",
            "description": "✔️ 确认并保存技术决策。将提取的决策确认后保存到记忆系统。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "decision": {
                        "type": "object",
                        "description": "决策对象（从extract_memories获取）"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "stage_id": {
                        "type": "string",
                        "description": "阶段ID"
                    }
                },
                "required": ["decision", "work_item_id", "stage_id"]
            }
        },

        {
            "name": "aceflow_v4_confirm_lesson",
            "description": "✔️ 确认并保存经验教训。将提取的教训确认后保存到记忆系统。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lesson": {
                        "type": "object",
                        "description": "教训对象（从extract_memories获取）"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "工作项ID"
                    },
                    "stage_id": {
                        "type": "string",
                        "description": "阶段ID"
                    }
                },
                "required": ["lesson", "work_item_id", "stage_id"]
            }
        },

        {
            "name": "aceflow_v4_inject_memories",
            "description": "💉 注入记忆到模板。将相关的历史决策和教训注入到当前阶段的模板中。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "description": "包含{{project_memory}}占位符的模板"
                    },
                    "context": {
                        "type": "object",
                        "description": "注入上下文（work_item_id, stage_id等）"
                    }
                },
                "required": ["template", "context"]
            }
        },

        {
            "name": "aceflow_v4_preview_injection",
            "description": "👁️ 预览记忆注入效果。在实际注入前预览将会注入哪些记忆。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "object",
                        "description": "注入上下文"
                    }
                },
                "required": ["context"]
            }
        },

        {
            "name": "aceflow_v4_list_decisions",
            "description": "📜 列出技术决策。可按范围、标签等筛选。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["global", "project", "stage", "task"],
                        "description": "决策范围（可选）"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签筛选（可选）"
                    }
                },
                "required": []
            }
        },

        {
            "name": "aceflow_v4_list_lessons",
            "description": "📚 列出经验教训。可按类别、适用性等筛选。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["technical", "process", "communication", "testing"],
                        "description": "教训类别（可选）"
                    },
                    "applicability": {
                        "type": "string",
                        "enum": ["universal", "domain_specific", "project_specific"],
                        "description": "适用性（可选）"
                    }
                },
                "required": []
            }
        },

        {
            "name": "aceflow_v4_get_decision",
            "description": "🔍 获取单个技术决策详情。根据decision_id获取完整的决策信息。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "decision_id": {
                        "type": "string",
                        "description": "决策ID"
                    }
                },
                "required": ["decision_id"]
            }
        },

        {
            "name": "aceflow_v4_get_lesson",
            "description": "🔍 获取单个经验教训详情。根据lesson_id获取完整的教训信息。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lesson_id": {
                        "type": "string",
                        "description": "教训ID"
                    }
                },
                "required": ["lesson_id"]
            }
        }
    ]
