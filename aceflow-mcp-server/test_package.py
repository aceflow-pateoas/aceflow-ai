#!/usr/bin/env python3
"""
测试打包后的MCP服务器功能
验证模板文件是否正确包含和可访问
"""

import sys
import json
from pathlib import Path


def test_template_config():
    """测试模板配置"""
    print("🧪 测试模板配置...")
    
    try:
        from aceflow_mcp_server.config.template_config import template_config
        
        info = template_config.get_template_info()
        print(f"✅ 模板目录: {info['main_templates_dir']}")
        print(f"✅ 模板可用: {info['templates_available']}")
        print(f"✅ 支持阶段数: {len(info['supported_stages'])}")
        print(f"✅ 模板文件数: {len(info['template_files'])}")
        
        return True
    except Exception as e:
        print(f"❌ 模板配置测试失败: {e}")
        return False


def test_template_files():
    """测试模板文件访问"""
    print("\n🧪 测试模板文件访问...")
    
    try:
        from aceflow_mcp_server.config.template_config import template_config
        
        # 测试几个关键模板
        test_stages = [
            "S1_user_stories",
            "S2_task_breakdown", 
            "S3_test_design",
            "S4_implementation"
        ]
        
        success_count = 0
        for stage in test_stages:
            path = template_config.get_template_path(stage)
            if path and path.exists():
                content = path.read_text(encoding='utf-8')
                print(f"✅ {stage}: {path.name} ({len(content)} 字符)")
                success_count += 1
            else:
                print(f"❌ {stage}: 模板文件不存在")
        
        print(f"✅ 成功访问 {success_count}/{len(test_stages)} 个模板文件")
        return success_count == len(test_stages)
        
    except Exception as e:
        print(f"❌ 模板文件测试失败: {e}")
        return False


def test_document_generation():
    """测试文档生成功能"""
    print("\n🧪 测试文档生成功能...")
    
    try:
        # 简化测试：只检查模块是否可以导入
        import aceflow_mcp_server.core.document_generator as doc_gen
        
        # 检查关键属性是否存在
        if hasattr(doc_gen, 'DocumentResult'):
            print("✅ DocumentResult 类可用")
        else:
            print("❌ DocumentResult 类不可用")
            return False
            
        print("✅ 文档生成模块导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 文档生成测试失败: {e}")
        return False


def test_mcp_tools():
    """测试MCP工具功能"""
    print("\n🧪 测试MCP工具功能...")
    
    try:
        from aceflow_mcp_server.tools import AceFlowTools
        
        tools = AceFlowTools()
        
        # 测试验证功能
        result = tools.aceflow_validate(mode="basic")
        if result["success"]:
            print("✅ aceflow_validate 工具正常")
        else:
            print(f"❌ aceflow_validate 工具失败: {result.get('error')}")
            return False
        
        # 测试模板功能
        result = tools.aceflow_template(action="list")
        if result["success"]:
            print("✅ aceflow_template 工具正常")
        else:
            print(f"❌ aceflow_template 工具失败: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP工具测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 AceFlow MCP Server 打包测试")
    print("=" * 50)
    
    tests = [
        ("模板配置", test_template_config),
        ("模板文件访问", test_template_files),
        ("MCP工具", test_mcp_tools),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 执行测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MCP服务器打包正确。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查问题。")
        return 1


if __name__ == "__main__":
    exit(main())