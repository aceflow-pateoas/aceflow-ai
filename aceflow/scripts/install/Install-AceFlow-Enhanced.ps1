# AceFlow v3.0 Enhanced Windows Installation Script
# Solution 3: Global init script + Project-level working scripts
# Enhanced version with better error handling and compatibility

param(
    [switch]$UserInstall,
    [switch]$SystemInstall, 
    [switch]$Uninstall,
    [switch]$Check,
    [switch]$Help,
    [switch]$Version,
    [switch]$Verbose
)

# Script Information
$ScriptName = "Install-AceFlow-Enhanced.ps1"
$ScriptVersion = "3.0.1"
$AceFlowHome = if ($env:ACEFLOW_HOME) { $env:ACEFLOW_HOME } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }

# Enhanced Error Handling
$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Logging Functions
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    if ($Host.UI.RawUI.ForegroundColor) {
        Write-Host $Text -ForegroundColor $Color
    } else {
        Write-Host $Text
    }
}

function Write-Info { 
    Write-ColorText "[INFO] $args" -Color Cyan 
    Write-Verbose "INFO: $args"
}

function Write-Success { 
    Write-ColorText "[SUCCESS] $args" -Color Green 
    Write-Verbose "SUCCESS: $args"
}

function Write-Warning { 
    Write-ColorText "[WARNING] $args" -Color Yellow 
    Write-Verbose "WARNING: $args"
}

function Write-Error { 
    Write-ColorText "[ERROR] $args" -Color Red 
    Write-Verbose "ERROR: $args"
}

function Write-Header {
    $headerText = @"
====================================================
       AceFlow v3.0 Enhanced Windows Installer
        Solution 3: Hybrid Deployment Mode
====================================================
"@
    Write-ColorText $headerText -Color Magenta
}

# Enhanced Help Information
function Show-Help {
    $helpText = @"
AceFlow v3.0 Enhanced Windows Installation Script

USAGE: .\$ScriptName [PARAMETERS]

PARAMETERS:
  -UserInstall         Install to user PATH (Recommended)
  -SystemInstall       Install to system PATH (Requires Admin)
  -Uninstall          Uninstall installed scripts
  -Check              Check installation status
  -Verbose            Show detailed output
  -Help               Show this help message
  -Version            Show version information

SOLUTION 3 EXPLANATION:
  Global Script: aceflow (Python CLI) - Project initialization and management
  Project Scripts: aceflow-stage.py, aceflow-validate.py, aceflow-templates.py
  
INSTALLATION LOCATIONS:
  User Install: ~/Scripts/ or user PATH directory
  System Install: C:\Windows\System32 (Requires administrator privileges)

EXAMPLES:
  .\$ScriptName -UserInstall -Verbose
  .\$ScriptName -Check
  .\$ScriptName -Uninstall

REQUIREMENTS:
  - Windows PowerShell 5.1 or later
  - Python 3.7 or later installed and in PATH
  - Appropriate permissions for target installation directory

For more information, visit: https://github.com/your-repo/aceflow-ai
"@
    Write-Host $helpText
}

# System Requirements Check
function Test-SystemRequirements {
    Write-Info "Checking system requirements..."
    $issues = @()
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        $issues += "PowerShell version $psVersion is too old. Minimum required: 5.1"
    } else {
        Write-Success "PowerShell version: $psVersion"
    }
    
    # Check Python installation
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python detected: $pythonVersion"
        } else {
            $issues += "Python not found in PATH. Please install Python 3.7+ and add to PATH"
        }
    } catch {
        $issues += "Python not found in PATH. Please install Python 3.7+ and add to PATH"
    }
    
    # Check execution policy
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq "Restricted") {
        $issues += "PowerShell execution policy is Restricted. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    } else {
        Write-Success "Execution policy: $executionPolicy"
    }
    
    # Check available disk space (basic check)
    $systemDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
    $freeSpaceGB = [math]::Round($systemDrive.FreeSpace / 1GB, 2)
    if ($freeSpaceGB -lt 0.1) {
        $issues += "Low disk space on system drive: ${freeSpaceGB}GB available"
    } else {
        Write-Success "Available disk space: ${freeSpaceGB}GB"
    }
    
    if ($issues.Count -gt 0) {
        Write-Error "System requirements check failed:"
        foreach ($issue in $issues) {
            Write-Error "  - $issue"
        }
        return $false
    } else {
        Write-Success "All system requirements met"
        return $true
    }
}

# Enhanced Administrator Check
function Test-Administrator {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        Write-Verbose "Administrator check: $isAdmin"
        return $isAdmin
    } catch {
        Write-Warning "Could not determine administrator status: $($_.Exception.Message)"
        return $false
    }
}

# Enhanced Installation Status Check
function Test-Installation {
    Write-Info "Checking AceFlow installation status..."
    
    $globalScript = "aceflow"
    $installedPath = ""
    $installationStatus = @{
        GlobalScriptInstalled = $false
        GlobalScriptPath = ""
        GlobalScriptVersion = ""
        ProjectScriptsFound = 0
        ProjectScriptsTotal = 4
        InstallationType = "None"
    }
    
    # Check if global script is in PATH
    try {
        $pathScript = Get-Command $globalScript -ErrorAction SilentlyContinue
        if ($pathScript) {
            $installationStatus.GlobalScriptInstalled = $true
            $installationStatus.GlobalScriptPath = $pathScript.Source
            Write-Success "Global script found: $($pathScript.Source)"
            
            # Determine installation type
            if ($pathScript.Source -like "*System32*") {
                $installationStatus.InstallationType = "System"
            } elseif ($pathScript.Source -like "*$env:USERPROFILE*") {
                $installationStatus.InstallationType = "User"
            } else {
                $installationStatus.InstallationType = "Custom"
            }
            
            # Check version
            try {
                $versionOutput = & $globalScript --version 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $installationStatus.GlobalScriptVersion = $versionOutput
                    Write-Host "   Version: $versionOutput"
                } else {
                    Write-Host "   Version: Could not determine"
                }
            } catch {
                Write-Host "   Version: Error checking version"
            }
        } else {
            Write-Warning "Global script not found in PATH"
        }
    } catch {
        Write-Error "Error checking global script: $($_.Exception.Message)"
    }
    
    # Check project-level scripts in current directory
    $projectScripts = @("aceflow-stage.py", "aceflow-validate.py", "aceflow-templates.py", "aceflow-init.py")
    Write-Info "Checking current directory for project-level scripts..."
    
    foreach ($script in $projectScripts) {
        if (Test-Path ".\$script") {
            Write-Success "Project script found: $script"
            $installationStatus.ProjectScriptsFound++
        } else {
            Write-Warning "Project script missing: $script"
        }
    }
    
    # Summary
    Write-Host ""
    Write-ColorText "Installation Summary:" -Color Cyan
    Write-Host "  Global Installation: $(if ($installationStatus.GlobalScriptInstalled) { 'Installed (' + $installationStatus.InstallationType + ')' } else { 'Not Installed' })"
    Write-Host "  Project Scripts: $($installationStatus.ProjectScriptsFound)/$($installationStatus.ProjectScriptsTotal) found"
    
    return $installationStatus
}

# Enhanced User-Level Installation
function Install-UserLevel {
    Write-Info "Starting user-level installation..."
    
    try {
        # Create user script directory
        $userScriptPath = "$env:USERPROFILE\Scripts"
        if (!(Test-Path $userScriptPath)) {
            New-Item -Path $userScriptPath -ItemType Directory -Force | Out-Null
            Write-Info "Created user script directory: $userScriptPath"
        } else {
            Write-Info "User script directory exists: $userScriptPath"
        }
        
        # Install global script
        $globalScript = "aceflow"
        $sourcePath = Join-Path $AceFlowHome "scripts\$globalScript"
        $targetPath = Join-Path $userScriptPath $globalScript
        
        Write-Info "Installing global script: $globalScript"
        Write-Verbose "Source: $sourcePath"
        Write-Verbose "Target: $targetPath"
        
        if (!(Test-Path $sourcePath)) {
            throw "Source script not found: $sourcePath. Please ensure AceFlow is properly downloaded."
        }
        
        # Copy with error handling
        try {
            Copy-Item $sourcePath $targetPath -Force
            Write-Success "Script copied successfully to: $targetPath"
        } catch {
            throw "Failed to copy script: $($_.Exception.Message)"
        }
        
        # Verify copy
        if (!(Test-Path $targetPath)) {
            throw "Copy verification failed: Target file does not exist"
        }
        
        # Check and update user PATH
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$userScriptPath*") {
            Write-Warning "Adding $userScriptPath to user PATH..."
            
            try {
                $newPath = if ($userPath) { "$userPath;$userScriptPath" } else { $userScriptPath }
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                Write-Success "Added to user PATH successfully"
                Write-Warning "Please restart PowerShell or terminal for PATH changes to take effect"
            } catch {
                throw "Failed to update PATH: $($_.Exception.Message)"
            }
        } else {
            Write-Success "User script directory already in PATH"
        }
        
        Write-Success "User-level installation completed successfully"
        Write-Host "   Installation location: $targetPath"
        Write-Host "   To verify: Restart terminal and run 'aceflow --version'"
        
    } catch {
        Write-Error "User-level installation failed: $($_.Exception.Message)"
        throw
    }
}

# Enhanced System-Level Installation
function Install-SystemLevel {
    Write-Info "Starting system-level installation..."
    
    if (!(Test-Administrator)) {
        $errorMsg = @"
System-level installation requires administrator privileges.

To resolve this:
1. Right-click on PowerShell
2. Select 'Run as Administrator'
3. Navigate to the AceFlow directory
4. Run this script again with -SystemInstall

Alternatively, use -UserInstall for user-level installation (recommended).
"@
        Write-Error $errorMsg
        throw "Administrator privileges required for system-level installation"
    }
    
    try {
        $systemPath = "$env:WINDIR\System32"
        
        # Install global script
        $globalScript = "aceflow"
        $sourcePath = Join-Path $AceFlowHome "scripts\$globalScript"
        $targetPath = Join-Path $systemPath $globalScript
        
        Write-Info "Installing global script to system directory: $globalScript"
        Write-Verbose "Source: $sourcePath"
        Write-Verbose "Target: $targetPath"
        
        if (!(Test-Path $sourcePath)) {
            throw "Source script not found: $sourcePath"
        }
        
        Copy-Item $sourcePath $targetPath -Force
        
        # Verify installation
        if (Test-Path $targetPath) {
            Write-Success "System-level installation completed successfully"
            Write-Host "   Installation location: $targetPath"
        } else {
            throw "Installation verification failed"
        }
        
    } catch {
        Write-Error "System-level installation failed: $($_.Exception.Message)"
        throw
    }
}

# Enhanced Uninstallation
function Uninstall-AceFlow {
    Write-Info "Starting AceFlow uninstallation..."
    
    $globalScript = "aceflow"
    $removedCount = 0
    $errors = @()
    
    # Remove user-level installation
    $userScriptPath = "$env:USERPROFILE\Scripts\$globalScript"
    if (Test-Path $userScriptPath) {
        try {
            Remove-Item $userScriptPath -Force
            Write-Success "Removed user-level script: $userScriptPath"
            $removedCount++
        } catch {
            $errors += "Failed to remove user-level script: $($_.Exception.Message)"
        }
    }
    
    # Remove system-level installation (requires admin)
    $systemPath = "$env:WINDIR\System32\$globalScript"
    if (Test-Path $systemPath) {
        if (Test-Administrator) {
            try {
                Remove-Item $systemPath -Force
                Write-Success "Removed system-level script: $systemPath"
                $removedCount++
            } catch {
                $errors += "Failed to remove system-level script: $($_.Exception.Message)"
            }
        } else {
            Write-Warning "Administrator privileges required to remove system-level script: $systemPath"
            Write-Host "Run the following command as Administrator:"
            Write-Host "Remove-Item '$systemPath' -Force"
        }
    }
    
    # Report results
    if ($errors.Count -gt 0) {
        Write-Warning "Uninstallation completed with errors:"
        foreach ($error in $errors) {
            Write-Error "  - $error"
        }
    }
    
    if ($removedCount -eq 0) {
        Write-Warning "No installed scripts found to remove"
    } else {
        Write-Success "Uninstallation completed. Removed $removedCount script(s)"
        Write-Info "You may need to restart your terminal for PATH changes to take effect"
    }
}

# Main Function with Enhanced Error Handling
function Main {
    try {
        # Display header
        Write-Header
        
        # Parse arguments and execute
        if ($Help) {
            Show-Help
            return
        }
        
        if ($Version) {
            Write-Host "AceFlow Enhanced Windows Installer v$ScriptVersion"
            Write-Host "Compatible with AceFlow v3.0+"
            return
        }
        
        # Check system requirements for installation operations
        if ($UserInstall -or $SystemInstall) {
            if (!(Test-SystemRequirements)) {
                Write-Error "System requirements not met. Installation aborted."
                exit 1
            }
        }
        
        # Execute requested operation
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
            # Default: show installation status
            Write-Info "No operation specified. Showing current installation status."
            Write-Info "Use -Help for available options."
            Write-Host ""
            Test-Installation
        }
        
    } catch {
        Write-Error "Script execution failed: $($_.Exception.Message)"
        Write-Host ""
        Write-Host "For help and troubleshooting:"
        Write-Host "  - Run with -Help for usage information"
        Write-Host "  - Run with -Verbose for detailed output"
        Write-Host "  - Check system requirements with Test-SystemRequirements"
        Write-Host "  - Report issues at: https://github.com/your-repo/aceflow-ai/issues"
        exit 1
    }
}

# Execute main function
Main