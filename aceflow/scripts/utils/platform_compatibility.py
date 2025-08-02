#!/usr/bin/env python3
"""
AceFlow v3.0 跨平台兼容性和错误处理增强模块
解决Windows平台特定问题和改进用户体验
"""

import os
import sys
import stat
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import json
from datetime import datetime


class PlatformUtils:
    """跨平台工具类"""
    
    @staticmethod
    def is_windows() -> bool:
        """检查是否为Windows系统"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_admin() -> bool:
        """检查是否具有管理员权限"""
        try:
            if PlatformUtils.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.getuid() == 0
        except Exception:
            return False
    
    @staticmethod
    def get_safe_encoding() -> str:
        """获取安全的文件编码"""
        if PlatformUtils.is_windows():
            return 'utf-8-sig'  # Windows with BOM
        return 'utf-8'
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """标准化路径处理"""
        return Path(path).resolve()
    
    @staticmethod
    def get_user_script_dir() -> Path:
        """获取用户脚本目录"""
        if PlatformUtils.is_windows():
            return Path.home() / "Scripts"
        else:
            return Path.home() / ".local" / "bin"


class FilePermissionChecker:
    """文件权限检查器"""
    
    @staticmethod
    def check_file_permissions(file_path: Path) -> Dict[str, bool]:
        """检查文件权限"""
        permissions = {
            'exists': False,
            'readable': False,
            'writable': False,
            'executable': False
        }
        
        try:
            if file_path.exists():
                permissions['exists'] = True
                permissions['readable'] = os.access(file_path, os.R_OK)
                permissions['writable'] = os.access(file_path, os.W_OK)
                permissions['executable'] = os.access(file_path, os.X_OK)
        except Exception:
            pass
        
        return permissions
    
    @staticmethod
    def check_directory_permissions(dir_path: Path) -> Dict[str, bool]:
        """检查目录权限"""
        permissions = {
            'exists': False,
            'readable': False,
            'writable': False,
            'creatable': False
        }
        
        try:
            if dir_path.exists():
                permissions['exists'] = True
                permissions['readable'] = os.access(dir_path, os.R_OK)
                permissions['writable'] = os.access(dir_path, os.W_OK)
            else:
                # 检查是否可以创建目录
                parent_dir = dir_path.parent
                if parent_dir.exists():
                    permissions['creatable'] = os.access(parent_dir, os.W_OK)
        except Exception:
            pass
        
        return permissions
    
    @staticmethod
    def fix_file_permissions(file_path: Path) -> bool:
        """尝试修复文件权限"""
        try:
            if not PlatformUtils.is_windows():
                # Unix/Linux系统
                current_stat = file_path.stat()
                # 添加用户读写权限
                new_mode = current_stat.st_mode | stat.S_IRUSR | stat.S_IWUSR
                if file_path.suffix in ['.py', '.sh']:
                    new_mode |= stat.S_IXUSR  # 可执行权限
                file_path.chmod(new_mode)
            return True
        except Exception:
            return False


class SafeFileOperations:
    """安全文件操作类"""
    
    @staticmethod
    def safe_write_text(file_path: Path, content: str, backup: bool = True) -> Tuple[bool, str]:
        """安全写入文本文件"""
        try:
            # 创建父目录
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 备份现有文件
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                file_path.replace(backup_path)
            
            # 使用安全编码写入
            encoding = PlatformUtils.get_safe_encoding()
            
            # 先写入临时文件，然后原子性替换
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding=encoding, 
                dir=file_path.parent,
                delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_path = Path(temp_file.name)
            
            # 原子性替换
            temp_path.replace(file_path)
            
            # 修复权限
            FilePermissionChecker.fix_file_permissions(file_path)
            
            return True, "文件写入成功"
            
        except PermissionError as e:
            return False, f"权限错误: {e}. 请检查文件权限或以管理员身份运行"
        except UnicodeEncodeError as e:
            return False, f"编码错误: {e}. 文件包含不支持的字符"
        except OSError as e:
            return False, f"系统错误: {e}. 请检查磁盘空间和路径有效性"
        except Exception as e:
            return False, f"未知错误: {e}"
    
    @staticmethod
    def safe_read_text(file_path: Path) -> Tuple[bool, str, str]:
        """安全读取文本文件"""
        try:
            # 检查文件权限
            permissions = FilePermissionChecker.check_file_permissions(file_path)
            if not permissions['exists']:
                return False, "", "文件不存在"
            if not permissions['readable']:
                return False, "", "文件不可读，请检查权限"
            
            # 尝试多种编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'cp1252']
            
            for encoding in encodings:
                try:
                    content = file_path.read_text(encoding=encoding)
                    return True, content, f"使用 {encoding} 编码读取成功"
                except UnicodeDecodeError:
                    continue
            
            return False, "", "无法识别文件编码"
            
        except PermissionError as e:
            return False, "", f"权限错误: {e}"
        except Exception as e:
            return False, "", f"读取错误: {e}"
    
    @staticmethod
    def safe_copy_file(src: Path, dst: Path) -> Tuple[bool, str]:
        """安全复制文件"""
        try:
            # 检查源文件
            if not src.exists():
                return False, f"源文件不存在: {src}"
            
            # 创建目标目录
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            import shutil
            shutil.copy2(src, dst)
            
            # 修复权限
            FilePermissionChecker.fix_file_permissions(dst)
            
            return True, f"文件复制成功: {src} -> {dst}"
            
        except PermissionError as e:
            return False, f"权限错误: {e}. 请检查目标目录权限"
        except shutil.SameFileError:
            return True, "源文件和目标文件相同，跳过复制"
        except Exception as e:
            return False, f"复制错误: {e}"


class EnhancedErrorHandler:
    """增强错误处理器"""
    
    @staticmethod
    def handle_import_error(module_name: str, error: Exception) -> str:
        """处理导入错误"""
        error_msg = f"模块导入失败: {module_name}"
        
        if "No module named" in str(error):
            if module_name in ['yaml', 'pyyaml']:
                return f"{error_msg}\n解决方案: pip install pyyaml"
            elif module_name in ['requests']:
                return f"{error_msg}\n解决方案: pip install requests"
            else:
                return f"{error_msg}\n解决方案: pip install {module_name.replace('_', '-')}"
        
        return f"{error_msg}\n错误详情: {error}"
    
    @staticmethod
    def handle_subprocess_error(cmd: List[str], error: Exception) -> str:
        """处理子进程错误"""
        cmd_str = ' '.join(cmd)
        
        if isinstance(error, FileNotFoundError):
            return f"命令未找到: {cmd[0]}\n请确保命令已安装并在PATH中"
        elif isinstance(error, subprocess.CalledProcessError):
            return f"命令执行失败: {cmd_str}\n返回码: {error.returncode}\n错误输出: {error.stderr if error.stderr else '无'}"
        else:
            return f"执行命令时发生错误: {cmd_str}\n错误: {error}"
    
    @staticmethod
    def create_error_report(error: Exception, context: str = "") -> Dict[str, Any]:
        """创建详细错误报告"""
        import traceback
        
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'platform': platform.platform(),
            'python_version': sys.version,
            'working_directory': str(Path.cwd()),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc(),
            'suggestions': EnhancedErrorHandler.get_error_suggestions(error)
        }
    
    @staticmethod
    def get_error_suggestions(error: Exception) -> List[str]:
        """获取错误建议"""
        suggestions = []
        error_str = str(error).lower()
        
        if isinstance(error, PermissionError):
            if PlatformUtils.is_windows():
                suggestions.extend([
                    "以管理员身份运行PowerShell或命令提示符",
                    "检查文件是否被其他程序占用",
                    "临时禁用杀毒软件的实时保护",
                    "确保目标目录有写入权限"
                ])
            else:
                suggestions.extend([
                    "使用 sudo 运行命令",
                    "检查文件和目录权限: ls -la",
                    "确保当前用户有相应权限"
                ])
        
        elif isinstance(error, FileNotFoundError):
            suggestions.extend([
                "检查文件路径是否正确",
                "确保文件确实存在",
                "检查当前工作目录"
            ])
        
        elif isinstance(error, UnicodeDecodeError):
            suggestions.extend([
                "文件可能使用了不同的编码格式",
                "尝试使用文本编辑器检查文件编码",
                "确保文件是有效的文本文件"
            ])
        
        elif "module" in error_str and "not found" in error_str:
            suggestions.extend([
                "安装缺失的Python模块",
                "检查Python环境和虚拟环境",
                "确保所有依赖都已安装"
            ])
        
        return suggestions


class WindowsCompatibilityFixer:
    """Windows兼容性修复器"""
    
    @staticmethod
    def fix_path_issues(path_str: str) -> str:
        """修复路径问题"""
        # 标准化路径分隔符
        if PlatformUtils.is_windows():
            # 将Unix风格路径转换为Windows风格
            path_str = path_str.replace('/', '\\')
        
        # 处理路径长度限制
        if PlatformUtils.is_windows() and len(path_str) > 260:
            # Windows长路径支持
            if not path_str.startswith('\\\\?\\'):
                path_str = '\\\\?\\' + os.path.abspath(path_str)
        
        return path_str
    
    @staticmethod
    def fix_encoding_issues(content: str) -> str:
        """修复编码问题"""
        if PlatformUtils.is_windows():
            # 移除可能有问题的字符
            content = content.encode('utf-8', errors='ignore').decode('utf-8')
            # 标准化行结束符
            content = content.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
        
        return content
    
    @staticmethod
    def check_windows_requirements() -> Dict[str, bool]:
        """检查Windows环境要求"""
        requirements = {
            'powershell_available': False,
            'python_in_path': False,
            'long_path_enabled': False,
            'execution_policy_ok': False
        }
        
        if not PlatformUtils.is_windows():
            return requirements
        
        # 检查PowerShell
        try:
            subprocess.run(['powershell', '-Command', 'Write-Host test'], 
                         capture_output=True, check=True)
            requirements['powershell_available'] = True
        except:
            pass
        
        # 检查Python在PATH中
        try:
            subprocess.run(['python', '--version'], 
                         capture_output=True, check=True)
            requirements['python_in_path'] = True
        except:
            pass
        
        # 检查执行策略
        try:
            result = subprocess.run([
                'powershell', '-Command', 'Get-ExecutionPolicy'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                policy = result.stdout.strip()
                requirements['execution_policy_ok'] = policy not in ['Restricted']
        except:
            pass
        
        return requirements


def create_compatibility_test_script():
    """创建兼容性测试脚本"""
    test_script = '''#!/usr/bin/env python3
"""
AceFlow 跨平台兼容性测试脚本
"""

import sys
import os
from pathlib import Path

# 导入我们的兼容性模块
from platform_compatibility import (
    PlatformUtils, FilePermissionChecker, SafeFileOperations,
    EnhancedErrorHandler, WindowsCompatibilityFixer
)

def test_platform_detection():
    """测试平台检测"""
    print(f"当前平台: {sys.platform}")
    print(f"是否为Windows: {PlatformUtils.is_windows()}")
    print(f"是否为管理员: {PlatformUtils.is_admin()}")
    print(f"安全编码: {PlatformUtils.get_safe_encoding()}")

def test_file_operations():
    """测试文件操作"""
    test_file = Path("test_aceflow_compat.txt")
    test_content = "AceFlow兼容性测试\\n中文字符测试"
    
    # 测试写入
    success, msg = SafeFileOperations.safe_write_text(test_file, test_content)
    print(f"文件写入测试: {'成功' if success else '失败'} - {msg}")
    
    if success:
        # 测试读取
        success, content, msg = SafeFileOperations.safe_read_text(test_file)
        print(f"文件读取测试: {'成功' if success else '失败'} - {msg}")
        
        # 清理测试文件
        try:
            test_file.unlink()
        except:
            pass

def test_windows_compatibility():
    """测试Windows兼容性"""
    if PlatformUtils.is_windows():
        requirements = WindowsCompatibilityFixer.check_windows_requirements()
        print("Windows环境检查:")
        for req, status in requirements.items():
            print(f"  {req}: {'✓' if status else '✗'}")

def main():
    """主测试函数"""
    print("AceFlow 跨平台兼容性测试")
    print("=" * 40)
    
    test_platform_detection()
    print()
    
    test_file_operations()
    print()
    
    test_windows_compatibility()

if __name__ == "__main__":
    main()
'''
    
    return test_script

# 导出主要类和函数
__all__ = [
    'PlatformUtils',
    'FilePermissionChecker', 
    'SafeFileOperations',
    'EnhancedErrorHandler',
    'WindowsCompatibilityFixer',
    'create_compatibility_test_script'
]