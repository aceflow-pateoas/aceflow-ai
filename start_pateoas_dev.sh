#!/bin/bash

# PATEOAS增强的AceFlow + Cline 快速启动脚本
# 基于PATEOAS v3.0增强引擎的智能开发环境

echo "🚀 PATEOAS增强的AceFlow + Cline 开发环境启动"
echo "=================================================="
echo "基于PATEOAS v3.0增强引擎 | $(date)"
echo ""

# 检查是否在项目根目录
if [ ! -f "enhanced_cli.py" ]; then
    echo "❌ 错误：请在AceFlow PATEOAS项目根目录运行此脚本"
    echo "   (应该包含 enhanced_cli.py 文件)"
    exit 1
fi

# 检查PATEOAS增强引擎状态
echo "🧠 检查PATEOAS增强引擎状态..."
if python3 enhanced_cli.py pateoas status &> /dev/null; then
    echo "✅ PATEOAS增强引擎运行正常"
else
    echo "⚠️  PATEOAS增强引擎可能需要初始化"
    echo "   建议先运行: python3 debug_pateoas_integration.py"
fi

# 检查VSCode是否安装
echo ""
echo "🔍 检查开发环境..."
if command -v code &> /dev/null; then
    echo "✅ VSCode已安装"
    
    # 检查Cline扩展
    if code --list-extensions | grep -q "saoudrizwan.claude-dev"; then
        echo "✅ Cline扩展已安装"
    else
        echo "📦 Cline扩展未安装，正在安装..."
        code --install-extension saoudrizwan.claude-dev
    fi
else
    echo "❌ VSCode未安装"
    echo "   请先安装VSCode: https://code.visualstudio.com/"
    exit 1
fi

# 启动环境
echo ""
echo "🚀 启动PATEOAS增强开发环境..."

# 设置环境变量
export PYTHONPATH="./pateoas:./scripts:."
export ACEFLOW_PROJECT_ROOT="."
export PATEOAS_CONFIG_PATH="./config/pateoas.yaml"
export ACEFLOW_PATEOAS_MODE="enhanced"

echo "📝 打开VSCode工作区..."
code aceflow-pateoas-workspace.code-workspace

# 显示使用提示
echo ""
echo "🎉 PATEOAS增强开发环境已启动！"
echo "=================================="
echo ""
echo "💡 快速开始体验PATEOAS功能："
echo "1. 等待VSCode完全加载完成"
echo "2. 启动Cline扩展 (Ctrl+Shift+P -> Cline: Start New Task)"
echo "3. 对Cline说任一以下内容体验智能功能："
echo ""
echo "   🧠 智能状态分析："
echo "   \"检查项目状态\" - 获取PATEOAS增强的项目状态分析"
echo ""
echo "   🎯 智能任务分析："
echo "   \"我需要添加用户登录功能\" - 获取智能任务分析和工作流推荐"
echo ""
echo "   📚 智能记忆召回："
echo "   \"之前我们做过什么相关工作\" - 从项目记忆中智能召回相关信息"
echo ""
echo "   🔧 智能问题诊断："
echo "   \"登录功能有问题\" - 获取自适应错误分析和修复建议"
echo ""
echo "🔧 PATEOAS增强CLI命令："
echo "   • 状态检查: python3 enhanced_cli.py pateoas status"
echo "   • 记忆召回: python3 enhanced_cli.py pateoas memory recall --query '查询内容'"
echo "   • 任务分析: python3 enhanced_cli.py pateoas analyze --task '任务描述'"
echo "   • 决策门评估: python3 enhanced_cli.py pateoas gates evaluate"
echo "   • 工作流优化: python3 enhanced_cli.py pateoas optimize --analyze-workflow"
echo ""
echo "🧪 VSCode任务 (Ctrl+Shift+P -> Tasks: Run Task)："
echo "   • PATEOAS: Status Check - 快速状态检查"
echo "   • PATEOAS: Memory Recall - 智能记忆召回"
echo "   • PATEOAS: Analyze Task - AI任务分析"
echo "   • PATEOAS: Decision Gates Evaluation - 决策门评估"
echo "   • PATEOAS: Full System Test - 完整系统测试"
echo ""
echo "🔍 故障诊断："
echo "   • 运行诊断工具: python3 debug_pateoas_integration.py"
echo "   • 查看集成规则: cat .clinerules/pateoas_integration.md"
echo "   • 检查配置: cat .vscode/settings.json"
echo ""
echo "📚 更多帮助和文档："
echo "   • PATEOAS增强功能文档: cat docs/AceFlow_Cline_Integration_Guide.md"
echo "   • CLI完整帮助: python3 enhanced_cli.py --help"
echo "   • 集成测试: python3 test_pateoas_enhanced_engine_integration.py"
echo ""
echo "🎯 享受基于PATEOAS v3.0增强引擎的智能化开发体验！"