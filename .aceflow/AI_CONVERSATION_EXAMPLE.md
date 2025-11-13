# AceFlow 纯提示词驱动 - AI对话示例

> **场景**: 开发"用户登录"功能，使用Standard模式
> **工具**: Cline / Claude Code (配置了System Prompt)
> **模式**: Standard (7阶段)

---

## 📋 完整对话流程

### 第1步: 用户启动新迭代

```
👤 User:
开始一个新功能开发

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！我将帮你启动一个新的AceFlow工作流。

请确认以下信息：

📝 基本信息
├─ 功能名称: [请输入，例如: 用户登录功能]
├─ 工作流模式:
│  • Standard (7阶段) - 日常开发，5-10天
│  • Complete (10阶段) - 大型项目，2-4周
└─ 迭代ID: [建议: iter_20250113_001]

💡 提示: 如果不确定模式，我可以根据功能描述推荐。
```

---

### 第2步: 用户提供信息

```
👤 User:
- 功能名称: 用户登录功能
- 模式: Standard
- 迭代ID: iter_20250113_001

────────────────────────────────────────────────────────

🤖 AI Assistant:
✅ 收到！正在初始化工作流...

[创建目录]
mkdir -p aceflow_result/iter_20250113_001/standard

[生成状态文件]
已创建: aceflow_result/iter_20250113_001/WORKFLOW_STATE.md

────────────────────────────────────────────────────────

📊 工作流已初始化

项目: 用户登录功能
迭代: iter_20250113_001
模式: Standard (7阶段)

工作流阶段:
1. user_stories      - 用户故事
2. task_breakdown    - 任务分解
3. test_design       - 测试设计
4. implementation    - 功能实现
5. unit_test         - 单元测试
6. integration_test  - 集成测试
7. code_review       - 代码审查

────────────────────────────────────────────────────────

🚀 现在进入第一阶段: user_stories (用户故事)

[读取模板]
正在读取: .aceflow/templates/standard/user_stories.md

我将基于模板为"用户登录功能"生成用户故事。请稍候...
```

---

### 第3步: AI自动生成第一阶段文档

```
🤖 AI Assistant:
✅ 已完成用户故事生成！

[保存文档]
aceflow_result/iter_20250113_001/standard/user_stories.md

────────────────────────────────────────────────────────

📄 生成内容预览:

# 用户故事

> **项目**: 用户登录功能
> **日期**: 2025-01-13

## 故事概览

| ID | 故事标题 | 优先级 | 故事点 | 状态 |
|----|---------|--------|--------|------|
| US-001 | 用户名密码登录 | P0 | 3 | 待开发 |
| US-002 | 记住登录状态 | P1 | 2 | 待开发 |
| US-003 | 登录失败提示 | P0 | 1 | 待开发 |

---

## US-001: 用户名密码登录

**作为** 系统用户
**我希望** 使用用户名和密码登录系统
**以便** 访问个人账户和受保护的功能

### 验收标准
| 场景 | Given (前置条件) | When (操作) | Then (预期结果) |
|-----|----------------|------------|----------------|
| 正常流程 | 用户在登录页面，已注册账号 | 输入正确的用户名和密码，点击登录 | 成功登录，跳转到首页，显示用户信息 |
| 异常流程 | 用户在登录页面 | 输入错误的密码 | 显示"用户名或密码错误"，登录失败 |

### 补充说明
- **优先级**: P0
- **故事点**: 3
- **依赖**: 无
- **技术考虑**: 使用JWT认证，密码需BCrypt加密

---

[查看完整文档请打开文件]

────────────────────────────────────────────────────────

📊 进度更新: 1/7 (14%)

✅ user_stories (刚刚完成)
⏳ task_breakdown
⏳ test_design
⏳ implementation
⏳ unit_test
⏳ integration_test
⏳ code_review

────────────────────────────────────────────────────────

💡 下一阶段: task_breakdown (任务分解)

我将基于刚生成的用户故事，分解具体的开发任务。

是否继续？或者你想先审查用户故事文档？
```

---

### 第4步: 用户确认继续

```
👤 User:
继续

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！进入第二阶段: task_breakdown (任务分解)

[读取前置文档]
正在读取: aceflow_result/iter_20250113_001/standard/user_stories.md

[读取模板]
正在读取: .aceflow/templates/standard/task_breakdown.md

基于3个用户故事，我将分解具体的开发任务...
```

---

### 第5步: AI生成任务分解

```
🤖 AI Assistant:
✅ 任务分解已完成！

[保存文档]
aceflow_result/iter_20250113_001/standard/task_breakdown.md

────────────────────────────────────────────────────────

📄 任务分解摘要:

## 任务统计
- 总任务数: 12个
- 前端任务: 5个
- 后端任务: 5个
- 测试任务: 2个
- 总工时估算: 38小时 (~5个工作日)

## 核心任务

| 任务ID | 任务描述 | 负责方 | 工时 | 依赖 | 优先级 |
|-------|---------|--------|------|------|--------|
| T-001 | 设计数据库User表结构 | 后端 | 2h | - | P0 |
| T-002 | 实现用户注册API | 后端 | 4h | T-001 | P0 |
| T-003 | 实现登录API (JWT) | 后端 | 4h | T-001 | P0 |
| T-004 | 实现Token刷新机制 | 后端 | 3h | T-003 | P1 |
| T-005 | 登录页面UI组件 | 前端 | 5h | - | P0 |
| T-006 | 登录状态管理 | 前端 | 3h | T-005 | P0 |
| T-007 | 记住登录功能 | 前端 | 3h | T-006 | P1 |
| T-008 | 错误提示组件 | 前端 | 2h | T-005 | P0 |
| ... | ... | ... | ... | ... | ... |

[查看完整任务清单请打开文件]

────────────────────────────────────────────────────────

🔗 Contract-First提醒:

💡 建议在开始implementation之前：
1. 生成OpenAPI合同 (定义登录相关API)
2. 推送到Git合同仓库
3. 启动Mock Server供前端使用

这样前后端可以并行开发，提升效率！

是否现在生成OpenAPI合同？
(回答"是"或"跳过"，或者继续下一阶段)
```

---

### 第6步: 用户选择生成合同

```
👤 User:
是，生成合同

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！基于任务分解中的API需求，我将生成OpenAPI合同。

[分析API需求]
从任务分解中识别到以下API:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/refresh
- GET  /api/auth/me

[生成OpenAPI 3.0合同]
正在生成: user_login_openapi.yaml
```

---

### 第7步: AI生成OpenAPI合同

```
🤖 AI Assistant:
✅ OpenAPI合同已生成！

[保存合同]
aceflow_result/iter_20250113_001/contract/user_login_openapi.yaml

────────────────────────────────────────────────────────

📄 OpenAPI合同摘要:

openapi: 3.0.0
info:
  title: 用户登录API
  version: 1.0.0

servers:
  - url: http://localhost:8080/api
    description: 本地开发服务器

paths:
  /auth/login:
    post:
      summary: 用户登录
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username: { type: string }
                password: { type: string }
                remember_me: { type: boolean }
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: { type: string }
                  refresh_token: { type: string }
                  user: { $ref: '#/components/schemas/User' }

[查看完整合同请打开文件]

────────────────────────────────────────────────────────

🚀 下一步建议:

1. 推送合同到Git仓库:
   aceflow contract push --feature user-login

2. 启动Mock Server:
   aceflow mock start --feature user-login --port 4010

3. 前端即可访问: http://localhost:4010/api

是否需要我继续下一个工作流阶段(test_design)？
或者你想先手动执行合同推送和Mock Server启动？
```

---

### 第8步: 用户继续工作流

```
👤 User:
跳过合同推送，继续工作流

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！继续推进工作流。

📊 当前进度: 2/7 (29%)

✅ user_stories
✅ task_breakdown
🔄 test_design (即将开始)
⏳ implementation
⏳ unit_test
⏳ integration_test
⏳ code_review

────────────────────────────────────────────────────────

🚀 进入第三阶段: test_design (测试设计)

[读取前置文档]
- user_stories.md (3个用户故事)
- task_breakdown.md (12个任务)

[读取模板]
.aceflow/templates/standard/test_design.md

我将设计测试用例覆盖所有用户故事...
```

---

### 第9步: AI生成测试设计

```
🤖 AI Assistant:
✅ 测试设计已完成！

[保存文档]
aceflow_result/iter_20250113_001/standard/test_design.md

────────────────────────────────────────────────────────

📄 测试设计摘要:

## 测试策略

| 测试类型 | 优先级 | 覆盖范围 | 目标 |
|---------|--------|---------|------|
| 单元测试 | P0 | 所有业务逻辑 | 覆盖率 ≥80% |
| 集成测试 | P0 | API端到端流程 | 通过率 ≥95% |
| UI测试 | P1 | 关键用户路径 | 无阻塞性问题 |

## 测试用例统计
- 单元测试用例: 18个
  - 后端API: 10个
  - 前端组件: 5个
  - 工具函数: 3个

- 集成测试用例: 8个
  - 登录流程: 3个
  - Token刷新: 2个
  - 错误处理: 3个

## 核心测试用例

### 单元测试

| 用例ID | 测试对象 | 测试场景 | 输入 | 预期输出 |
|-------|---------|---------|------|---------|
| UT-001 | POST /auth/login | 正确的用户名密码 | {username:"admin", password:"123456"} | 200, {access_token, refresh_token} |
| UT-002 | POST /auth/login | 错误的密码 | {username:"admin", password:"wrong"} | 401, {error:"用户名或密码错误"} |
| UT-003 | POST /auth/login | 不存在的用户 | {username:"nobody", password:"123456"} | 401, {error:"用户名或密码错误"} |

[查看完整测试用例请打开文件]

────────────────────────────────────────────────────────

📊 进度更新: 3/7 (43%)

✅ user_stories
✅ task_breakdown
✅ test_design
⏳ implementation
⏳ unit_test
⏳ integration_test
⏳ code_review

────────────────────────────────────────────────────────

💡 下一阶段: implementation (功能实现)

这个阶段需要你实际编写代码。我可以：
1. 基于任务分解生成代码框架
2. 提供关键代码片段参考
3. 等你完成实现后，记录实现要点

你希望我做什么？
```

---

### 第10步: 用户请求代码框架

```
👤 User:
生成后端登录API的代码框架（使用FastAPI）

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！基于你的项目使用FastAPI，我将生成登录API的代码框架。

[检测项目结构]
发现: requirements.txt, src/backend/

[生成代码框架]
```

---

### 第11步: AI生成代码框架

````
🤖 AI Assistant:
✅ 代码框架已生成！

────────────────────────────────────────────────────────

📁 文件结构:

src/backend/
├── models/
│   └── user.py          # User数据模型
├── routes/
│   └── auth.py          # 认证路由
├── services/
│   └── auth_service.py  # 认证业务逻辑
├── utils/
│   └── security.py      # 安全工具(JWT, BCrypt)
└── main.py              # FastAPI应用入口

────────────────────────────────────────────────────────

📄 核心代码:

**src/backend/routes/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services import auth_service
from ..utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录API

    对应用户故事: US-001 用户名密码登录
    对应任务: T-003 实现登录API
    """
    # TODO: 实现登录逻辑
    user = await auth_service.authenticate_user(
        request.username,
        request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成Token
    access_token = create_access_token(
        data={"sub": user.username}
    )

    # 根据remember_me决定refresh_token过期时间
    refresh_token_expires = (
        7 * 24 * 60 if request.remember_me else 24 * 60
    )

    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

# TODO: 实现其他API (logout, refresh, me)
```

[完整代码框架请查看生成的文件]

────────────────────────────────────────────────────────

💡 实现要点:

1. ✅ 遵循OpenAPI合同规范
2. ✅ 使用BCrypt加密密码
3. ✅ JWT Token包含用户信息
4. ✅ remember_me控制Token过期时间
5. ⚠️  需要实现: auth_service.authenticate_user()
6. ⚠️  需要实现: 数据库User模型

────────────────────────────────────────────────────────

下一步:
1. 完善TODO部分的代码
2. 完成后告诉我，我会更新implementation文档
3. 或者继续生成前端代码框架
````

---

### 第12步: 用户完成实现

```
👤 User:
代码已实现完成，更新implementation文档

────────────────────────────────────────────────────────

🤖 AI Assistant:
太好了！让我记录实现要点。

[检查代码变更]
扫描 src/backend/ 目录...

[生成实现文档]
```

---

### 第13步: AI生成实现文档

```
🤖 AI Assistant:
✅ 实现文档已生成！

[保存文档]
aceflow_result/iter_20250113_001/standard/implementation.md

────────────────────────────────────────────────────────

📄 实现摘要:

# 功能实现

## 实现统计
- 实现任务: 12/12 (100%)
- 新增文件: 15个
- 代码行数: ~800行
- 关键技术: FastAPI, JWT, BCrypt, SQLAlchemy

## 后端实现

### API接口 (符合OpenAPI合同)
| 接口 | 路由 | 状态 | 说明 |
|-----|------|------|------|
| 登录 | POST /api/auth/login | ✅ | JWT认证，返回access_token |
| 登出 | POST /api/auth/logout | ✅ | 清除Token |
| 刷新 | POST /api/auth/refresh | ✅ | 使用refresh_token获取新token |
| 获取用户信息 | GET /api/auth/me | ✅ | 需要Authorization header |

### 数据库设计
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 安全措施
- ✅ 密码使用BCrypt加密 (cost factor: 12)
- ✅ JWT Token签名验证
- ✅ Token过期时间: access(1h), refresh(7d)
- ✅ 登录失败锁定机制 (3次失败锁定10分钟)
- ✅ CORS配置正确

## 前端实现

### 页面组件
- LoginPage.tsx - 登录页面
- LoginForm.tsx - 登录表单
- ErrorAlert.tsx - 错误提示

### 状态管理
- useAuth hook - 管理认证状态
- localStorage - 持久化Token (remember_me)

[查看完整实现文档请打开文件]

────────────────────────────────────────────────────────

📊 进度更新: 4/7 (57%)

✅ user_stories
✅ task_breakdown
✅ test_design
✅ implementation
🔄 unit_test (下一步)
⏳ integration_test
⏳ code_review

────────────────────────────────────────────────────────

💡 下一阶段: unit_test (单元测试)

我将基于test_design中的测试用例，帮你执行单元测试并记录结果。

是否继续？
```

---

### 第14步: 执行测试阶段

```
👤 User:
继续，运行单元测试

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！开始执行单元测试。

[读取测试设计]
测试用例: 18个单元测试

[执行测试命令]
$ pytest tests/unit/ -v --cov=src/backend --cov-report=term

────────────────────────────────────────────────────────

执行中...
```

---

### 第15步: AI记录测试结果

```
🤖 AI Assistant:
✅ 单元测试已完成！

────────────────────────────────────────────────────────

📊 测试结果:

tests/unit/test_auth_api.py::test_login_success PASSED
tests/unit/test_auth_api.py::test_login_wrong_password FAILED
tests/unit/test_auth_api.py::test_login_user_not_found PASSED
tests/unit/test_auth_api.py::test_refresh_token PASSED
tests/unit/test_auth_service.py::test_authenticate_user PASSED
tests/unit/test_auth_service.py::test_hash_password PASSED
tests/unit/test_security.py::test_create_jwt_token PASSED
tests/unit/test_security.py::test_verify_jwt_token PASSED

────────────────────────────────────────────────────────

📈 统计:
- 总计: 18个
- 通过: 17个 ✅
- 失败: 1个 ❌
- 跳过: 0个
- 通过率: 94.4%
- 代码覆盖率: 87%

────────────────────────────────────────────────────────

❌ 失败用例分析:

**test_login_wrong_password**
- 期望: 401 Unauthorized
- 实际: 500 Internal Server Error
- 原因: auth_service中未正确处理密码校验异常
- 修复建议: 在authenticate_user中添加try-catch

────────────────────────────────────────────────────────

⚠️ 质量检查:
- [❌] 通过率未达标 (目标: 100%, 实际: 94.4%)
- [✅] 覆盖率达标 (目标: ≥80%, 实际: 87%)

建议: 修复失败用例后重新运行测试

是否修复后重新测试？还是先继续记录当前结果？
```

---

### 第16步: 用户修复后继续

```
👤 User:
已修复，重新运行测试

────────────────────────────────────────────────────────

🤖 AI Assistant:
[重新执行测试]
$ pytest tests/unit/ -v --cov=src/backend --cov-report=term

────────────────────────────────────────────────────────

✅ 测试全部通过！

📊 最终结果:
- 总计: 18个
- 通过: 18个 ✅
- 失败: 0个
- 通过率: 100% 🎉
- 代码覆盖率: 89%

────────────────────────────────────────────────────────

[保存测试报告]
aceflow_result/iter_20250113_001/standard/unit_test.md

────────────────────────────────────────────────────────

✅ 质量检查通过:
- [✅] 通过率: 100%
- [✅] 覆盖率: 89% (≥80%)

📊 进度更新: 5/7 (71%)

✅ user_stories
✅ task_breakdown
✅ test_design
✅ implementation
✅ unit_test
🔄 integration_test (下一步)
⏳ code_review

────────────────────────────────────────────────────────

💡 下一阶段: integration_test (集成测试)

集成测试将测试完整的API流程（前后端联调）。

是否继续？
```

---

### 第17步: 快速完成剩余阶段

```
👤 User:
继续完成剩余阶段

────────────────────────────────────────────────────────

🤖 AI Assistant:
好的！我将快速完成剩余两个阶段。

────────────────────────────────────────────────────────

[Stage 6/7] integration_test (集成测试)

[执行集成测试]
$ pytest tests/integration/ -v

结果:
- 8个场景全部通过 ✅
- API端到端流程正常
- 前后端联调成功

[保存文档]
aceflow_result/iter_20250113_001/standard/integration_test.md

────────────────────────────────────────────────────────

[Stage 7/7] code_review (代码审查)

[执行代码质量检查]
- pylint: 8.5/10 ✅
- 安全扫描: 无严重漏洞 ✅
- 代码规范: 95%符合PEP8 ✅

[性能分析]
- 登录API平均响应: 85ms ✅
- 并发100用户: 无性能问题 ✅

[保存文档]
aceflow_result/iter_20250113_001/standard/code_review.md

────────────────────────────────────────────────────────

🎉 工作流已完成！

📊 最终进度: 7/7 (100%)

✅ user_stories
✅ task_breakdown
✅ test_design
✅ implementation
✅ unit_test
✅ integration_test
✅ code_review

────────────────────────────────────────────────────────

[生成工作流摘要]
aceflow_result/iter_20250113_001/SUMMARY.md

[更新最终状态]
WORKFLOW_STATE.md: status → completed
```

---

### 第18步: AI展示完成摘要

```
🤖 AI Assistant:
🎉🎉🎉 恭喜！"用户登录功能"工作流已全部完成！

────────────────────────────────────────────────────────

📋 完成摘要

**项目**: 用户登录功能
**迭代**: iter_20250113_001
**模式**: Standard (7阶段)
**开始时间**: 2025-01-13 09:00:00
**完成时间**: 2025-01-13 14:30:00
**总耗时**: 5.5小时

────────────────────────────────────────────────────────

📄 产出物清单

aceflow_result/iter_20250113_001/
├── standard/
│   ├── user_stories.md        ✅ 3个用户故事
│   ├── task_breakdown.md      ✅ 12个开发任务
│   ├── test_design.md         ✅ 26个测试用例
│   ├── implementation.md      ✅ ~800行代码
│   ├── unit_test.md           ✅ 100%通过，89%覆盖
│   ├── integration_test.md    ✅ 8个场景通过
│   └── code_review.md         ✅ 8.5/10评分
├── contract/
│   └── user_login_openapi.yaml ✅ OpenAPI 3.0合同
├── WORKFLOW_STATE.md          ✅ 状态: completed
└── SUMMARY.md                 ✅ 完整摘要

────────────────────────────────────────────────────────

📊 质量指标

- 用户故事: 3个，覆盖完整
- 开发任务: 12个，全部完成
- 测试用例: 26个
- 单元测试通过率: 100%
- 代码覆盖率: 89%
- 集成测试通过率: 100%
- 代码审查评分: 8.5/10

────────────────────────────────────────────────────────

💡 建议下一步

1. **提交到Git**（可选）:
   ```bash
   git add aceflow_result/iter_20250113_001/
   git commit -m "docs: 用户登录功能完整工作流文档"
   ```

2. **部署上线**:
   - 前端: 部署LoginPage组件
   - 后端: 部署认证API
   - 数据库: 执行User表迁移

3. **开始新迭代**:
   如果有其他功能需求，可以开始新的迭代：
   ```
   开始新功能开发
   ```

────────────────────────────────────────────────────────

感谢使用AceFlow！🚀

所有文档已保存，随时可以回顾查看。
```

---

## 📊 对话流程总结

### 阶段时间线

```
09:00 ─┬─ 用户启动新迭代
       │
09:05 ─┼─ [Stage 1] user_stories 生成
       │
09:30 ─┼─ [Stage 2] task_breakdown 生成
       │
09:45 ─┼─ [Contract] OpenAPI合同生成
       │
10:00 ─┼─ [Stage 3] test_design 生成
       │
10:30 ─┼─ [Stage 4] implementation (用户实现代码)
       │
13:00 ─┼─ [Stage 5] unit_test 执行
       │
13:30 ─┼─ [Stage 6] integration_test 执行
       │
14:00 ─┼─ [Stage 7] code_review 执行
       │
14:30 ─┴─ 工作流完成，生成摘要
```

### 用户交互次数

总共 **18次** 对话:
- 启动和配置: 2次
- 阶段推进: 7次
- 合同生成: 2次
- 代码实现: 2次
- 测试执行: 3次
- 确认和完成: 2次

### AI自动化操作

- ✅ 自动读取模板
- ✅ 自动生成文档
- ✅ 自动保存文件
- ✅ 自动更新状态
- ✅ 自动推进阶段
- ✅ 自动质量检查
- ✅ 自动生成摘要

---

## 💡 关键要点

### 1. 状态追踪自动化

AI自动维护 `WORKFLOW_STATE.md`，用户无需手动管理状态。

### 2. 阶段连贯性

每个阶段都基于前一阶段的输出，形成完整的文档链。

### 3. 主动推进

AI完成当前阶段后，主动提示下一步，用户只需确认"继续"。

### 4. 质量把关

每个阶段都有质量检查点，不达标会提示重新生成。

### 5. 灵活控制

用户可以随时:
- 查看进度
- 跳过阶段
- 回退修改
- 暂停继续

---

**🎯 这就是纯提示词驱动的完整工作流！**

用户只需配置System Prompt，AI就能自动按AceFlow标准管理整个开发流程。
