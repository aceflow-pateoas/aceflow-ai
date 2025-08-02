# AceFlow MCP安装方式 - 产品需求文档 (PRD)

## 📋 文档信息

- **产品名称**: AceFlow MCP Server
- **版本**: v1.0
- **创建日期**: 2025-08-02
- **文档类型**: 产品需求文档 (PRD)
- **优先级**: P1 (高优先级)

## 🎯 产品概述

### 背景与动机

当前AceFlow的安装方式存在以下痛点：
1. **复杂的安装流程** - 需要多步骤手动安装和配置
2. **平台兼容性问题** - Windows/macOS/Linux环境差异导致安装失败
3. **依赖管理困难** - 需要用户手动管理Python环境和依赖
4. **版本更新麻烦** - 无法自动更新，需要重新安装

### 解决方案

通过MCP (Model Context Protocol) 提供AceFlow服务，让用户可以：
- **一键安装** - 通过`uvx`命令直接安装使用
- **自动更新** - MCP服务器自动处理版本更新
- **跨平台兼容** - 统一的安装和使用体验
- **零配置启动** - 无需复杂的环境配置

## 🎯 产品目标

### 主要目标
1. **简化安装流程** - 从10+步骤减少到1条命令
2. **提高成功率** - 安装成功率从60%提升到95%+
3. **改善用户体验** - 安装时间从10分钟减少到30秒
4. **增强可维护性** - 支持自动更新和远程配置

### 成功指标
- 安装成功率 > 95%
- 平均安装时间 < 30秒
- 用户满意度 > 4.5/5.0
- 支持问题减少 > 70%

## 👥 目标用户

### 主要用户群体

1. **AI开发者**
   - 使用Kiro、Cursor、Claude等AI工具
   - 需要结构化的开发流程管理
   - 希望快速上手，专注于开发

2. **团队协作者**
   - 多人协作的软件项目
   - 需要统一的工作流程标准
   - 要求简单的部署和维护

3. **企业用户**
   - 有严格的合规和质量要求
   - 需要可控的安装和更新流程
   - 要求稳定可靠的服务

### 用户画像

**典型用户**: Alex - AI应用开发者
- 使用Kiro进行日常开发
- 管理多个并行项目
- 希望有标准化的项目管理流程
- 不想花时间在工具安装和配置上

## 🔧 功能需求

### 核心功能

#### 1. MCP服务器实现
- **服务器名称**: `aceflow-mcp-server`
- **协议版本**: MCP v1.0
- **运行环境**: Python 3.8+
- **依赖管理**: 通过uvx自动处理

#### 2. 工具集成 (Tools)

##### 2.1 项目初始化工具
```json
{
  "name": "aceflow_init",
  "description": "Initialize AceFlow project with specified mode",
  "inputSchema": {
    "type": "object",
    "properties": {
      "mode": {
        "type": "string",
        "enum": ["minimal", "standard", "complete", "smart"],
        "description": "Workflow mode"
      },
      "project_name": {
        "type": "string",
        "description": "Project name"
      },
      "directory": {
        "type": "string",
        "description": "Project directory path"
      }
    },
    "required": ["mode"]
  }
}
```

##### 2.2 阶段管理工具
```json
{
  "name": "aceflow_stage",
  "description": "Manage project stages and workflow",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["status", "next", "list", "reset"],
        "description": "Stage management action"
      },
      "stage": {
        "type": "string",
        "description": "Target stage name (for specific actions)"
      }
    },
    "required": ["action"]
  }
}
```

##### 2.3 项目验证工具
```json
{
  "name": "aceflow_validate",
  "description": "Validate project compliance and quality",
  "inputSchema": {
    "type": "object",
    "properties": {
      "mode": {
        "type": "string",
        "enum": ["basic", "complete"],
        "default": "basic"
      },
      "fix": {
        "type": "boolean",
        "default": false,
        "description": "Auto-fix issues if possible"
      },
      "report": {
        "type": "boolean",
        "default": false,
        "description": "Generate detailed report"
      }
    }
  }
}
```

##### 2.4 模板管理工具
```json
{
  "name": "aceflow_template",
  "description": "Manage workflow templates",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["list", "apply", "validate"],
        "description": "Template action"
      },
      "template": {
        "type": "string",
        "description": "Template name"
      }
    },
    "required": ["action"]
  }
}
```

#### 3. 资源提供 (Resources)

##### 3.1 项目状态资源
```json
{
  "uri": "aceflow://project/state",
  "name": "Project State",
  "description": "Current project state and progress",
  "mimeType": "application/json"
}
```

##### 3.2 工作流配置资源
```json
{
  "uri": "aceflow://workflow/config",
  "name": "Workflow Configuration",
  "description": "Current workflow mode and settings",
  "mimeType": "application/json"
}
```

##### 3.3 阶段指导资源
```json
{
  "uri": "aceflow://stage/guide/{stage}",
  "name": "Stage Guide",
  "description": "Detailed guidance for specific stage",
  "mimeType": "text/markdown"
}
```

### 高级功能

#### 1. 智能推荐
- 基于项目特征推荐最适合的工作流模式
- 根据历史数据优化阶段转换建议
- 提供个性化的最佳实践建议

#### 2. 团队协作
- 支持多用户共享项目状态
- 提供团队进度同步功能
- 集成常见协作工具（Git、Slack等）

#### 3. 扩展性
- 支持自定义工作流模式
- 允许第三方插件集成
- 提供API接口供其他工具调用

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │  MCP Server     │    │  AceFlow Core   │
│  (Kiro/Cursor)  │◄──►│   (FastMCP)     │◄──►│    Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  File System    │
                       │ (.aceflow/...)  │
                       └─────────────────┘
```

### 技术栈

#### 后端技术
- **MCP框架**: FastMCP (Python)
- **核心引擎**: AceFlow v3.0
- **数据存储**: JSON文件 + SQLite (可选)
- **配置管理**: YAML + JSON
- **日志系统**: Python logging

#### 分发技术
- **包管理**: PyPI + uvx
- **版本控制**: Semantic Versioning
- **自动更新**: uvx自动处理
- **跨平台**: Python跨平台支持

### 数据模型

#### 项目状态模型
```python
@dataclass
class ProjectState:
    name: str
    mode: WorkflowMode
    current_stage: str
    completed_stages: List[str]
    progress_percentage: float
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any]
```

#### 工作流配置模型
```python
@dataclass
class WorkflowConfig:
    mode: WorkflowMode
    stages: List[Stage]
    transitions: Dict[str, str]
    quality_gates: List[QualityGate]
    templates: Dict[str, Template]
```

## 🎨 用户体验设计

### 安装流程

#### 当前流程 (复杂)
```bash
# 1. 下载源码
git clone https://github.com/aceflow/aceflow.git

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行安装脚本
./aceflow/scripts/install/Install-AceFlow.ps1 -UserInstall

# 4. 初始化项目
python aceflow/scripts/aceflow-init.py -m standard -p myproject

# 5. 配置环境变量
export ACEFLOW_HOME=/path/to/aceflow

# 6. 验证安装
python aceflow-validate.py
```

#### 新流程 (简化)
```bash
# 1. 一键安装并使用
uvx aceflow-mcp-server

# 2. 在AI客户端中配置MCP服务器
# (通过UI或配置文件)

# 3. 直接在AI对话中使用
"请使用AceFlow初始化一个标准模式的项目"
```

### 用户界面

#### MCP配置示例
```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": [
        "aceflow_init",
        "aceflow_stage",
        "aceflow_validate"
      ]
    }
  }
}
```

#### 使用示例对话
```
用户: "我想开始一个新的AI项目，需要标准的开发流程"

AI: 我来帮你使用AceFlow初始化项目。让我先了解一下项目信息：
- 项目名称是什么？
- 你希望使用哪种工作流模式？(minimal/standard/complete/smart)

用户: "项目名称是ai-chatbot，使用standard模式"

AI: 好的，我来为你初始化项目...
[调用 aceflow_init 工具]

✅ 项目初始化完成！
- 项目名称: ai-chatbot
- 工作流模式: standard
- 当前阶段: user_stories
- 下一步: 开始用户故事分析

现在你可以开始第一个阶段的工作了。需要我提供用户故事分析的指导吗？
```

## 📋 实施计划

### 开发阶段

#### Phase 1: 核心MCP服务器 (4周)
- **Week 1-2**: MCP服务器框架搭建
  - FastMCP集成
  - 基础工具实现
  - 本地测试环境
  
- **Week 3-4**: 核心功能开发
  - 项目初始化工具
  - 阶段管理工具
  - 基础验证功能

#### Phase 2: 高级功能 (3周)
- **Week 5-6**: 资源管理和模板系统
  - 资源提供实现
  - 模板管理工具
  - 配置管理优化
  
- **Week 7**: 智能推荐功能
  - 项目分析算法
  - 推荐引擎
  - 用户偏好学习

#### Phase 3: 发布准备 (2周)
- **Week 8**: 打包和分发
  - PyPI包准备
  - uvx兼容性测试
  - 文档编写
  
- **Week 9**: 测试和优化
  - 端到端测试
  - 性能优化
  - 用户反馈收集

### 发布计划

#### Beta版本 (v0.9.0)
- **目标用户**: 内部测试和早期采用者
- **功能范围**: 核心MCP工具 + 基础资源
- **发布时间**: 开发完成后1周

#### 正式版本 (v1.0.0)
- **目标用户**: 所有AceFlow用户
- **功能范围**: 完整功能集
- **发布时间**: Beta测试完成后2周

## 🧪 测试策略

### 测试类型

#### 1. 单元测试
- MCP工具函数测试
- 核心业务逻辑测试
- 数据模型验证测试
- 覆盖率目标: >90%

#### 2. 集成测试
- MCP协议兼容性测试
- AI客户端集成测试
- 文件系统操作测试
- 跨平台兼容性测试

#### 3. 端到端测试
- 完整用户流程测试
- 多项目并发测试
- 长期运行稳定性测试
- 性能基准测试

### 测试环境

#### 开发环境
- **平台**: Windows 11, macOS 14, Ubuntu 22.04
- **Python版本**: 3.8, 3.9, 3.10, 3.11, 3.12
- **AI客户端**: Kiro, Cursor, Claude Desktop

#### 生产环境
- **分发平台**: PyPI
- **运行环境**: uvx + Python
- **监控系统**: 使用统计和错误报告

## 📊 风险评估

### 技术风险

#### 高风险
1. **MCP协议兼容性**
   - 风险: 不同AI客户端的MCP实现差异
   - 缓解: 多客户端测试，标准协议遵循

2. **跨平台兼容性**
   - 风险: 不同操作系统的文件系统差异
   - 缓解: 使用pathlib，充分的平台测试

#### 中风险
1. **性能问题**
   - 风险: 大型项目的响应速度
   - 缓解: 异步处理，缓存优化

2. **版本兼容性**
   - 风险: AceFlow核心版本更新导致不兼容
   - 缓解: 版本锁定，向后兼容设计

### 业务风险

#### 中风险
1. **用户接受度**
   - 风险: 用户不愿意改变现有工作流程
   - 缓解: 渐进式迁移，保持向后兼容

2. **竞争产品**
   - 风险: 类似的MCP服务器出现
   - 缓解: 持续创新，用户体验优化

## 📈 成功指标

### 技术指标
- **安装成功率**: >95%
- **响应时间**: <2秒 (90%的请求)
- **错误率**: <1%
- **可用性**: >99.5%

### 业务指标
- **用户采用率**: 30%的现有用户在3个月内迁移
- **新用户增长**: 50%的新用户选择MCP安装方式
- **用户满意度**: >4.5/5.0
- **支持工单减少**: >70%

### 社区指标
- **GitHub Stars**: +500 (6个月内)
- **PyPI下载量**: >10,000/月
- **社区贡献**: >10个外部贡献者
- **文档访问**: >50,000 页面浏览/月

## 🔄 后续规划

### 短期规划 (3-6个月)
1. **功能增强**
   - 添加更多工作流模式
   - 集成更多AI客户端
   - 提供Web界面管理

2. **生态建设**
   - 开发插件系统
   - 建立模板市场
   - 社区贡献指南

### 长期规划 (6-12个月)
1. **企业功能**
   - 团队协作增强
   - 权限管理系统
   - 审计和合规功能

2. **AI增强**
   - 智能代码生成
   - 自动化测试建议
   - 项目健康度分析

## 📞 联系信息

- **产品经理**: [待定]
- **技术负责人**: [待定]
- **项目仓库**: https://github.com/aceflow/aceflow-mcp-server
- **文档站点**: https://docs.aceflow.dev/mcp

---

**文档版本**: v1.0  
**最后更新**: 2025-08-02  
**审核状态**: 待审核