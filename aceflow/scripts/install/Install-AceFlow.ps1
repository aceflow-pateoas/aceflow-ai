# AceFlow v3.0 Windows安装脚本
# 实施方案3: 全局安装初始化脚本，项目级拷贝工作脚本

param(
    [switch]$UserInstall,
    [switch]$SystemInstall, 
    [switch]$Uninstall,
    [switch]$Check,
    [switch]$Help,
    [switch]$Version
)

# 脚本信息
$ScriptName = "Install-AceFlow.ps1"
$ScriptVersion = "3.0.0"
$AceFlowHome = if ($env:ACEFLOW_HOME) { $env:ACEFLOW_HOME } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }

# 颜色函数
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Info { Write-ColorText "ℹ️ [INFO] $args" -Color Cyan }
function Write-Success { Write-ColorText "✅ [SUCCESS] $args" -Color Green }
function Write-Warning { Write-ColorText "⚠️ [WARNING] $args" -Color Yellow }
function Write-Error { Write-ColorText "❌ [ERROR] $args" -Color Red }

function Write-Header {
    Write-Host @"
╔══════════════════════════════════════╗
║       AceFlow v3.0 Windows安装       ║
║        方案3: 混合部署模式           ║ 
╚══════════════════════════════════════╝
"@ -ForegroundColor Magenta
}

# 帮助信息
function Show-Help {
    Write-Host @"
AceFlow v3.0 Windows安装脚本 - 方案3实施

用法: .\$ScriptName [参数]

参数:
  -UserInstall         安装到用户PATH (推荐)
  -SystemInstall       安装到系统PATH (需要管理员权限)
  -Uninstall          卸载已安装的脚本
  -Check              检查安装状态
  -Help               显示此帮助信息
  -Version            显示版本信息

方案3说明:
  全局脚本: aceflow (Python CLI) - 项目初始化和管理
  项目脚本: aceflow-stage.sh, aceflow-validate.sh, aceflow-templates.sh
  
安装位置:
  用户安装: ~\Scripts\ 或用户PATH目录
  系统安装: C:\Windows\System32 (需要管理员权限)

示例:
  .\$ScriptName -UserInstall
  .\$ScriptName -Check
  .\$ScriptName -Uninstall

"@
}

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查安装状态
function Test-Installation {
    Write-Info "检查AceFlow安装状态..."
    
    $globalScript = "aceflow"
    $installedPath = ""
    
    # 检查是否在PATH中
    $pathScript = Get-Command $globalScript -ErrorAction SilentlyContinue
    if ($pathScript) {
        $installedPath = $pathScript.Source
        Write-Success "✅ 全局脚本已安装: $installedPath"
        
        # 检查版本
        try {
            $installedVersion = & $globalScript --version 2>$null
            Write-Host "   版本: $installedVersion"
        } catch {
            Write-Host "   版本: unknown"
        }
    } else {
        Write-Warning "❌ 全局脚本未安装"
    }
    
    # 检查项目级脚本（在当前目录）
    $projectScripts = @("aceflow-stage.sh", "aceflow-validate.sh", "aceflow-templates.sh")
    $foundCount = 0
    
    Write-Info "检查当前目录的项目级脚本..."
    foreach ($script in $projectScripts) {
        if (Test-Path ".\$script") {
            Write-Success "✅ 项目脚本存在: $script"
            $foundCount++
        } else {
            Write-Warning "❌ 项目脚本缺失: $script"
        }
    }
    
    Write-Host ""
    if ($pathScript) {
        Write-Success "全局安装状态: 已安装"
    } else {
        Write-Error "全局安装状态: 未安装"
    }
    
    Write-Info "项目脚本状态: $foundCount/3 已安装"
}

# 用户级安装
function Install-UserLevel {
    Write-Info "开始用户级安装..."
    
    # 创建用户脚本目录
    $userScriptPath = "$env:USERPROFILE\Scripts"
    if (!(Test-Path $userScriptPath)) {
        New-Item -Path $userScriptPath -ItemType Directory -Force | Out-Null
        Write-Info "创建用户脚本目录: $userScriptPath"
    }
    
    # 安装全局脚本
    $globalScript = "aceflow"
    $sourcePath = Join-Path $AceFlowHome "scripts\$globalScript"
    $targetPath = Join-Path $userScriptPath $globalScript
    
    Write-Info "安装全局脚本: $globalScript"
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $targetPath -Force
        Write-Success "✅ 脚本已复制到: $targetPath"
    } else {
        Write-Error "源脚本不存在: $sourcePath"
        return
    }
    
    # 检查并更新用户PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$userScriptPath*") {
        Write-Warning "⚠️ $userScriptPath 不在用户PATH中"
        Write-Info "正在添加到用户PATH..."
        
        $newPath = if ($userPath) { "$userPath;$userScriptPath" } else { $userScriptPath }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        
        Write-Success "✅ 已添加到用户PATH"
        Write-Warning "⚠️ 请重启PowerShell或终端以使PATH生效"
    }
    
    Write-Success "✅ 用户级安装完成"
    Write-Host "   安装位置: $targetPath"
}

# 系统级安装
function Install-SystemLevel {
    Write-Info "开始系统级安装..."
    
    if (!(Test-Administrator)) {
        Write-Error "系统级安装需要管理员权限"
        Write-Host "请以管理员身份运行PowerShell，然后重新执行此脚本"
        return
    }
    
    $systemPath = "$env:WINDIR\System32"
    
    # 安装全局脚本
    $globalScript = "aceflow"
    $sourcePath = Join-Path $AceFlowHome "scripts\$globalScript"
    $targetPath = Join-Path $systemPath $globalScript
    
    Write-Info "安装全局脚本: $globalScript"
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $targetPath -Force
        Write-Success "✅ 系统级安装完成"
        Write-Host "   安装位置: $targetPath"
    } else {
        Write-Error "源脚本不存在: $sourcePath"
    }
}

# 卸载
function Uninstall-AceFlow {
    Write-Info "开始卸载AceFlow..."
    
    $globalScript = "aceflow"
    $removedCount = 0
    
    # 卸载用户级
    $userScriptPath = "$env:USERPROFILE\Scripts\$globalScript"
    if (Test-Path $userScriptPath) {
        Remove-Item $userScriptPath -Force
        Write-Success "✅ 已删除用户级脚本: $userScriptPath"
        $removedCount++
    }
    
    # 卸载系统级（需要权限）
    $systemPath = "$env:WINDIR\System32\$globalScript"
    if (Test-Path $systemPath) {
        if (Test-Administrator) {
            Remove-Item $systemPath -Force
            Write-Success "✅ 已删除系统级脚本: $systemPath"
            $removedCount++
        } else {
            Write-Warning "⚠️ 需要管理员权限删除系统级脚本: $systemPath"
            Write-Host "请以管理员身份运行以下命令: Remove-Item '$systemPath' -Force"
        }
    }
    
    if ($removedCount -eq 0) {
        Write-Warning "❌ 未找到已安装的脚本"
    } else {
        Write-Success "✅ 卸载完成，共删除 $removedCount 个脚本"
    }
}

# 主函数
function Main {
    # 显示标题
    Write-Header
    
    # 解析参数并执行相应操作
    if ($Help) {
        Show-Help
        return
    }
    
    if ($Version) {
        Write-Host "AceFlow Windows Install v$ScriptVersion"
        return
    }
    
    if ($UserInstall) {
        Install-UserLevel
    }
    elseif ($SystemInstall) {
        Install-SystemLevel
    }
    elseif ($Uninstall) {
        Uninstall-AceFlow
    }
    elseif ($Check) {
        Test-Installation
    }
    else {
        # 默认显示安装状态
        Test-Installation
    }
}

# 执行主函数
Main