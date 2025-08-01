#!/usr/bin/env python3
"""
PATEOAS增强的AceFlow + Cline 集成调试工具
基于PATEOAS v3.0增强引擎的完整诊断系统
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_pateoas_status():
    """检查PATEOAS增强引擎状态"""
    print("🧠 检查PATEOAS增强引擎状态...")
    
    success, stdout, stderr = run_command("python3 enhanced_cli.py pateoas status")
    
    if success:
        print("✅ PATEOAS增强引擎正常运行")
        print("📊 系统状态:")
        # 尝试解析状态信息
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip():
                print(f"   {line}")
        return True
    else:
        print("❌ PATEOAS增强引擎检查失败")
        print(f"错误: {stderr}")
        return False

def check_memory_system():
    """检查记忆系统功能"""
    print("\n🧠 检查PATEOAS记忆系统...")
    
    # 测试记忆召回功能
    success, stdout, stderr = run_command("python3 enhanced_cli.py pateoas memory recall --query 'test' --limit 5")
    
    if success:
        print("✅ 记忆系统正常工作")
        if "相关记忆" in stdout or "memories" in stdout.lower():
            print("📚 记忆召回功能正常")
        return True
    else:
        print("❌ 记忆系统检查失败")
        print(f"错误: {stderr}")
        return False

def check_decision_gates():
    """检查决策门系统"""
    print("\n🚦 检查智能决策门系统...")
    
    success, stdout, stderr = run_command("python3 enhanced_cli.py pateoas gates evaluate")
    
    if success:
        print("✅ 决策门系统正常工作")
        if "决策门评估" in stdout or "evaluation" in stdout.lower():
            print("🎯 决策门评估功能正常")
        return True
    else:
        print("❌ 决策门系统检查失败")
        print(f"错误: {stderr}")
        return False

def check_flow_controller():
    """检查自适应流程控制器"""
    print("\n🎯 检查自适应流程控制器...")
    
    success, stdout, stderr = run_command("python3 enhanced_cli.py pateoas analyze 'test task'")
    
    if success:
        print("✅ 流程控制器正常工作")
        if "任务分析" in stdout or "analysis" in stdout.lower():
            print("🔍 任务分析功能正常")
        return True
    else:
        print("❌ 流程控制器检查失败")
        print(f"错误: {stderr}")
        return False

def check_integration_files():
    """检查集成文件"""
    print("\n📁 检查PATEOAS集成文件...")
    
    files_to_check = [
        ("enhanced_cli.py", "PATEOAS增强CLI"),
        ("pateoas/enhanced_engine.py", "PATEOAS增强引擎"),
        ("pateoas/memory_system.py", "记忆管理系统"),
        ("pateoas/flow_controller.py", "流程控制器"),
        ("pateoas/decision_gates.py", "决策门系统"),
        (".clinerules/pateoas_integration.md", "Cline集成规则"),
        (".vscode/settings.json", "VSCode设置"),
        (".vscode/tasks.json", "VSCode任务"),
        ("aceflow-pateoas-workspace.code-workspace", "工作区文件"),
        ("test_pateoas_enhanced_engine_integration.py", "集成测试")
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {description}")
        else:
            print(f"❌ {description} 缺失: {file_path}")
            all_good = False
    
    return all_good

def test_cline_integration():
    """测试Cline集成配置"""
    print("\n🤖 检查Cline集成配置...")
    
    # 检查.clinerules配置
    rules_file = Path(".clinerules/pateoas_integration.md")
    if rules_file.exists():
        print("✅ Cline集成规则文件存在")
        
        # 检查规则文件内容
        with open(rules_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_sections = [
            "PATEOAS状态感知",
            "智能工作流模式", 
            "上下文记忆增强",
            "自适应决策支持"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if not missing_sections:
            print("✅ Cline集成规则内容完整")
            return True
        else:
            print(f"⚠️ Cline集成规则缺少部分: {missing_sections}")
            return False
    else:
        print("❌ Cline集成规则文件缺失")
        return False

def run_integration_tests():
    """运行集成测试"""
    print("\n🧪 运行PATEOAS集成测试...")
    
    success, stdout, stderr = run_command("python3 test_pateoas_enhanced_engine_integration.py")
    
    if success:
        # 分析测试结果
        lines = stdout.split('\n')
        for line in lines:
            if "测试通过" in line or "OK" in line:
                print("✅ 集成测试全部通过")
                return True
            elif "FAILED" in line or "失败" in line:
                print("⚠️ 部分集成测试失败")
                print(f"详情: {line}")
                return False
        
        print("✅ 集成测试执行成功")
        return True
    else:
        print("❌ 集成测试执行失败")
        print(f"错误: {stderr}")
        return False

def generate_integration_report():
    """生成集成报告"""
    print("\n📊 生成PATEOAS集成报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": "AceFlow PATEOAS v3.0 + Cline",
        "components": {},
        "overall_status": "unknown"
    }
    
    # 收集各组件状态
    components_status = {
        "pateoas_engine": check_pateoas_status(),
        "memory_system": check_memory_system(),
        "decision_gates": check_decision_gates(), 
        "flow_controller": check_flow_controller(),
        "integration_files": check_integration_files(),
        "cline_integration": test_cline_integration(),
        "integration_tests": run_integration_tests()
    }
    
    report["components"] = components_status
    
    # 计算整体状态
    passed_count = sum(1 for status in components_status.values() if status)
    total_count = len(components_status)
    
    if passed_count == total_count:
        report["overall_status"] = "excellent"
        status_emoji = "🎉"
        status_text = "优秀"
    elif passed_count >= total_count * 0.8:
        report["overall_status"] = "good" 
        status_emoji = "✅"
        status_text = "良好"
    elif passed_count >= total_count * 0.6:
        report["overall_status"] = "fair"
        status_emoji = "⚠️"
        status_text = "一般"
    else:
        report["overall_status"] = "poor"
        status_emoji = "❌"
        status_text = "较差"
    
    # 保存报告
    with open("pateoas_integration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{status_emoji} 集成状态: {status_text} ({passed_count}/{total_count})")
    print(f"📄 详细报告已保存到: pateoas_integration_report.json")
    
    return report

def provide_recommendations(report):
    """提供改进建议"""
    print("\n💡 改进建议:")
    
    failed_components = [comp for comp, status in report["components"].items() if not status]
    
    if not failed_components:
        print("🎉 所有组件运行正常！")
        print("\n🚀 下一步建议:")
        print("1. 开始使用 code aceflow-pateoas-workspace.code-workspace")
        print("2. 启动Cline扩展并测试智能对话")
        print("3. 尝试说'检查项目状态'体验PATEOAS功能")
        print("4. 探索高级功能如智能任务分析和记忆召回")
    else:
        print("🔧 需要修复的组件:")
        
        recommendations = {
            "pateoas_engine": "检查enhanced_cli.py和pateoas模块路径",
            "memory_system": "确保记忆系统配置正确，检查数据库连接",
            "decision_gates": "验证决策门配置文件和评估逻辑",
            "flow_controller": "检查流程控制器的任务分析模块",
            "integration_files": "确保所有必需文件存在且配置正确", 
            "cline_integration": "检查.clinerules配置和Cline扩展设置",
            "integration_tests": "运行单个测试文件排查具体问题"
        }
        
        for component in failed_components:
            if component in recommendations:
                print(f"  • {component}: {recommendations[component]}")
        
        print("\n🛠️ 通用修复步骤:")
        print("1. 确保Python环境和依赖包完整")
        print("2. 检查PYTHONPATH环境变量设置")
        print("3. 验证所有配置文件语法正确")
        print("4. 重新运行setup脚本")

def main():
    """主函数"""
    print("🔍 PATEOAS增强的AceFlow + Cline 集成诊断工具")
    print("=" * 60)
    print("基于PATEOAS v3.0增强引擎的全面诊断")
    print("")
    
    # 检查是否在项目根目录
    if not Path("enhanced_cli.py").exists():
        print("❌ 错误：请在AceFlow PATEOAS项目根目录运行此脚本")
        print("   (应该包含 enhanced_cli.py 文件)")
        sys.exit(1)
    
    # 生成集成报告
    report = generate_integration_report()
    
    # 提供改进建议
    provide_recommendations(report)
    
    print("\n" + "=" * 60)
    print("📚 更多帮助:")
    print("  • PATEOAS文档: cat docs/AceFlow_Cline_Integration_Guide.md")
    print("  • 集成规则: cat .clinerules/pateoas_integration.md")
    print("  • 快速测试: python3 enhanced_cli.py pateoas status")
    print("  • 工作区启动: code aceflow-pateoas-workspace.code-workspace")

if __name__ == "__main__":
    main()