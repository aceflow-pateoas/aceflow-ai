# 🧪 AceFlow-AI 新项目测试指南

> **完整的新项目测试操作手册**  
> **适用版本**: AceFlow-AI v3.0  
> **更新时间**: 2025-07-28

## 🎯 测试目标

通过创建一个新项目来验证：
- ✅ AceFlow-AI 安装是否正确
- ✅ 核心功能是否正常工作
- ✅ Cline集成是否有效
- ✅ 记忆系统是否可用
- ✅ 工作流模式是否正确

---

## 🚀 第一步：环境准备

### 1.1 确认安装状态

**检查全局安装**：
```bash
# 验证全局命令是否可用
which aceflow
which aceflow-start

# 检查AceFlow状态
aceflow status
```

**预期结果**：
- 命令路径应显示在 `$HOME/.local/bin/`
- 状态显示应包含版本信息和基本配置

### 1.2 确认依赖环境

**检查必要组件**：
```bash
# 检查Python版本
python3 --version

# 检查Git版本  
git --version

# 检查VSCode是否安装
code --version

# 检查Cline扩展是否安装
code --list-extensions | grep saoudrizwan.claude-dev
```

**预期结果**：
- Python >= 3.8
- Git 正常显示版本
- VSCode 正常显示版本
- Cline扩展已安装

---

## 🎯 第二步：创建测试项目

### 2.1 创建项目目录

选择一个干净的位置创建测试项目：

```bash
# 创建项目目录
mkdir ~/test-aceflow-project
cd ~/test-aceflow-project

# 验证当前目录
pwd
ls -la
```

**预期结果**：
- 目录创建成功
- 目录为空（除了可能的 `.` 和 `..`）

### 2.2 初始化AceFlow项目

```bash
# 初始化AceFlow项目
aceflow init
```

**预期结果**：
```
🚀 AceFlow-AI 项目初始化
==============================
🔧 检查系统环境...
✅ 环境检查通过
🔧 创建项目目录结构...
✅ 目录结构创建完成
🔧 生成配置文件...
✅ 配置文件生成完成
🔧 配置VSCode集成...
✅ VSCode集成配置完成
🎉 AceFlow-AI 项目初始化完成！
```

### 2.3 验证项目结构

```bash
# 检查生成的目录结构
ls -la
tree . # 如果有tree命令

# 检查关键目录
ls -la .aceflow/
ls -la .clinerules/
ls -la .vscode/
```

**预期结果**：
- `.aceflow/` 目录存在，包含 `config/`, `state/`, `memory/` 等子目录
- `.clinerules/` 目录存在，包含 `pateoas_integration.md`
- `.vscode/` 目录存在，包含 `settings.json`, `tasks.json`
- `aceflow-workspace.code-workspace` 文件存在

---

## 🧠 第三步：测试核心功能

### 3.1 测试状态查询

```bash
# 查看项目状态
aceflow status

# 查看详细状态
aceflow status --performance

# 查看记忆统计
aceflow status --memory-stats
```

**预期结果**：
- 显示项目基本信息
- 显示当前阶段（通常为 "ready" 或 "初始化"）
- 记忆数量为 0 或少量初始记忆

### 3.2 测试记忆系统

```bash
# 添加测试记忆
aceflow memory add "这是第一个测试记忆，用于验证记忆系统功能"

# 添加分类记忆
aceflow memory add "选择使用FastAPI作为后端框架" --category decision --tags "框架,后端"

# 搜索记忆
aceflow memory find "测试"

# 列出所有记忆
aceflow memory list --recent
```

**预期结果**：
- 记忆添加成功，返回记忆ID
- 搜索能找到刚添加的记忆
- 记忆列表显示正确的分类和标签

### 3.3 测试PATEOAS功能

```bash
# 测试PATEOAS状态
aceflow pateoas status

# 测试任务分析
aceflow pateoas analyze "开发一个简单的TODO应用"

# 测试决策门
aceflow pateoas gates evaluate
```

**预期结果**：
- PATEOAS状态正常
- 任务分析返回复杂度评估和建议
- 决策门评估显示当前质量检查点状态

---

## 🎨 第四步：测试VSCode+Cline集成

### 4.1 启动开发环境

```bash
# 启动AceFlow开发环境
aceflow-start
```

**预期结果**：
- VSCode自动打开
- 加载 `aceflow-workspace.code-workspace` 工作区
- 显示项目文件结构

### 4.2 测试Cline扩展

在VSCode中：

1. **启动Cline扩展**：
   - 按 `Ctrl+Shift+P`
   - 输入 "Cline: Start New Task"
   - 或点击侧边栏的Cline图标

2. **测试基本对话**：
   - 对Cline说：`"检查项目状态"`
   - 对Cline说：`"这个项目现在是什么情况？"`

**预期结果**：
- Cline扩展成功启动
- 能够响应AceFlow相关查询
- 显示项目状态信息

### 4.3 测试智能功能

继续在Cline中测试：

1. **测试记忆召回**：
   - 对Cline说：`"之前我们记录了什么？"`
   - 对Cline说：`"有关框架的决策是什么？"`

2. **测试任务分析**：
   - 对Cline说：`"我想开发一个用户登录功能"`
   - 对Cline说：`"分析一下这个任务的复杂度"`

**预期结果**：
- 能够召回之前添加的记忆
- 提供任务复杂度分析和建议
- 显示相关的工作流建议

---

## ✅ 第五步：功能验证清单

### 5.1 基础功能验证

**命令行功能**：
- [ ] `aceflow status` 正常显示
- [ ] `aceflow memory add/find/list` 正常工作
- [ ] `aceflow pateoas status` 正常显示
- [ ] `aceflow init` 创建正确的目录结构
- [ ] `aceflow-start` 能启动VSCode

**文件结构验证**：
- [ ] `.aceflow/` 目录结构完整
- [ ] `.clinerules/pateoas_integration.md` 存在
- [ ] `.vscode/` 配置文件正确
- [ ] `aceflow-workspace.code-workspace` 可用

### 5.2 集成功能验证

**VSCode集成**：
- [ ] 工作区正确加载
- [ ] Cline扩展可以启动
- [ ] VSCode任务（Tasks）可用

**Cline集成**：
- [ ] 能够响应AceFlow相关查询
- [ ] 能够调用AceFlow命令
- [ ] 能够访问项目记忆
- [ ] 提供智能分析和建议

### 5.3 高级功能验证

**PATEOAS功能**：
- [ ] 状态感知正常
- [ ] 记忆系统智能召回
- [ ] 任务分析准确
- [ ] 决策门评估有效

**工作流功能**：
- [ ] 能够设置不同工作流模式
- [ ] 模式切换正常
- [ ] 阶段管理有效

---

## 🔧 第六步：常见问题排查

### 6.1 安装问题

**问题**：`aceflow` 命令找不到
```bash
# 检查安装路径
ls -la $HOME/.local/bin/aceflow

# 检查PATH设置
echo $PATH | grep -o $HOME/.local/bin

# 重新加载shell配置
source ~/.bashrc
```

**问题**：Python依赖报错
```bash
# 检查Python环境
cd $HOME/.aceflow/aceflow
source venv/bin/activate  # 如果使用虚拟环境
pip list | grep -E "(yaml|pyyaml)"
```

### 6.2 VSCode集成问题

**问题**：Cline扩展无响应
1. 重启VSCode
2. 重新安装Cline扩展：
   ```bash
   code --uninstall-extension saoudrizwan.claude-dev
   code --install-extension saoudrizwan.claude-dev
   ```
3. 检查 `.clinerules/pateoas_integration.md` 文件

**问题**：工作区配置错误
1. 删除并重新生成工作区文件
2. 运行 `aceflow init --force` 重新初始化

### 6.3 功能异常问题

**问题**：记忆系统不工作
```bash
# 检查记忆目录
ls -la .aceflow/memory/

# 重建记忆索引
aceflow memory rebuild-index

# 运行诊断
aceflow pateoas diagnose
```

**问题**：PATEOAS功能异常
```bash
# 运行完整诊断
aceflow pateoas diagnose --generate-report

# 检查配置文件
cat .aceflow/config/project.yaml

# 重置PATEOAS状态
aceflow pateoas reset --confirm
```

---

## 📊 第七步：性能测试

### 7.1 响应时间测试

测试各种命令的响应时间：

```bash
# 测试状态查询响应时间
time aceflow status

# 测试记忆搜索响应时间
time aceflow memory find "test"

# 测试PATEOAS分析响应时间
time aceflow pateoas analyze "简单测试任务"
```

**预期结果**：
- 基本命令 < 2秒
- 记忆搜索 < 3秒
- PATEOAS分析 < 5秒

### 7.2 内存使用测试

```bash
# 查看进程内存使用
ps aux | grep -E "(python|aceflow)"

# 检查磁盘使用
du -sh .aceflow/
du -sh $HOME/.aceflow/
```

**预期结果**：
- 项目配置 < 5MB
- 全局安装 < 100MB

---

## 🎯 第八步：清理测试环境

测试完成后，可以选择清理测试数据：

### 8.1 清理项目目录

```bash
# 返回上级目录
cd ..

# 删除测试项目
rm -rf ~/test-aceflow-project
```

### 8.2 清理测试记忆（可选）

```bash
# 清理测试期间的记忆
aceflow memory clean --pattern "测试" --dry-run  # 先预览
aceflow memory clean --pattern "测试"            # 确认删除
```

---

## 📋 测试报告模板

完成测试后，可以使用以下模板记录结果：

```markdown
# AceFlow-AI 测试报告

**测试时间**: YYYY-MM-DD HH:MM
**测试环境**: 
- 操作系统: [OS版本]
- Python版本: [版本号]
- VSCode版本: [版本号]

## 测试结果

### ✅ 通过的功能
- [ ] 基础安装
- [ ] 命令行功能
- [ ] 记忆系统
- [ ] VSCode集成
- [ ] Cline集成
- [ ] PATEOAS功能

### ❌ 发现的问题
1. [问题描述]
   - 重现步骤: [步骤]
   - 错误信息: [信息]
   - 解决方案: [方案]

### 📊 性能数据
- 状态查询: [时间]
- 记忆搜索: [时间]
- PATEOAS分析: [时间]

### 💡 改进建议
[建议内容]
```

---

## 🎉 总结

这份测试指南将帮助你：
- ✅ 验证AceFlow-AI的完整功能
- ✅ 确保所有组件正常工作
- ✅ 熟悉核心操作流程
- ✅ 排查常见问题
- ✅ 为实际项目使用做好准备

通过完整的测试流程，你将对AceFlow-AI的能力有全面的了解，并能够充分利用其智能化的开发工作流管理功能！🚀