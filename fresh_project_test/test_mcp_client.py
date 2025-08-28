#!/usr/bin/env python3
"""
MCP客户端测试脚本
用于测试AceFlow MCP服务器的真实MCP协议通信
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """测试MCP服务器功能"""
    
    # MCP服务器参数
    server_params = StdioServerParameters(
        command="aceflow-mcp-server",
        args=[],
        env=None
    )
    
    print("🚀 启动MCP服务器连接...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # 初始化连接
                await session.initialize()
                print("✅ MCP连接初始化成功")
                
                # 1. 列出可用工具
                print("\n=== 📋 步骤1: 列出可用的MCP工具 ===")
                tools_result = await session.list_tools()
                print(f"可用工具数量: {len(tools_result.tools)}")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # 2. 测试aceflow_stage工具 - 列出阶段
                print("\n=== 🎯 步骤2: 调用aceflow_stage工具 ===")
                stage_result = await session.call_tool(
                    name="aceflow_stage",
                    arguments={
                        "action": "list"
                    }
                )
                print("阶段列表结果:")
                for content in stage_result.content:
                    if content.type == "text":
                        result_data = json.loads(content.text)
                        print(f"  成功: {result_data.get('success')}")
                        if 'result' in result_data:
                            stages = result_data['result'].get('stages', [])
                            print(f"  阶段数量: {len(stages)}")
                            print(f"  阶段列表: {stages}")
                
                # 3. 测试aceflow_template工具 - 列出模板
                print("\n=== 📄 步骤3: 调用aceflow_template工具 ===")
                template_result = await session.call_tool(
                    name="aceflow_template", 
                    arguments={
                        "action": "list"
                    }
                )
                print("模板列表结果:")
                for content in template_result.content:
                    if content.type == "text":
                        result_data = json.loads(content.text)
                        print(f"  成功: {result_data.get('success')}")
                        if 'templates' in result_data:
                            templates = result_data['templates']
                            print(f"  模板数量: {len(templates)}")
                            for tmpl in templates:
                                print(f"    - {tmpl['name']}: {tmpl['description']}")
                
                # 4. 测试双向协作 - AI向MCP发送数据
                print("\n=== 🤖 步骤4: 测试双向AI-MCP协作 ===")
                analysis_data = {
                    "project_type": "web_application",
                    "tech_stack": ["React", "Node.js", "TypeScript"],
                    "features": ["用户管理", "任务CRUD", "状态跟踪"]
                }
                
                collab_result = await session.call_tool(
                    name="aceflow_stage",
                    arguments={
                        "action": "set_analysis",
                        "data": analysis_data
                    }
                )
                print("协作数据保存结果:")
                for content in collab_result.content:
                    if content.type == "text":
                        result_data = json.loads(content.text)
                        print(f"  成功: {result_data.get('success')}")
                        print(f"  消息: {result_data.get('message')}")
                
                print("\n🎉 MCP服务器测试完成！")
                
    except Exception as e:
        print(f"❌ MCP测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("AceFlow MCP Server - 真实MCP协议测试")
    print("=" * 50)
    
    # 运行异步测试
    success = asyncio.run(test_mcp_server())
    
    if success:
        print("\n✅ 所有MCP协议测试通过！")
        sys.exit(0)
    else:
        print("\n❌ MCP协议测试失败！")
        sys.exit(1)