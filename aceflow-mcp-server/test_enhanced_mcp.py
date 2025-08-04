#!/usr/bin/env python3
"""
测试增强后的 AceFlow MCP Tools
验证修复效果和新功能
"""

import sys
import json
from pathlib import Path

# Add the aceflow_mcp_server to path
sys.path.insert(0, str(Path(__file__).parent))

from aceflow_mcp_server.tools import AceFlowTools


def test_enhanced_init():
    """测试增强后的 aceflow_init 功能"""
    print("🧪 测试增强后的 aceflow_init 功能")
    print("=" * 50)
    
    tools = AceFlowTools()
    
    # 测试初始化
    test_dir = Path("test_enhanced_project")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    result = tools.aceflow_init(
        mode="complete",
        project_name="test_enhanced",
        directory=str(test_dir)
    )
    
    print(f"初始化结果: {result['success']}")
    if result['success']:
        print(f"创建的文件: {result['project_info']['created_files']}")
        
        # 验证 .clinerules 目录结构
        clinerules_dir = test_dir / ".clinerules"
        if clinerules_dir.is_dir():
            print("✅ .clinerules 目录创建成功")
            
            # 检查子目录
            subdirs = ["config", "templates", "schemas"]
            for subdir in subdirs:
                if (clinerules_dir / subdir).exists():
                    print(f"✅ {subdir}/ 目录存在")
                else:
                    print(f"❌ {subdir}/ 目录缺失")
        else:
            print("❌ .clinerules 不是目录")
    else:
        print(f"初始化失败: {result.get('error', 'Unknown error')}")
    
    return test_dir


def test_stage_execution(test_dir):
    """测试阶段执行功能"""
    print("\n🧪 测试阶段执行功能")
    print("=" * 50)
    
    # 切换到测试目录
    import os
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        tools = AceFlowTools()
        
        # 测试状态查询
        status_result = tools.aceflow_stage(action="status")
        print(f"状态查询: {status_result['success']}")
        if status_result['success']:
            current_stage = status_result['result']['current_stage']
            print(f"当前阶段: {current_stage}")
        
        # 测试阶段执行
        print("\n尝试执行当前阶段...")
        execute_result = tools.aceflow_stage(action="execute")
        print(f"执行结果: {execute_result['success']}")
        
        if execute_result['success']:
            print(f"执行阶段: {execute_result['stage_id']}")
            print(f"输出文件: {execute_result['output_path']}")
            print(f"质量评分: {execute_result['quality_score']}")
            print(f"执行时间: {execute_result['execution_time']}秒")
            
            if execute_result.get('warnings'):
                print(f"警告: {execute_result['warnings']}")
        else:
            print(f"执行失败: {execute_result.get('error', 'Unknown error')}")
            if execute_result.get('errors'):
                print(f"错误详情: {execute_result['errors']}")
    
    finally:
        os.chdir(original_cwd)


def test_template_system(test_dir):
    """测试模板系统"""
    print("\n🧪 测试模板系统")
    print("=" * 50)
    
    # 检查模板文件
    templates_dir = test_dir / ".clinerules" / "templates"
    if templates_dir.exists():
        print("✅ 模板目录存在")
        
        # 检查模式定义文件
        mode_def_file = test_dir / ".clinerules" / "config" / "mode_definitions.yaml"
        if mode_def_file.exists():
            print("✅ 模式定义文件存在")
            
            # 读取并验证内容
            try:
                import yaml
                with open(mode_def_file, 'r', encoding='utf-8') as f:
                    mode_definitions = yaml.safe_load(f)
                
                modes = mode_definitions.get('modes', {})
                print(f"支持的模式: {list(modes.keys())}")
                
                # 检查 complete 模式
                if 'complete' in modes:
                    complete_mode = modes['complete']
                    stages = complete_mode.get('stages', [])
                    print(f"Complete 模式阶段数: {len(stages)}")
                    
                    if stages:
                        first_stage = stages[0]
                        print(f"第一个阶段: {first_stage.get('id')} - {first_stage.get('name')}")
                
            except Exception as e:
                print(f"❌ 模式定义文件解析失败: {e}")
        else:
            print("❌ 模式定义文件缺失")
    else:
        print("❌ 模板目录不存在")


def test_document_generation(test_dir):
    """测试文档生成功能"""
    print("\n🧪 测试文档生成功能")
    print("=" * 50)
    
    # 检查是否生成了文档
    result_dir = test_dir / "aceflow_result"
    if result_dir.exists():
        print("✅ 结果目录存在")
        
        # 列出生成的文档
        docs = list(result_dir.glob("*.md"))
        if docs:
            print(f"生成的文档数量: {len(docs)}")
            for doc in docs:
                print(f"  - {doc.name}")
                
                # 检查文档内容
                content = doc.read_text(encoding='utf-8')
                if len(content) > 100:
                    print(f"    内容长度: {len(content)} 字符 ✅")
                else:
                    print(f"    内容长度: {len(content)} 字符 ⚠️ (可能太短)")
        else:
            print("❌ 没有生成文档")
    else:
        print("❌ 结果目录不存在")


def cleanup_test(test_dir):
    """清理测试环境"""
    print("\n🧹 清理测试环境")
    print("=" * 50)
    
    try:
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print("✅ 测试目录已清理")
    except Exception as e:
        print(f"❌ 清理失败: {e}")


def main():
    """主测试函数"""
    print("🚀 AceFlow MCP Tools 增强功能测试")
    print("=" * 60)
    
    try:
        # 1. 测试增强的初始化功能
        test_dir = test_enhanced_init()
        
        # 2. 测试模板系统
        test_template_system(test_dir)
        
        # 3. 测试阶段执行功能
        test_stage_execution(test_dir)
        
        # 4. 测试文档生成
        test_document_generation(test_dir)
        
        print("\n🎉 测试完成!")
        print("=" * 60)
        
        # 询问是否清理
        response = input("\n是否清理测试环境? (y/N): ")
        if response.lower() == 'y':
            cleanup_test(test_dir)
        else:
            print(f"测试环境保留在: {test_dir}")
    
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()