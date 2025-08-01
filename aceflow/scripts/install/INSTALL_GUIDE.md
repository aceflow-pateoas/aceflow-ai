# AceFlow v3.0 跨平台安装指南

## 🎯 方案3：混合部署架构

### 架构设计
- **全局脚本**: `aceflow` (Python CLI) - 跨平台通用
- **项目脚本**: Shell脚本 - 项目级拷贝，支持离线工作
- **安装工具**: 平台特定安装脚本

## 🖥️ Linux/macOS 安装

### 1. 使用安装脚本（推荐）
```bash
# 用户级安装（推荐）
bash /path/to/aceflow/scripts/install/global-install.sh --user-install

# 系统级安装（需要sudo）
sudo bash /path/to/aceflow/scripts/install/global-install.sh --system-install
```

### 2. 手动安装
```bash
# 1. 添加到PATH
export PATH="$PATH:/path/to/aceflow/scripts"

# 2. 创建符号链接
ln -s /path/to/aceflow/scripts/aceflow ~/.local/bin/aceflow

# 3. 使PATH生效
source ~/.bashrc  # 或 ~/.zshrc
```

### 3. 验证安装
```bash
aceflow --version
aceflow --help
```

## 🪟 Windows 安装

### 1. 使用PowerShell安装脚本（推荐）
```powershell
# 用户级安装（推荐）
.\Install-AceFlow.ps1 -UserInstall

# 系统级安装（需要管理员权限）
.\Install-AceFlow.ps1 -SystemInstall
```

### 2. 手动安装
```powershell
# 1. 复制脚本到用户目录
Copy-Item "C:\path\to\aceflow\scripts\aceflow" "$env:USERPROFILE\Scripts\"

# 2. 添加到用户PATH
$path = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "$path;$env:USERPROFILE\Scripts"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# 3. 重启PowerShell使PATH生效
```

### 3. 验证安装
```powershell
aceflow --version
aceflow --help
```

## 📁 项目初始化使用

### 基础使用
```bash
# Linux/macOS
aceflow init --mode=standard --project="我的项目"

# Windows  
aceflow init --mode=standard --project="我的项目"
```

### 交互式初始化
```bash
aceflow init --interactive
```

### Smart模式（AI驱动）
```bash
aceflow init --mode=smart --interactive
```

## 🛠️ 日常工作流程

### 项目级脚本使用
初始化完成后，项目目录中会包含工作脚本：

```bash
# Linux/macOS
./aceflow-stage.sh status
./aceflow-validate.sh
./aceflow-templates.sh list

# Windows (在Git Bash或WSL中)
./aceflow-stage.sh status
./aceflow-validate.sh  
./aceflow-templates.sh list
```

### Python CLI使用
```bash
# 全局命令，所有平台通用
aceflow stage status
aceflow validate
aceflow template list
```

## 🔧 安装检查和维护

### 检查安装状态
```bash
# Linux/macOS
bash /path/to/global-install.sh --check

# Windows
.\Install-AceFlow.ps1 -Check
```

### 更新安装
```bash
# 重新运行安装命令即可更新
```

### 卸载
```bash
# Linux/macOS
bash /path/to/global-install.sh --uninstall

# Windows
.\Install-AceFlow.ps1 -Uninstall
```

## 📋 目录结构对比

### Linux/macOS
```
~/.local/bin/aceflow          # 全局CLI脚本
项目目录/
├── .aceflow/                 # 配置目录
├── .clinerules/             # AI Agent配置
├── aceflow_result/          # 输出目录
├── aceflow-stage.sh         # 项目脚本
├── aceflow-validate.sh      # 项目脚本
├── aceflow-templates.sh     # 项目脚本
└── SCRIPTS_README.md        # 脚本说明
```

### Windows
```
%USERPROFILE%\Scripts\aceflow # 全局CLI脚本
项目目录\
├── .aceflow\                # 配置目录
├── .clinerules\             # AI Agent配置
├── aceflow_result\          # 输出目录
├── aceflow-stage.sh         # 项目脚本（在WSL/Git Bash中使用）
├── aceflow-validate.sh      # 项目脚本
├── aceflow-templates.sh     # 项目脚本
└── SCRIPTS_README.md        # 脚本说明
```

## ⚠️ 注意事项

### Windows特殊说明
1. **Python环境**: 确保Python 3.7+已安装并在PATH中
2. **Shell脚本**: 项目级Shell脚本需要在WSL、Git Bash或Cygwin中运行
3. **权限**: PowerShell执行策略可能需要调整：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### 通用要求
1. **Python 3.7+**: 核心CLI需要Python环境
2. **Git**: 推荐安装Git以获得完整功能
3. **AI Agent**: 推荐安装Cline、Cursor或Claude Code

## 🎯 优势总结

### 跨平台兼容性
- ✅ 核心功能使用Python实现，完全跨平台
- ✅ 只有安装脚本需要平台特定版本
- ✅ 避免重复开发和维护成本

### 用户体验
- ✅ 统一的CLI命令接口
- ✅ 平台原生的安装体验
- ✅ 项目独立的工作脚本

### 维护效率
- ✅ 核心逻辑只需维护一份Python代码
- ✅ 安装脚本简单，维护成本低
- ✅ 支持增量更新和版本管理