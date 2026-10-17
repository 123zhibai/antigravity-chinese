# Antigravity 界面中文汉化一键安装脚本 (自愈架构升级版)
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Antigravity 桌面端界面中文汉化自愈系统安装程序" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$CliScript = Join-Path (Split-Path -Parent $ScriptDir) "core\cli.py"

if (-not (Test-Path $CliScript)) {
    Write-Host "[错误] 未找到自愈核心管理脚本 cli.py！" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n[提示] 正在调用自愈引擎执行安全汉化注入..." -ForegroundColor Yellow
python "$CliScript" install

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[完成] 汉化安装与状态数据库已同步！" -ForegroundColor Green
    Write-Host "提示：请完全退出并重新启动 Antigravity 客户端以生效。" -ForegroundColor Yellow
} else {
    Write-Host "`n[失败] 汉化安装过程中出现错误，请检查 Python 环境及运行权限。" -ForegroundColor Red
}

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
