#!/usr/bin/env python3
"""
模板同步脚本 - 将主项目的模板文件同步到MCP服务器
确保模板内容的一致性
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime


class TemplateSyncer:
    """模板同步器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.mcp_root = self.script_dir.parent
        self.main_templates_dir = self.mcp_root.parent / "aceflow" / "templates"
        self.mcp_templates_dir = self.mcp_root / "aceflow_mcp_server" / "templates"
        self.sync_manifest_file = self.mcp_templates_dir / "sync_manifest.json"
    
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        if not file_path.exists():
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def get_template_files(self) -> List[Path]:
        """获取需要同步的模板文件列表"""
        if not self.main_templates_dir.exists():
            raise FileNotFoundError(f"主模板目录不存在: {self.main_templates_dir}")
        
        template_files = []
        
        # 获取所有.md模板文件
        for pattern in ["*.md", "*.j2", "*.yaml"]:
            template_files.extend(self.main_templates_dir.glob(pattern))
            # 也包含子目录中的文件
            template_files.extend(self.main_templates_dir.glob(f"**/{pattern}"))
        
        return template_files
    
    def load_sync_manifest(self) -> Dict:
        """加载同步清单"""
        if not self.sync_manifest_file.exists():
            return {"last_sync": None, "files": {}}
        
        try:
            with open(self.sync_manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"last_sync": None, "files": {}}
    
    def save_sync_manifest(self, manifest: Dict):
        """保存同步清单"""
        self.sync_manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.sync_manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def sync_templates(self, force: bool = False) -> Dict:
        """同步模板文件"""
        print("开始同步模板文件...")
        
        # 创建目标目录
        self.mcp_templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取模板文件
        template_files = self.get_template_files()
        print(f"发现 {len(template_files)} 个模板文件")
        
        # 加载同步清单
        manifest = self.load_sync_manifest()
        
        sync_result = {
            "total_files": len(template_files),
            "synced_files": 0,
            "skipped_files": 0,
            "updated_files": [],
            "new_files": [],
            "errors": []
        }
        
        for template_file in template_files:
            try:
                # 计算相对路径
                rel_path = template_file.relative_to(self.main_templates_dir)
                target_file = self.mcp_templates_dir / rel_path
                
                # 计算文件哈希
                source_hash = self.get_file_hash(template_file)
                target_hash = self.get_file_hash(target_file)
                
                # 检查是否需要同步
                file_key = str(rel_path)
                last_hash = manifest["files"].get(file_key, "")
                
                if not force and source_hash == target_hash == last_hash:
                    sync_result["skipped_files"] += 1
                    continue
                
                # 创建目标目录
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(template_file, target_file)
                
                # 更新清单
                manifest["files"][file_key] = source_hash
                
                if target_hash == "":
                    sync_result["new_files"].append(str(rel_path))
                else:
                    sync_result["updated_files"].append(str(rel_path))
                
                sync_result["synced_files"] += 1
                print(f"同步: {rel_path}")
                
            except Exception as e:
                error_msg = f"同步失败 {template_file}: {str(e)}"
                sync_result["errors"].append(error_msg)
                print(f"同步失败: {error_msg}")
        
        # 更新同步清单
        manifest["last_sync"] = datetime.now().isoformat()
        self.save_sync_manifest(manifest)
        
        # 输出结果
        print(f"\n同步完成:")
        print(f"   总文件数: {sync_result['total_files']}")
        print(f"   已同步: {sync_result['synced_files']}")
        print(f"   跳过: {sync_result['skipped_files']}")
        print(f"   新文件: {len(sync_result['new_files'])}")
        print(f"   更新文件: {len(sync_result['updated_files'])}")
        print(f"   错误: {len(sync_result['errors'])}")
        
        return sync_result
    
    def check_sync_status(self) -> Dict:
        """检查同步状态"""
        print("🔍 检查模板同步状态...")
        
        if not self.main_templates_dir.exists():
            return {"error": f"主模板目录不存在: {self.main_templates_dir}"}
        
        template_files = self.get_template_files()
        manifest = self.load_sync_manifest()
        
        status = {
            "main_templates_dir": str(self.main_templates_dir),
            "mcp_templates_dir": str(self.mcp_templates_dir),
            "last_sync": manifest.get("last_sync"),
            "total_templates": len(template_files),
            "out_of_sync": [],
            "missing": [],
            "extra": []
        }
        
        # 检查每个文件的同步状态
        for template_file in template_files:
            rel_path = template_file.relative_to(self.main_templates_dir)
            target_file = self.mcp_templates_dir / rel_path
            
            if not target_file.exists():
                status["missing"].append(str(rel_path))
            else:
                source_hash = self.get_file_hash(template_file)
                target_hash = self.get_file_hash(target_file)
                if source_hash != target_hash:
                    status["out_of_sync"].append(str(rel_path))
        
        # 检查多余的文件
        if self.mcp_templates_dir.exists():
            for mcp_file in self.mcp_templates_dir.rglob("*"):
                if mcp_file.is_file() and mcp_file.name != "sync_manifest.json":
                    try:
                        rel_path = mcp_file.relative_to(self.mcp_templates_dir)
                        source_file = self.main_templates_dir / rel_path
                        if not source_file.exists():
                            status["extra"].append(str(rel_path))
                    except ValueError:
                        continue
        
        return status


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AceFlow模板同步工具")
    parser.add_argument("--check", action="store_true", help="检查同步状态")
    parser.add_argument("--force", action="store_true", help="强制同步所有文件")
    parser.add_argument("--sync", action="store_true", help="执行同步")
    
    args = parser.parse_args()
    
    syncer = TemplateSyncer()
    
    if args.check:
        status = syncer.check_sync_status()
        if "error" in status:
            print(f"❌ {status['error']}")
            return 1
        
        print(f"📁 主模板目录: {status['main_templates_dir']}")
        print(f"📁 MCP模板目录: {status['mcp_templates_dir']}")
        print(f"🕒 上次同步: {status['last_sync'] or '从未同步'}")
        print(f"📊 总模板数: {status['total_templates']}")
        
        if status['missing']:
            print(f"❌ 缺失文件 ({len(status['missing'])}):")
            for file in status['missing']:
                print(f"   - {file}")
        
        if status['out_of_sync']:
            print(f"⚠️  不同步文件 ({len(status['out_of_sync'])}):")
            for file in status['out_of_sync']:
                print(f"   - {file}")
        
        if status['extra']:
            print(f"🗑️  多余文件 ({len(status['extra'])}):")
            for file in status['extra']:
                print(f"   - {file}")
        
        if not status['missing'] and not status['out_of_sync']:
            print("✅ 所有模板文件都已同步")
    
    elif args.sync or not any([args.check]):
        # 默认执行同步
        try:
            result = syncer.sync_templates(force=args.force)
            if result['errors']:
                return 1
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())