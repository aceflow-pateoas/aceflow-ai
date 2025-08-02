#!/usr/bin/env python3
"""
AceFlow 跨平台兼容性测试脚本
用于验证和测试Windows平台兼容性问题
"""

import sys
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# 添加项目路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "utils"))

try:
    from platform_compatibility import (
        PlatformUtils, FilePermissionChecker, SafeFileOperations,
        EnhancedErrorHandler, WindowsCompatibilityFixer
    )
except ImportError as e:
    print(f"❌ 无法导入兼容性模块: {e}")
    sys.exit(1)


class CompatibilityTester:
    """兼容性测试器"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
    
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        print(f"🧪 测试: {test_name}")
        try:
            result = test_func()
            if result:
                print(f"   ✅ 通过")
                self.test_results.append((test_name, True, ""))
            else:
                print(f"   ❌ 失败")
                self.test_results.append((test_name, False, "测试返回False"))
                self.failed_tests.append(test_name)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            self.test_results.append((test_name, False, str(e)))
            self.failed_tests.append(test_name)
    
    def test_platform_detection(self) -> bool:
        """测试平台检测功能"""
        try:
            is_win = PlatformUtils.is_windows()
            is_admin = PlatformUtils.is_admin()
            encoding = PlatformUtils.get_safe_encoding()
            user_dir = PlatformUtils.get_user_script_dir()
            
            print(f"     平台: {platform.system()}")
            print(f"     Windows: {is_win}")
            print(f"     管理员权限: {is_admin}")
            print(f"     安全编码: {encoding}")
            print(f"     用户脚本目录: {user_dir}")
            
            return True
        except Exception:
            return False
    
    def test_file_permissions(self) -> bool:
        """测试文件权限检查"""
        try:
            # 创建测试文件
            test_file = Path(tempfile.gettempdir()) / "aceflow_perm_test.txt"
            test_file.write_text("permission test")
            
            # 检查权限
            perms = FilePermissionChecker.check_file_permissions(test_file)
            print(f"     权限检查: {perms}")
            
            # 清理
            test_file.unlink(missing_ok=True)
            
            return perms['exists'] and perms['readable']
        except Exception:
            return False
    
    def test_safe_file_operations(self) -> bool:
        """测试安全文件操作"""
        try:
            test_file = Path(tempfile.gettempdir()) / "aceflow_safe_test.txt"
            test_content = "AceFlow 安全文件操作测试\n包含中文字符的内容"
            
            # 测试写入
            success, msg = SafeFileOperations.safe_write_text(test_file, test_content)
            if not success:
                print(f"     写入失败: {msg}")
                return False
            
            # 测试读取
            success, content, msg = SafeFileOperations.safe_read_text(test_file)
            if not success:
                print(f"     读取失败: {msg}")
                return False
            
            print(f"     内容匹配: {content.strip() == test_content.strip()}")
            
            # 清理
            test_file.unlink(missing_ok=True)
            
            return content.strip() == test_content.strip()
        except Exception:
            return False
    
    def test_path_handling(self) -> bool:
        """测试路径处理"""
        try:
            test_paths = [
                "C:\\Users\\test\\Documents",
                "/home/user/documents", 
                "relative/path/test",
                "path with spaces/test"
            ]
            
            for path in test_paths:
                normalized = PlatformUtils.normalize_path(path)
                print(f"     {path} -> {normalized}")
            
            return True
        except Exception:
            return False
    
    def test_encoding_handling(self) -> bool:
        """测试编码处理"""
        try:
            test_strings = [
                "ASCII only",
                "中文字符测试",
                "Mixed 混合 content",
                "Special chars: áéíóú"
            ]
            
            for test_str in test_strings:
                if PlatformUtils.is_windows():
                    fixed = WindowsCompatibilityFixer.fix_encoding_issues(test_str)
                    print(f"     编码修复: {test_str[:20]}... -> OK")
                else:
                    print(f"     跳过编码修复 (非Windows): {test_str[:20]}...")
            
            return True
        except Exception:
            return False
    
    def test_subprocess_handling(self) -> bool:
        """测试子进程处理"""
        try:
            # 测试简单命令
            if PlatformUtils.is_windows():
                cmd = ["powershell", "-Command", "Write-Host 'test'"]
            else:
                cmd = ["echo", "test"]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                print(f"     命令执行: {cmd[0]} -> 返回码 {result.returncode}")
                return result.returncode == 0
            except subprocess.TimeoutExpired:
                print(f"     命令超时: {cmd[0]}")
                return False
            except FileNotFoundError:
                print(f"     命令未找到: {cmd[0]}")
                return False
        except Exception:
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            # 创建一个故意的错误
            try:
                raise PermissionError("测试权限错误")
            except Exception as e:
                report = EnhancedErrorHandler.create_error_report(e, "测试上下文")
                suggestions = EnhancedErrorHandler.get_error_suggestions(e)
                
                print(f"     错误报告生成: {len(report)} 个字段")
                print(f"     建议数量: {len(suggestions)}")
                
                return len(report) > 0 and len(suggestions) > 0
        except Exception:
            return False
    
    def test_windows_specific(self) -> bool:
        """测试Windows特定功能"""
        try:
            if not PlatformUtils.is_windows():
                print("     跳过Windows特定测试 (非Windows系统)")
                return True
            
            requirements = WindowsCompatibilityFixer.check_windows_requirements()
            print("     Windows环境检查:")
            for req, status in requirements.items():
                print(f"       {req}: {'✓' if status else '✗'}")
            
            return True
        except Exception:
            return False
    
    def test_aceflow_scripts_syntax(self) -> bool:
        """测试AceFlow脚本语法"""
        try:
            script_dir = Path(__file__).parent
            python_scripts = [
                "aceflow-init.py",
                "aceflow-stage.py", 
                "aceflow-validate.py",
                "aceflow-templates.py"
            ]
            
            syntax_ok = 0
            for script in python_scripts:
                script_path = script_dir / script
                if script_path.exists():
                    try:
                        # 语法检查
                        result = subprocess.run([
                            sys.executable, "-m", "py_compile", str(script_path)
                        ], capture_output=True)
                        
                        if result.returncode == 0:
                            print(f"     {script}: ✓ 语法正确")
                            syntax_ok += 1
                        else:
                            print(f"     {script}: ✗ 语法错误")
                            print(f"       {result.stderr.decode()}")
                    except Exception as e:
                        print(f"     {script}: ✗ 检查失败 - {e}")
                else:
                    print(f"     {script}: - 文件不存在")
            
            return syntax_ok > 0
        except Exception:
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 AceFlow 跨平台兼容性测试")
        print("=" * 50)
        print(f"📊 测试环境:")
        print(f"   操作系统: {platform.platform()}")
        print(f"   Python版本: {sys.version}")
        print(f"   工作目录: {Path.cwd()}")
        print(f"   测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 运行所有测试
        tests = [
            ("平台检测", self.test_platform_detection),
            ("文件权限检查", self.test_file_permissions),
            ("安全文件操作", self.test_safe_file_operations),
            ("路径处理", self.test_path_handling),
            ("编码处理", self.test_encoding_handling),
            ("子进程处理", self.test_subprocess_handling),
            ("错误处理", self.test_error_handling),
            ("Windows特定功能", self.test_windows_specific),
            ("AceFlow脚本语法", self.test_aceflow_scripts_syntax)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            print()
        
        # 显示总结
        self.show_summary()
    
    def show_summary(self):
        """显示测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print("📊 测试总结")
        print("=" * 30)
        print(f"总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"📈 成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ 失败的测试:")
            for test_name in self.failed_tests:
                print(f"   - {test_name}")
        
        if failed_tests == 0:
            print(f"\n🎉 所有测试通过！AceFlow在当前平台上应该可以正常工作。")
        elif failed_tests <= 2:
            print(f"\n⚠️ 大部分测试通过，但有少量问题需要注意。")
        else:
            print(f"\n🚨 多个测试失败，建议检查环境配置。")


def main():
    """主函数"""
    tester = CompatibilityTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()