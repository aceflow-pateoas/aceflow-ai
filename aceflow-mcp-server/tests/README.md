# AceFlow Contract Management Tests

## 测试结果（当前状态）

### ✅ 通过的测试

**test_filter.py: 11/11 (100%)** ✅
- 所有契约过滤测试全部通过
- 精确匹配、前缀匹配、正则匹配均正常

**test_mock_server.py: 14/15 (93%)** ⚠️
- Mock Server 大部分功能测试通过
- 1个失败：端口检测相关

**test_completion.py: 9/14 (64%)** ⚠️
- 部分智能补全测试通过
- 5个失败：API 需要调整

**test_config.py: 0/12 (0%)** ❌
- 配置管理测试全部失败
- 问题：ContractConfig 构造函数接受目录路径，但期望config文件路径

### 总体统计

- **单元测试**: 34/52 通过 (65%)
- **集成测试**: 未运行

## 已知问题

### 1. ContractConfig API 不匹配
```python
# 测试中
config = ContractConfig(temp_dir)  # 传入目录

# 实际API
config_file = temp_dir / ".aceflow/config.yaml"
# 需要检查实际构造函数签名
```

### 2. SmartCompletion API 问题
- `get_example_for_property()` 返回值与预期不符
- 需要检查实际方法签名和返回值

### 3. Mock Server 端口检测
- `_is_port_in_use()` 测试失败
- 可能是私有方法访问问题

---

## 测试结构

```
tests/
├── fixtures/          # 测试数据
│   ├── __init__.py
│   └── sample_data.py
├── unit/              # 单元测试
│   ├── __init__.py
│   ├── test_filter.py      # 契约过滤测试
│   ├── test_completion.py  # 智能补全测试
│   ├── test_config.py      # 配置管理测试
│   └── test_mock_server.py # Mock Server 测试
└── integration/       # 集成测试
    ├── __init__.py
    └── test_contract_workflow.py  # 完整工作流测试
```

## 测试内容

### 单元测试

1. **test_filter.py** - 契约过滤功能
   - 精确匹配（exact）
   - 前缀匹配（prefix）
   - 正则匹配（regex）
   - 路径过滤集成

2. **test_completion.py** - 智能补全功能
   - ID 字段匹配
   - 日期字段匹配
   - UUID 字段匹配
   - Email/Phone 匹配
   - 嵌套 schema 处理

3. **test_config.py** - 配置管理
   - 配置加载/保存
   - Feature 增删改查
   - SMTP 配置
   - 契约仓库配置

4. **test_mock_server.py** - Mock Server 管理
   - Prism 检测
   - 服务器启动/停止
   - 端口管理
   - PID 文件跟踪
   - 进程列表

### 集成测试

**test_contract_workflow.py** - 完整工作流
- 契约生成流程
- CLI 命令集成
- 过滤与补全集成
- 端到端测试

## 运行测试

### 前置条件

1. 安装测试依赖：
```bash
pip install pytest pytest-cov
```

2. 或使用虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 运行所有测试

```bash
cd aceflow-mcp-server
pytest tests/
```

### 运行单元测试

```bash
pytest tests/unit/
```

### 运行集成测试

```bash
pytest tests/integration/
```

### 生成覆盖率报告

```bash
pytest tests/ --cov=aceflow_mcp_server --cov-report=html
# 查看报告：open htmlcov/index.html
```

## 注意事项

⚠️ **测试文件需要修复**：
- 当前测试文件中的 API 调用需要根据实际实现进行调整
- `ContractFilter` 构造函数接受字典参数，测试中使用了错误的参数形式
- 需要根据实际代码更新所有测试用例

## TODO

- [ ] 修复所有测试用例中的 API 调用
- [ ] 运行完整测试套件
- [ ] 验证测试覆盖率 > 80%
- [ ] 添加更多边界案例测试
- [ ] 添加性能测试（可选）
