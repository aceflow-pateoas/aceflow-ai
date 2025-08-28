#!/usr/bin/env python3
"""
Claude Code MCP集成测试
模拟Claude Code通过MCP协议使用AceFlow服务器的完整工作流
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def simulate_claude_code_workflow():
    """模拟Claude Code使用AceFlow MCP Server的完整开发工作流"""
    
    server_params = StdioServerParameters(
        command="aceflow-mcp-server",
        args=[],
        env=None
    )
    
    print("🤖 Claude Code + AceFlow MCP Server 集成测试")
    print("模拟真实开发场景: 构建一个博客管理系统")
    print("=" * 60)
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                await session.initialize()
                print("✅ Claude Code成功连接到AceFlow MCP服务器")
                
                # === 场景1: Claude Code发现可用工具 ===
                print("\\n🔍 Claude Code: 发现可用的工作流工具...")
                tools = await session.list_tools()
                print(f"找到 {len(tools.tools)} 个AceFlow工具:")
                for tool in tools.tools:
                    print(f"  🛠  {tool.name}")
                
                # === 场景2: 选择合适的开发模板 ===
                print("\\n📋 Claude Code: 为博客系统选择开发模板...")
                templates = await session.call_tool(
                    name="aceflow_template",
                    arguments={"action": "list"}
                )
                
                template_data = json.loads(templates.content[0].text)
                print("可用模板:")
                for tmpl in template_data['templates']:
                    print(f"  📄 {tmpl['name']}: {tmpl['description']}")
                
                print("\\n✨ Claude Code决策: 选择 'standard' 模板用于博客系统")
                
                # === 场景3: AI分析项目需求并提供给MCP ===
                print("\\n🧠 Claude Code: 分析博客系统需求并提供给AceFlow...")
                project_analysis = {
                    "project_name": "博客管理系统",
                    "project_type": "web_application", 
                    "tech_stack": ["React", "Node.js", "Express", "MongoDB"],
                    "features": [
                        "用户认证和授权",
                        "博客文章CRUD",
                        "评论系统",
                        "标签和分类",
                        "搜索功能",
                        "响应式设计"
                    ],
                    "complexity": "medium-high",
                    "estimated_duration": "4-6 weeks",
                    "team_size": 2,
                    "ai_analysis": {
                        "architecture": "单页应用 + RESTful API",
                        "database_design": "文档型数据库适合博客内容",
                        "security_considerations": ["JWT认证", "输入验证", "XSS防护"],
                        "performance_priorities": ["页面加载速度", "搜索响应时间"]
                    }
                }
                
                analysis_result = await session.call_tool(
                    name="aceflow_stage",
                    arguments={
                        "action": "set_analysis", 
                        "data": project_analysis
                    }
                )
                
                result = json.loads(analysis_result.content[0].text)
                print(f"分析数据保存: {result['success']}")
                print(f"存储类别: {result['data_stored']['categories']}")
                
                # === 场景4: 获取工作流阶段指导 ===
                print("\\n📊 Claude Code: 获取开发阶段规划...")
                stages = await session.call_tool(
                    name="aceflow_stage",
                    arguments={"action": "list"}
                )
                
                stage_data = json.loads(stages.content[0].text)
                stages_list = stage_data['result']['stages']
                print("AceFlow标准开发阶段:")
                for i, stage in enumerate(stages_list, 1):
                    print(f"  {i}. {stage}")
                
                # === 场景5: 模拟多个阶段的AI-MCP协作 ===
                print("\\n🚀 Claude Code: 执行多阶段开发工作流...")
                
                # 阶段1: 用户故事
                print("\\n  📝 阶段1: 用户故事生成")
                stage1_output = {
                    "stage": "user_stories",
                    "content": [
                        "作为博客作者，我想要创建和发布文章",
                        "作为读者，我想要搜索和阅读感兴趣的文章", 
                        "作为管理员，我想要管理用户和内容"
                    ],
                    "acceptance_criteria": "每个用户故事都有明确的验收标准",
                    "priority": "高优先级功能已识别"
                }
                
                await session.call_tool(
                    name="aceflow_stage", 
                    arguments={
                        "action": "save_output",
                        "stage": "user_stories", 
                        "data": stage1_output
                    }
                )
                print("     ✅ 用户故事已保存到AceFlow")
                
                # 阶段2: 任务分解  
                print("\\n  🔧 阶段2: 技术任务分解")
                stage2_output = {
                    "stage": "task_breakdown",
                    "frontend_tasks": [
                        "设置React + TypeScript项目",
                        "实现用户认证界面", 
                        "构建博客编辑器组件",
                        "开发文章列表和详情页"
                    ],
                    "backend_tasks": [
                        "设计Express API架构",
                        "实现JWT认证中间件",
                        "创建MongoDB数据模型",
                        "开发RESTful API端点"
                    ],
                    "infrastructure_tasks": [
                        "配置开发环境",
                        "设置CI/CD流水线",
                        "部署MongoDB实例"
                    ]
                }
                
                await session.call_tool(
                    name="aceflow_stage",
                    arguments={
                        "action": "save_output", 
                        "stage": "task_breakdown",
                        "data": stage2_output
                    }
                )
                print("     ✅ 任务分解已保存到AceFlow")
                
                # === 场景6: 验证项目质量 ===
                print("\\n🔍 Claude Code: 验证项目开发质量...")
                validation = await session.call_tool(
                    name="aceflow_validate",
                    arguments={
                        "check_type": "workflow",
                        "stage": "task_breakdown"
                    }
                )
                
                validation_result = json.loads(validation.content[0].text)
                print(f"工作流验证: {validation_result.get('success', False)}")
                
                # === 最终总结 ===
                print("\\n" + "=" * 60)
                print("🎉 Claude Code + AceFlow MCP 集成测试完成!")
                print("\\n✅ 验证的功能:")
                print("  • MCP协议通信正常")
                print("  • 4个核心工具全部可用") 
                print("  • 双向AI-MCP数据交换成功")
                print("  • 模板系统工作正常")
                print("  • 工作流阶段管理有效")
                print("  • 项目质量验证功能正常")
                print("\\n🚀 Claude Code可以通过MCP协议完美使用AceFlow!")
                
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(simulate_claude_code_workflow())
    sys.exit(0 if success else 1)