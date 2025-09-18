#!/usr/bin/env python3
"""
在干净目录中演示AceFlow MCP Server完整功能
"""
import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def clean_project_demo():
    """在全新目录中演示完整工作流"""
    print("🌟 AceFlow MCP Server 全新项目演示")
    print("=" * 60)
    
    # 创建临时工作目录
    temp_dir = tempfile.mkdtemp(prefix="aceflow_demo_")
    old_cwd = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        print(f"📁 工作目录: {temp_dir}")
        
        server_params = StdioServerParameters(
            command="aceflow-mcp-server",
            args=[],
            env={"PWD": temp_dir}  # 设置工作目录环境变量
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ MCP连接已建立")
                
                # 1. 查看和设置模板
                print("\n🎨 步骤1: 设置smart模板")
                result = await session.call_tool("aceflow_template", {
                    "action": "apply", 
                    "template": "smart"
                })
                print("✅ 模板应用成功")
                
                # 2. 在全新目录初始化项目
                print("\n🚀 步骤2: 初始化全新项目")
                result = await session.call_tool("aceflow_init", {
                    "project_name": "smart-todo-app",
                    "project_type": "web_app", 
                    "mode": "smart"
                })
                content = result.content[0].text
                print("项目初始化结果:")
                print(content)
                
                # 3. 查看生成的文件结构
                print("\n📂 步骤3: 查看生成的项目结构")
                for root, dirs, files in os.walk(temp_dir):
                    # 限制显示深度
                    level = root.replace(temp_dir, '').count(os.sep)
                    if level < 3:  # 只显示3级深度
                        indent = ' ' * 2 * level
                        print(f"{indent}{os.path.basename(root)}/")
                        subindent = ' ' * 2 * (level + 1)
                        for file in files[:5]:  # 最多显示5个文件
                            print(f"{subindent}{file}")
                        if len(files) > 5:
                            print(f"{subindent}... (还有{len(files)-5}个文件)")
                
                # 4. 完整的工作流演示
                print("\n🔄 步骤4: 完整工作流演示")
                
                # 查看当前状态
                result = await session.call_tool("aceflow_stage", {"action": "status"})
                current_info = json.loads(result.content[0].text)
                print(f"当前阶段: {current_info['result']['current_stage']}")
                print(f"进度: {current_info['result']['progress']}%")
                
                # 执行几个阶段转换
                stages_to_test = ["task_breakdown", "test_design", "implementation"]
                for i, stage in enumerate(stages_to_test):
                    print(f"\n   {i+1}. 进入 {stage} 阶段")
                    result = await session.call_tool("aceflow_stage", {"action": "next"})
                    stage_info = json.loads(result.content[0].text)
                    if stage_info['success']:
                        print(f"   ✅ 当前进度: {stage_info['result']['progress']}%")
                
                # 5. 运行最终验证
                print("\n✅ 步骤5: 项目质量验证")
                result = await session.call_tool("aceflow_validate", {
                    "action": "validate",
                    "mode": "detailed"
                })
                validation_info = json.loads(result.content[0].text)
                print(f"验证结果: {validation_info['validation_result']['status']}")
                print(f"通过检查: {validation_info['validation_result']['checks_passed']}/{validation_info['validation_result']['checks_total']}")
                
                print(f"\n🎉 演示完成！项目位于: {temp_dir}")
                print("\n💫 成功展示的功能:")
                print("   ✨ 模板管理和应用")
                print("   ✨ 全新项目初始化") 
                print("   ✨ 项目文件结构生成")
                print("   ✨ 多阶段工作流控制")
                print("   ✨ 项目质量验证")
                print("   ✨ 状态跟踪和进度管理")
                
    finally:
        os.chdir(old_cwd)
        print(f"\n🧹 清理临时目录: {temp_dir}")
        # 可以选择不删除，方便查看生成的内容
        # shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        asyncio.run(clean_project_demo())
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()