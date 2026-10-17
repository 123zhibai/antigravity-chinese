# Antigravity 界面恢复官方英文原版脚本 (自愈架构版)
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Antigravity 恢复官方原版英文界面程序" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$CliScript = Join-Path (Split-Path -Parent $ScriptDir) "core\cli.py"

if (-not (Test-Path $CliScript)) {
    Write-Host "[错误] 未找到自愈核心管理脚本 cli.py！" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n[提示] 正在从独立备份区安全恢复官方纯净版本..." -ForegroundColor Yellow
python "$CliScript" restore

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[完成] 已成功恢复为官方英文原版！" -ForegroundColor Green
} else {
    Write-Host "`n[失败] 恢复过程中出现错误。" -ForegroundColor Red
}

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
