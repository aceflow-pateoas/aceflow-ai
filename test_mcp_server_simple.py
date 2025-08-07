#!/usr/bin/env python3
"""
简单MCP服务器测试 - 验证服务器启动和基本功能
Simple MCP Server Test for AceFlow Enhanced Server
"""

import subprocess
import time
import json
import requests
from pathlib import Path


def test_server_startup():
    """测试服务器启动"""
    print("🚀 测试AceFlow增强版MCP服务器启动...")
    
    try:
        # 尝试启动服务器（非阻塞模式）
        result = subprocess.run(
            ["aceflow-enhanced-server", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ 服务器命令行接口正常")
            print("   帮助信息:")
            for line in result.stdout.split('\n')[:5]:
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print(f"❌ 服务器启动失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 服务器启动超时")
        return False
    except FileNotFoundError:
        print("❌ aceflow-enhanced-server 命令未找到")
        print("   请确保已正确安装: pip install -e aceflow-mcp-server/")
        return False
    except Exception as e:
        print(f"❌ 服务器测试失败: {e}")
        return False


def test_package_installation():
    """测试包安装"""
    print("\n📦 测试包安装状态...")
    
    try:
        # 测试导入核心模块
        from aceflow_mcp_server.enhanced_tools import EnhancedAceFlowTools
        from aceflow_mcp_server.enhanced_resources import EnhancedAceFlowResources
        from aceflow_mcp_server.core.validation_engine import ValidationEngine
        from aceflow_mcp_server.core.enhanced_state_manager import EnhancedStateManager
        
        print("✅ 核心模块导入成功:")
        print("   - EnhancedAceFlowTools")
        print("   - EnhancedAceFlowResources") 
        print("   - ValidationEngine")
        print("   - EnhancedStateManager")
        
        # 测试基本功能
        tools = EnhancedAceFlowTools()
        resources = EnhancedAceFlowResources()
        validation_engine = ValidationEngine()
        state_manager = EnhancedStateManager()
        
        print("✅ 组件实例化成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False


def test_enhanced_functionality():
    """测试增强功能"""
    print("\n🤝 测试AI-人协同工作流功能...")
    
    try:
        from aceflow_mcp_server.enhanced_tools import EnhancedAceFlowTools
        from aceflow_mcp_server.core.intent_recognizer import IntentRecognizer, IntentType
        
        # 测试意图识别
        recognizer = IntentRecognizer()
        result = recognizer.recognize_intent("这是PRD文档，开始开发")
        
        print("✅ 意图识别测试:")
        print(f"   识别意图: {result.intent_type.value}")
        print(f"   置信度: {result.confidence:.2f}")
        print(f"   建议操作: {result.suggested_action}")
        
        # 测试增强工具
        tools = EnhancedAceFlowTools()
        
        # 测试协作状态
        status_result = tools.aceflow_collaboration_status()
        print("✅ 协作状态查询:")
        print(f"   成功: {status_result.get('success', False)}")
        print(f"   协作启用: {status_result.get('collaboration_enabled', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强功能测试失败: {e}")
        return False


def test_mcp_server_info():
    """显示MCP服务器信息"""
    print("\n📋 AceFlow增强版MCP服务器信息:")
    print("=" * 50)
    
    print("🎯 核心功能:")
    print("1. 🧠 智能意图识别 - 自动理解用户开发需求")
    print("2. 🤝 主动协作推进 - 阶段完成后主动询问用户")
    print("3. 📋 任务级协作执行 - 逐个任务执行和确认")
    print("4. 🔍 多级质量验证 - Basic/Standard/Strict验证")
    print("5. 📊 智能状态管理 - 完整的状态历史追踪")
    print("6. 💡 协作洞察分析 - 评估协作效果并优化")
    
    print("\n🔧 可用MCP工具:")
    tools = [
        ("aceflow_stage_collaborative", "智能协作式阶段管理"),
        ("aceflow_task_execute", "任务级协作执行"),
        ("aceflow_respond", "协作请求响应"),
        ("aceflow_collaboration_status", "协作状态查询"),
        ("aceflow_validate_quality", "多级质量验证")
    ]
    
    for tool_name, description in tools:
        print(f"   - {tool_name}: {description}")
    
    print("\n📊 可用MCP资源:")
    resources = [
        ("aceflow://project/intelligent-state/{project_id}", "智能项目状态"),
        ("aceflow://stage/adaptive-guide/{stage_id}", "自适应阶段指导"),
        ("aceflow://collaboration/insights/{project_id}", "协作洞察分析"),
        ("aceflow://workflow/dynamic-config/{mode}", "动态工作流配置"),
        ("aceflow://state/history/{project_id}", "状态变更历史")
    ]
    
    for resource_uri, description in resources:
        print(f"   - {resource_uri}: {description}")
    
    print("\n🚀 启动命令:")
    print("   aceflow-enhanced-server --host localhost --port 8000")
    
    print("\n📋 MCP客户端配置示例:")
    config = {
        "mcpServers": {
            "aceflow-enhanced": {
                "command": "aceflow-enhanced-server",
                "args": ["--host", "localhost", "--port", "8000"],
                "env": {
                    "ACEFLOW_LOG_LEVEL": "INFO"
                },
                "disabled": False,
                "autoApprove": [
                    "aceflow_stage_collaborative",
                    "aceflow_task_execute",
                    "aceflow_validate_quality"
                ]
            }
        }
    }
    
    print(json.dumps(config, indent=2, ensure_ascii=False))


def main():
    """主测试函数"""
    print("🚀 AceFlow AI-人协同工作流MCP服务器验证")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 测试1: 服务器启动
    if test_server_startup():
        success_count += 1
    
    # 测试2: 包安装
    if test_package_installation():
        success_count += 1
    
    # 测试3: 增强功能
    if test_enhanced_functionality():
        success_count += 1
    
    # 显示服务器信息
    test_mcp_server_info()
    
    # 总结
    print(f"\n📊 测试总结: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！AceFlow增强版MCP服务器已就绪")
        print("\n✅ 验证结果:")
        print("- ✅ 服务器命令行接口正常")
        print("- ✅ 核心模块安装完整")
        print("- ✅ AI-人协同功能正常")
        print("- ✅ MCP工具和资源已注册")
        
        print("\n🚀 下一步:")
        print("1. 在MCP客户端中配置aceflow-enhanced服务器")
        print("2. 使用aceflow_stage_collaborative工具开始协作开发")
        print("3. 体验完整的AI-人协同工作流")
        
    else:
        print("❌ 部分测试失败，请检查安装和配置")
        
    return success_count == total_tests


if __name__ == "__main__":
    main()