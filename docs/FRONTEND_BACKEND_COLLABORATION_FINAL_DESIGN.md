# AceFlow 前后端协作最终设计方案

**文档版本**: 1.0
**创建日期**: 2025-01-02
**基于讨论**: FRONTEND_BACKEND_COLLABORATION_DISCUSSION.md
**状态**: ✅ 设计完成，待实施

---

## 📊 项目背景

### 团队特征
- **需求配置**: 1 前端 + 1 后端
- **团队规模**: 后端 6 人左右，前端类似规模
- **迭代周期**: 1 个月
- **交付方式**: 稳健交付
- **业务复杂度**: 比较复杂

### 技术栈
- **后端**: Java + Spring Boot + Swagger
- **前端**: (未详细讨论，但支持 TypeScript)
- **代码仓库**: 多仓库（前后端独立）
- **接口文档**: Word/Markdown（手工编写 + Swagger 注解）

### 当前痛点
1. **文档不够清晰**（主要）: 缺少约束条件、缺少示例、数据类型不精确
2. **前端意见被忽略**（主要）: 缺少确认机制，口头答应容易遗忘
3. **通知不及时**（次要）: 偶尔发生
4. **文档版本混乱**（次要）: 偶尔发生
5. **前端无法验证**（次要）: 暂时较少

### 根本原因
- **文档与代码分离**: Word 文档和实际代码逐渐背离，无人知晓何者为准

---

## 🎯 核心设计方案

### 1. Single Source of Truth：OpenAPI 契约

**方案**：独立的 API 契约规范文件（OpenAPI/YAML）

**特点**：
- ✅ 独立性：不依赖前后端实现
- ✅ 可验证性：可自动生成测试
- ✅ 可生成性：可生成 Mock Server、TypeScript 类型
- ✅ 版本管理：Git 追踪变更历史

---

### 2. 仓库组织：独立的协作仓库

**方案**：新建轻量级 `api-contracts` 仓库，不迁移现有代码

**理由**：
- ✅ 零迁移成本：不改变现有仓库结构
- ✅ 易于推广：从一个需求试点即可
- ✅ 明确的协作空间：契约文件有统一位置

**仓库结构**：

```
api-contracts/
├── .aceflow-workspace/
│   └── workspace.yaml
├── contracts/
│   ├── active/                    # 开发中的需求
│   │   ├── user-export/
│   │   │   ├── openapi.yaml
│   │   │   └── meta.yaml         # 需求元数据（可选）
│   │   └── report-dashboard/
│   │       └── openapi.yaml
│   ├── released/                  # 已上线的接口
│   │   ├── user-api-v1.yaml
│   │   └── report-api-v1.yaml
│   └── archived/                  # 废弃的接口
│       └── old-api-v0.yaml
├── templates/                     # 契约模板（可选）
│   └── basic-crud-api.yaml
└── README.md

现有仓库保持不变：
frontend-repo/   (不动)
backend-repo/    (不动)
```

---

### 3. AceFlow 在工作流中的介入点

**不增加新阶段，在现有阶段中融入**：

```
S3_design:
  - 后端生成/管理 OpenAPI 契约文档
  - 作为前后端协作的基础

S4_implementation:
  - 前端：自动生成 Mock Server + TypeScript 类型
  - 后端：验证实现是否符合契约

S7_integration:
  - 契约测试：验证前后端对接的一致性
```

---

## 🔄 完整工作流程

### Phase 1: 需求启动

```bash
# 产品提需求 → 后端（需求负责人）组织需求澄清

# 后端配置需求
$ cd backend-repo/
$ aceflow feature add

交互式配置：
  需求名称: 用户数据导出
  需求编号: PROJ-1234
  前端负责人: li@company.com
  接口识别方式:
    - 精确路径: /api/reports/export
    - 路径前缀: /api/reports/

保存到 .aceflow/config.yaml
```

---

### Phase 2: 后端设计与开发 (S3 + S4 早期)

```java
// 1. 后端编写代码（Spring Boot + Swagger）
@RestController
@RequestMapping("/api")
@Tag(name = "报表管理")
public class ReportController {

    @PostMapping("/reports/export")
    @Operation(summary = "导出用户数据")
    public ResponseEntity<ExportResponse> exportReport(
        @RequestBody @Valid ExportRequest request) {
        // 业务逻辑
    }
}

@Data
@Schema(description = "导出请求")
public class ExportRequest {
    @Schema(description = "用户ID", example = "12345", required = true)
    private Integer userId;

    @Schema(description = "开始日期", example = "2025-01-01", required = true)
    private String startDate;

    @Schema(description = "导出格式", example = "excel",
            allowableValues = {"excel", "pdf"})
    private String format;
}

@Data
@Schema(description = "导出响应")
public class ExportResponse {
    @Schema(description = "文件下载地址",
            example = "https://cdn.example.com/file.xlsx")
    private String fileUrl;

    @Schema(description = "过期时间（Unix时间戳）", example = "1735689600")
    private Long expiresAt;
}
```

```bash
# 2. 启动应用
$ mvn spring-boot:run
# 应用运行在 http://localhost:8080

# 3. 生成契约
$ aceflow contract generate --feature user-export

执行流程：
  1. 从 http://localhost:8080/v3/api-docs 获取 OpenAPI
  2. 根据 config.yaml 过滤接口
  3. 智能补全缺失的示例（UUID、时间格式、字符串长度）
  4. 保存到 .aceflow/contracts/user-export.yaml
  5. 显示质量检查结果

输出：
  ✅ 契约生成成功: user-export v1.0
  包含接口: 1个
  • POST /api/reports/export - 导出用户数据

  智能补全:
  • startDate: "2025-01-01" (根据字段名推测日期格式)

  下一步:
  $ aceflow contract push --feature user-export

# 4. 推送契约
$ aceflow contract push --feature user-export --notify li@company.com

执行流程：
  1. 推送到 api-contracts/contracts/active/user-export/
  2. Git commit: "[后端] user-export 契约 v1.0"
  3. 发送通知：
     - 邮件 → li@company.com (详细摘要 + 示例 + Git 链接)
     - 钉钉 → li@company.com (简短提醒)
     - 群聊 → "@李工 接口文档已完成"

# 5. 后端在群里确认
群聊: "@李工 接口文档已完成，请查收"
```

---

### Phase 3: 前端并行开发 (S4)

```bash
# 前端收到通知（邮件 + 钉钉 + 群聊）

# 1. 拉取契约
$ cd frontend-repo/
$ aceflow contract pull --feature user-export

输出：
  ✅ 契约已下载: user-export v1.0

  📋 接口摘要:
  POST /api/reports/export
  请求: userId, startDate, format
  响应: fileUrl, expiresAt

  示例请求:
  {
    "userId": 12345,
    "startDate": "2025-01-01",
    "format": "excel"
  }

  示例响应:
  {
    "fileUrl": "https://cdn.example.com/file.xlsx",
    "expiresAt": 1735689600
  }

  保存位置: .aceflow/contracts/user-export.yaml

# 2. 启动 Mock Server（本地）
$ aceflow mock start --contract user-export

输出：
  ✅ Mock Server 已启动
  契约: user-export v1.0
  地址: http://localhost:4010
  进程: PID 12345

  接口列表:
  • POST http://localhost:4010/api/reports/export

  测试命令:
  curl -X POST http://localhost:4010/api/reports/export \
    -H "Content-Type: application/json" \
    -d '{"userId": 123, "startDate": "2025-01-01", "format": "excel"}'

# 3. 前端开发
// 前端代码
const API_BASE = 'http://localhost:4010';  // Mock Server

fetch(`${API_BASE}/api/reports/export`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    userId: 123,
    startDate: '2025-01-01',
    format: 'excel'
  })
})
.then(res => res.json())
.then(data => {
  console.log(data.fileUrl);     // Mock 返回的示例数据
  console.log(data.expiresAt);   // Mock 返回的示例数据
});

# 4. 前端确认（可选，不强制）
群聊: "✅" 或 "@王工 接口看起来没问题"
```

---

### Phase 4: 契约变更（如果需要）

```bash
# 场景：后端实现时需要调整接口

# 1. 后端修改代码
@Data
@Schema(description = "导出响应")
public class ExportResponse {
    @Schema(description = "文件下载地址", example = "https://...")
    private String fileUrl;

    @Schema(description = "过期时间", example = "1735689600")
    private Long expiresAt;

    // 新增字段
    @Schema(description = "数据总条数", example = "1000")
    private Integer totalCount;  // ← 新增
}

# 2. 重新生成契约
$ aceflow contract generate --feature user-export \
    --message "添加 totalCount 字段（前端李工建议）"

检测变更：
  ✅ 非破坏性变更（向后兼容）
  + 新增字段: totalCount (整数，可选)

  版本升级: v1.0 → v1.1

# 3. 推送新版本
$ aceflow contract push --feature user-export

通知内容：
  【接口契约更新】user-export v1.1

  变更类型: ✅ 安全更新（向后兼容）

  变更内容:
  + 新增字段: totalCount (整数，可选)
    说明: 导出数据的总条数

  影响评估: 前端代码无需修改，可选择是否使用新字段

  Git Diff: https://git.company.com/.../diff/v1.0...v1.1

# 4. 前端更新
$ aceflow contract pull --feature user-export

提示：
  ✅ 契约已更新: v1.0 → v1.1
  ✅ 非破坏性变更
  + 新增字段: totalCount

  ⚠️ Mock Server 检测:
  当前运行版本: v1.0
  最新契约版本: v1.1

  需要重启 Mock Server:
  $ aceflow mock restart --contract user-export

# 5. 前端重启 Mock（如果需要使用新字段）
$ aceflow mock restart --contract user-export

输出：
  ✅ Mock Server 已重启
  契约: user-export v1.1
  变更: + totalCount
```

---

### Phase 5: 联调与契约测试 (S7)

```bash
# 1. 后端开发完成，部署到测试环境
# 后端: http://test-backend.com

# 2. 前端切换到真实后端
// const API_BASE = 'http://localhost:4010';  // Mock
const API_BASE = 'http://test-backend.com';     // 真实后端

# 3. 运行契约测试
$ aceflow contract test \
    --feature user-export \
    --backend http://test-backend.com

执行流程：
  1. 读取契约: user-export v1.1
  2. 调用后端接口
  3. 验证请求/响应格式

输出：
  ✅ 测试: POST /api/reports/export
  ✅ 请求格式验证: 通过
  ✅ 响应格式验证: 通过
  ✅ 字段类型验证: 通过
    - fileUrl: string ✅
    - expiresAt: integer ✅
    - totalCount: integer ✅

  ✅ 所有测试通过！后端实现符合契约。

# 如果有问题：
  ❌ 响应格式验证: 失败
    - expiresAt: 预期 integer，实际 string

  建议:
    1. 检查后端实现
    2. 或更新契约以匹配实际实现

# 4. 停止 Mock Server（可选）
$ aceflow mock stop --contract user-export

输出：
  ✅ Mock Server 已停止 (PID 12345)
```

---

## ⚙️ 技术实现细节

### 1. 后端契约生成配置

**配置文件**: `backend-repo/.aceflow/config.yaml`

```yaml
aceflow:
  project:
    name: "用户管理系统后端"
    openapi_url: "http://localhost:8080/v3/api-docs"

  # 需求与接口映射
  features:
    user-export:
      name: "用户数据导出"
      jira: "PROJ-1234"
      frontend: "li@company.com"

      # 接口过滤规则
      include:
        - path: "/api/reports/export"      # 精确路径
        - path_prefix: "/api/reports/"     # 路径前缀

      exclude:
        - path: "/api/reports/internal/*"  # 排除内部接口

  # 智能补全配置
  smart_completion:
    enabled: true

    # 示例数据规则
    example_rules:
      # UUID 字符串
      uuid_pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
      uuid_example: "550e8400-e29b-41d4-a716-446655440000"

      # 时间格式
      date_pattern: "\\d{4}-\\d{2}-\\d{2}"
      date_example: "2025-01-01"

      datetime_pattern: "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"
      datetime_example: "2025-01-01T10:00:00Z"

      # 字符串长度
      default_string_length: 50

      # 根据字段名推测
      user_id: 12345
      username: "zhangsan"
      email: "zhangsan@example.com"
      phone: "13800138000"

  # 契约仓库配置
  contract_repo:
    url: "git@company.com:api-contracts.git"
    branch: "main"
    base_path: "contracts/active"
```

---

### 2. 通知机制

**邮件通知（默认）**：

```
主题: 【接口契约】用户数据导出 - 已更新 v1.0

李工，你好！

后端已完成接口设计，请查看并确认：

需求信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  需求名称：用户数据导出
  需求编号：PROJ-1234
  后端负责人：王工 (wang@company.com)
  前端负责人：李工 (li@company.com)
  契约版本：v1.0
  更新时间：2025-01-01 15:30:00

接口摘要：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  + 新增接口：POST /api/reports/export

  请求参数：
    - userId (必填，整数): 用户ID
    - startDate (必填，日期): 开始日期，格式 YYYY-MM-DD
    - format (必填，枚举): 导出格式，可选值：excel, pdf

  响应字段：
    - fileUrl (字符串): 文件下载地址
    - expiresAt (整数): 过期时间（Unix时间戳）

  示例请求：
  {
    "userId": 12345,
    "startDate": "2025-01-01",
    "format": "excel"
  }

  示例响应：
  {
    "fileUrl": "https://cdn.example.com/exports/user_12345.xlsx",
    "expiresAt": 1735689600
  }

快速开始：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # 拉取契约并启动 Mock Server
  $ cd frontend-repo/
  $ aceflow contract pull --feature user-export
  $ aceflow mock start --contract user-export

  Mock Server 地址：http://localhost:4010

查看详情：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  完整契约文件：
  https://git.company.com/api-contracts/.../openapi.yaml

  Git Commit：
  https://git.company.com/api-contracts/commit/abc123

如何反馈：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 如无问题，请在群里回复 "✅"
  2. 如有建议，请联系后端王工或在 Git 上留言
```

**钉钉/企微通知（简短）**：

```
【接口契约更新】

需求：用户数据导出 v1.0
后端：@王工
前端：@李工

变更：新增 POST /api/reports/export

详细信息请查看邮件
```

**群聊通知（保留习惯）**：

```
@李工 接口文档已完成

需求：用户数据导出 v1.0
详情：https://git.company.com/api-contracts/.../openapi.yaml

快速使用：
cd frontend-repo && aceflow contract pull --feature user-export

请确认或提建议 👍
```

---

### 3. Mock Server 设计

**部署位置**：本地（前端开发机）

**Mock 数据来源**：基于 OpenAPI 的 `example` 字段

**基本命令**：

```bash
# 启动
$ aceflow mock start --contract user-export
  → http://localhost:4010

# 重启（使用新契约版本）
$ aceflow mock restart --contract user-export

# 停止
$ aceflow mock stop --contract user-export

# 查看所有运行的 Mock Server
$ aceflow mock list

# 支持多个并行 Mock（不同端口）
$ aceflow mock start --contract user-export --port 4010
$ aceflow mock start --contract report-dashboard --port 4011
```

**持久化**：不自动恢复，需要手动重启

---

### 4. 契约变更检测

**破坏性变更（Breaking Change）**：

- 删除字段
- 修改字段类型
- 修改字段名
- 将可选字段改为必填
- 修改枚举值（删除某个值）

**非破坏性变更（Backward Compatible）**：

- 新增可选字段
- 扩展枚举值（新增值）
- 将必填字段改为可选
- 添加新接口

**版本号规则**：

- 破坏性变更：主版本升级（v1.0 → v2.0）
- 非破坏性变更：次版本升级（v1.0 → v1.1）

---

### 5. Review 机制

**核心原则**：不强制 Review，但 Review 是必要的

**确认方式**：
1. **主要**：前端在群里回复 "✅"
2. **可选**：在 Git Commit 上留言（不强制）

**记录方式**：
- Git 历史记录所有契约变更
- 群聊记录确认过程
- 不引入复杂的状态跟踪

---

## 📋 核心命令清单

### 后端命令

```bash
# 初始化
$ aceflow init

# 添加需求配置
$ aceflow feature add

# 生成契约
$ aceflow contract generate --feature <feature-name>
$ aceflow contract generate --feature user-export --message "描述"

# 推送契约
$ aceflow contract push --feature <feature-name> --notify <email>

# 查看契约
$ aceflow contract show --feature <feature-name>
```

### 前端命令

```bash
# 拉取契约
$ aceflow contract pull --feature <feature-name>

# 启动 Mock Server
$ aceflow mock start --contract <feature-name>
$ aceflow mock start --contract <feature-name> --port 4010

# 重启 Mock Server
$ aceflow mock restart --contract <feature-name>

# 停止 Mock Server
$ aceflow mock stop --contract <feature-name>

# 查看运行的 Mock Server
$ aceflow mock list

# Review 契约（可选）
$ aceflow contract review --feature <feature-name> --comment "建议..."
```

### 测试命令

```bash
# 契约测试
$ aceflow contract test --feature <feature-name> --backend <url>
```

---

## 🎯 成功标准

### 解决的核心痛点

1. ✅ **文档不够清晰**
   - OpenAPI 提供精确的类型定义
   - 示例数据减少沟通成本
   - 枚举值和约束明确

2. ✅ **前端意见被忽略**
   - Git 记录所有变更
   - 变更可见、可追溯
   - 通知机制及时

3. ✅ **文档与代码不一致**
   - 从代码生成契约，保证一致性
   - 契约测试验证实现符合性

4. ✅ **盲开发返工**
   - Mock Server 让前端提前验证
   - 基于真实示例数据开发

### 预期收益

- **90%+ 的问题得到解决**（基于讨论结论）
- **减少联调返工**：前端基于 Mock 开发，接口一致性高
- **提升沟通效率**：清晰的契约文档 + 自动通知
- **可追溯性**：Git 记录所有变更历史
- **零迁移成本**：不改变现有仓库结构

---

## 🚀 实施计划

### 第一阶段：基础能力（MVP）

**目标**：核心流程跑通

**功能清单**：
1. 后端契约生成（从 Spring Boot OpenAPI）
2. 契约推送到 Git
3. 前端契约拉取
4. Mock Server 启动（本地）
5. 基础通知（邮件）

**技术要点**：
- 读取 Spring Boot `/v3/api-docs` 端点
- 基于配置文件过滤接口
- 简单的智能补全（日期、UUID）
- Git 操作（clone, commit, push）
- Mock Server 基于 OpenAPI（可使用 Prism 等工具）

**验证标准**：
- 能完成一个完整的需求流程
- 后端生成 → 推送 → 前端拉取 → Mock Server

---

### 第二阶段：增强体验

**目标**：完善细节，提升易用性

**功能清单**：
1. 契约变更检测（破坏性 vs 非破坏性）
2. 版本管理（自动升级版本号）
3. 完整通知（邮件 + 钉钉）
4. 契约测试（基础验证）
5. 智能补全规则增强

**技术要点**：
- OpenAPI diff 算法
- 语义化版本号
- 钉钉 Webhook 集成
- 契约测试工具（可使用 Schemathesis 等）

---

### 第三阶段：生态完善

**目标**：扩展能力，支持更多场景

**功能清单**：
1. TypeScript 类型生成
2. 多技术栈支持（Go, Node.js）
3. CI/CD 集成
4. 契约测试增强
5. 可视化界面

**优先级**：根据实际使用反馈调整

---

## 📝 注意事项

### 对后端的要求

1. **代码规范**：Swagger 注解必须完整
   - `@Schema` 的 `description`（必须）
   - `@Schema` 的 `example`（必须）
   - `@Schema` 的 `allowableValues`（枚举时必须）
   - `@Schema` 的 `required`（建议）

2. **应用启动**：生成契约前需要启动应用

3. **配置维护**：维护 `.aceflow/config.yaml` 中的需求映射

### 对前端的要求

1. **主动拉取**：收到通知后主动拉取契约
2. **群里确认**：Review 后在群里回复确认
3. **Mock Server 管理**：手动启动/停止 Mock Server

### 对团队的要求

1. **沟通习惯**：保持群里沟通的习惯
2. **Git 使用**：熟悉基本的 Git 操作
3. **规范遵守**：双方都要遵守契约约定

---

## 🔚 总结

**核心理念**：
- ✅ 最小侵入：不改变现有仓库结构
- ✅ 渐进式：可以从一个需求试点
- ✅ 灵活务实：不强制流程，鼓励协作
- ✅ 自动化：减少人工同步工作

**关键成功因素**：
- OpenAPI 作为 Single Source of Truth
- 轻量级通知 + 可追溯
- Mock Server 让前端独立开发
- 智能补全降低使用门槛

**一口气吃不成胖子**：
- 先把核心流程做好
- 根据实际使用反馈迭代优化
- 逐步完善细节功能

---

**文档结束**

*本文档是 AceFlow 前后端协作功能的最终设计方案，可以作为开发的指导文档。*
