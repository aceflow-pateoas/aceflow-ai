#!/usr/bin/env python3
"""
AceFlow MCP Server 完整功能演示
"""
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def aceflow_complete_demo():
    """完整演示AceFlow MCP Server的工作流功能"""
    print("🎯 AceFlow MCP Server 完整功能演示")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="aceflow-mcp-server",
        args=[],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ MCP连接已建立")
            
            # 1. 查看可用模板
            print("\n📋 步骤1: 查看可用模板")
            result = await session.call_tool("aceflow_template", {"action": "list"})
            print(result.content[0].text)
            
            # 2. 应用complete模板
            print("\n🔧 步骤2: 应用complete模板")
            result = await session.call_tool("aceflow_template", {
                "action": "apply", 
                "template": "complete"
            })
            print(result.content[0].text)
            
            # 3. 初始化新项目
            print("\n🚀 步骤3: 初始化AceFlow项目")
            result = await session.call_tool("aceflow_init", {
                "project_name": "ai-chatbot-demo",
                "project_type": "web_app",
                "mode": "complete"
            })
            print(result.content[0].text)
            
            # 4. 查看项目阶段
            print("\n📊 步骤4: 查看项目工作流阶段")
            result = await session.call_tool("aceflow_stage", {"action": "list"})
            print(result.content[0].text)
            
            # 5. 进入下一个阶段
            print("\n📝 步骤5: 进入下一阶段")
            result = await session.call_tool("aceflow_stage", {
                "action": "next"
            })
            print(result.content[0].text)
            
            # 6. 再进入下一阶段
            print("\n🔨 步骤6: 继续进入下一阶段")
            result = await session.call_tool("aceflow_stage", {
                "action": "next"
            })
            print(result.content[0].text)
            
            # 7. 运行详细项目验证
            print("\n✅ 步骤7: 详细项目质量验证")
            result = await session.call_tool("aceflow_validate", {
                "action": "validate",
                "mode": "detailed",
                "auto_fix": True
            })
            print(result.content[0].text)
            
            # 8. 查看当前项目状态
            print("\n📈 步骤8: 查看当前项目状态")
            result = await session.call_tool("aceflow_stage", {
                "action": "status"
            })
            print(result.content[0].text)
            
            print("\n🎉 完整演示结束！")
            print("💡 AceFlow MCP Server 已成功展示:")
            print("   • 模板管理")
            print("   • 项目初始化")  
            print("   • 工作流阶段控制")
            print("   • 数据传递和状态管理")
            print("   • 项目验证和质量检查")

if __name__ == "__main__":
    try:
        asyncio.run(aceflow_complete_demo())
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")