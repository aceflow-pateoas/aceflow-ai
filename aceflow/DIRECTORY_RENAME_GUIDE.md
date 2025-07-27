# 🔄 目录重命名指南

## 📋 当前状态
```
当前路径: /home/chenjing/AI/acefow-pateoas-framework_v2/aceflow
需要修改: acefow-pateoas-framework_v2 → aceflow-ai
```

## 🛠️ 重命名步骤

### 方法1: 直接重命名 (推荐)
```bash
# 回到AI目录
cd /home/chenjing/AI

# 重命名整个项目目录
mv acefow-pateoas-framework_v2 aceflow-ai

# 进入新的项目目录
cd aceflow-ai

# 验证目录结构
ls -la
```

### 方法2: 如果遇到权限问题
```bash
# 使用sudo权限
sudo mv /home/chenjing/AI/acefow-pateoas-framework_v2 /home/chenjing/AI/aceflow-ai

# 修正所有权
sudo chown -R chenjing:chenjing /home/chenjing/AI/aceflow-ai
```

### 方法3: 复制后删除
```bash
# 复制到新目录
cp -r /home/chenjing/AI/acefow-pateoas-framework_v2 /home/chenjing/AI/aceflow-ai

# 删除旧目录 (谨慎操作)
rm -rf /home/chenjing/AI/acefow-pateoas-framework_v2
```

## 🎯 重命名后的下一步

### 1. 进入项目目录
```bash
cd /home/chenjing/AI/aceflow-ai/aceflow
```

### 2. 继续Git初始化
```bash
# 如果还没有初始化git
git init

# 设置主分支名称
git branch -M main

# 添加远程仓库
git remote add origin git@github.com:aceflow-pateoas/aceflow-ai.git

# 添加所有文件
git add .

# 创建首次提交
git commit -m "🚀 Initial release: ACEFLOW-AI v3.0

✨ Features:
- First AI programming assistant with project memory
- PATEOAS architecture for state-aware programming
- Cline/VSCode deep integration
- Intelligent memory system with pattern learning
- 5-minute quick setup and verification

📚 Documentation:
- Complete README with installation guide
- Comprehensive promotion and marketing materials
- Technical architecture documentation
- Brand assets and design guidelines

🎯 Ready for community launch and feedback

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送到远程仓库
git push -u origin main
```

## 📋 验证重命名成功

### 检查新目录结构
```bash
# 验证新路径存在
ls -la /home/chenjing/AI/aceflow-ai/

# 验证aceflow子目录存在
ls -la /home/chenjing/AI/aceflow-ai/aceflow/

# 验证重要文件存在
ls -la /home/chenjing/AI/aceflow-ai/aceflow/README.md
ls -la /home/chenjing/AI/aceflow-ai/aceflow/enhanced_cli.py
```

### 更新工作区配置
如果使用VSCode，可能需要更新工作区配置：
```bash
# 更新VSCode工作区文件中的路径引用
sed -i 's|acefow-pateoas-framework_v2|aceflow-ai|g' /home/chenjing/AI/aceflow-ai/aceflow/aceflow-pateoas-workspace.code-workspace
```

## 🎉 完成后的目录结构

```
/home/chenjing/AI/aceflow-ai/
├── aceflow/                    # 主项目目录
│   ├── README.md              # ACEFLOW-AI项目介绍
│   ├── enhanced_cli.py        # 主要CLI工具
│   ├── pateoas/               # PATEOAS核心引擎
│   ├── quick_verify.sh        # 快速验证脚本
│   └── ... (所有其他文件)
└── ... (其他相关文件)
```

---

**请执行上述重命名命令，然后我们就可以继续Git推送了！** 🚀