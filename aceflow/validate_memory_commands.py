#!/usr/bin/env python3
"""
PATEOAS Memory Commands Validation Tool
验证并展示优化后的PATEOAS记忆命令结构
"""

import sys
import subprocess
import json
from datetime import datetime

class MemoryCommandValidator:
    def __init__(self):
        self.cli_path = "enhanced_cli.py"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'command_tests': [],
            'summary': {}
        }
    
    def run_command(self, command, expected_success=True):
        """运行命令并验证结果"""
        try:
            result = subprocess.run(
                f"python3 {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0
            return {
                'command': command,
                'success': success,
                'expected_success': expected_success,
                'passed': success == expected_success,
                'stdout': result.stdout[:500] if result.stdout else '',
                'stderr': result.stderr[:200] if result.stderr else ''
            }
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'success': False,
                'expected_success': expected_success,
                'passed': False,
                'error': 'Command timeout'
            }
        except Exception as e:
            return {
                'command': command,
                'success': False,
                'expected_success': expected_success,
                'passed': False,
                'error': str(e)
            }
    
    def validate_command_structure(self):
        """验证命令结构"""
        print("🔍 验证PATEOAS记忆命令结构...")
        print("=" * 60)
        
        # 测试帮助命令
        help_result = self.run_command(f"{self.cli_path} pateoas memory --help")
        self.results['command_tests'].append(help_result)
        
        if help_result['success']:
            print("✅ 基础命令结构正常")
            
            # 验证子命令存在性
            expected_commands = ['list', 'add', 'find', 'recall', 'smart-recall', 'clean']
            output = help_result['stdout']
            
            missing_commands = []
            for cmd in expected_commands:
                if cmd not in output:
                    missing_commands.append(cmd)
            
            if not missing_commands:
                print("✅ 所有预期子命令都存在")
                print(f"   可用命令: {', '.join(expected_commands)}")
            else:
                print(f"❌ 缺少子命令: {', '.join(missing_commands)}")
        else:
            print("❌ 基础命令结构异常")
            print(f"   错误: {help_result.get('stderr', 'Unknown error')}")
    
    def test_parameter_consistency(self):
        """测试参数一致性"""
        print(f"\n🧪 测试参数一致性...")
        print("=" * 60)
        
        # 测试各子命令的帮助
        subcommands = ['list', 'add', 'find', 'recall', 'smart-recall', 'clean']
        
        for subcmd in subcommands:
            result = self.run_command(f"{self.cli_path} pateoas memory {subcmd} --help")
            self.results['command_tests'].append(result)
            
            if result['success']:
                print(f"✅ {subcmd} 命令参数结构正确")
            else:
                print(f"❌ {subcmd} 命令参数结构异常")
                print(f"   错误: {result.get('stderr', 'Unknown error')[:100]}")
    
    def test_deprecated_commands(self):
        """测试废弃命令的处理"""
        print(f"\n⚠️  测试废弃命令处理...")
        print("=" * 60)
        
        # 这些命令应该失败或显示警告
        deprecated_tests = [
            f"{self.cli_path} pateoas memory search 'test'",
            f"{self.cli_path} pateoas memory intelligent-recall --query 'test'"
        ]
        
        for cmd in deprecated_tests:
            result = self.run_command(cmd, expected_success=False)
            self.results['command_tests'].append(result)
            
            if not result['success']:
                print(f"✅ 废弃命令正确被拒绝: {cmd.split()[-2:]}")
            else:
                print(f"⚠️  废弃命令仍可执行: {cmd.split()[-2:]}")
    
    def test_functional_examples(self):
        """测试功能性示例"""
        print(f"\n🚀 测试功能性示例...")
        print("=" * 60)
        
        # 测试实际功能
        functional_tests = [
            # 添加记忆
            f'{self.cli_path} pateoas memory add "CLI验证测试记忆" --category pattern --tags "测试,验证"',
            # 基础搜索
            f'{self.cli_path} pateoas memory find "CLI验证"',
            # 智能召回
            f'{self.cli_path} pateoas memory recall "验证测试" --limit 3',
            # 列出记忆
            f'{self.cli_path} pateoas memory list --limit 3',
        ]
        
        for cmd in functional_tests:
            result = self.run_command(cmd)
            self.results['command_tests'].append(result)
            
            action = cmd.split()[-3] if 'add' in cmd else cmd.split()[-2]
            if result['success']:
                print(f"✅ {action} 功能正常")
            else:
                print(f"❌ {action} 功能异常")
                if result.get('stderr'):
                    print(f"   错误: {result['stderr'][:100]}")
    
    def generate_summary(self):
        """生成验证总结"""
        total_tests = len(self.results['command_tests'])
        passed_tests = sum(1 for test in self.results['command_tests'] if test['passed'])
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'overall_status': 'PASS' if passed_tests == total_tests else 'FAIL'
        }
        
        print(f"\n📊 验证总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"成功率: {self.results['summary']['success_rate']:.1%}")
        print(f"整体状态: {self.results['summary']['overall_status']}")
        
        if self.results['summary']['overall_status'] == 'PASS':
            print("\n🎉 所有测试通过! PATEOAS记忆命令结构优化成功!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，需要进一步调试")
    
    def save_results(self, filename="memory_commands_validation.json"):
        """保存验证结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 详细结果已保存到: {filename}")
    
    def run_full_validation(self):
        """运行完整验证"""
        print("🧪 PATEOAS Memory Commands Validation Tool")
        print("🎯 目标: 验证优化后的命令结构，避免参数识别错误")
        print("=" * 80)
        
        self.validate_command_structure()
        self.test_parameter_consistency()
        self.test_deprecated_commands()
        self.test_functional_examples()
        self.generate_summary()
        self.save_results()
        
        return self.results['summary']['overall_status'] == 'PASS'

def main():
    validator = MemoryCommandValidator()
    success = validator.run_full_validation()
    
    # 显示使用建议
    print(f"\n💡 优化后的PATEOAS记忆命令使用建议:")
    print("=" * 60)
    print("📝 添加记忆:     memory add '内容' --category pattern")
    print("🔍 快速搜索:     memory find '关键词'") 
    print("🧠 智能召回:     memory recall '查询' --context '上下文'")
    print("🚀 高级召回:     memory smart-recall '查询' --include-patterns")
    print("📋 列出记忆:     memory list --recent --tags '标签'")
    print("🧹 清理记忆:     memory clean --days 30 --dry-run")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())