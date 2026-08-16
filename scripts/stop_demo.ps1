<#
.SYNOPSIS
    Stops everything started by start_demo.ps1: the SSH tunnel, the API server window,
    and the frontend dev server window. Safe to run even if some of them were already
    closed manually - each stop is best-effort.
#>

$RepoRoot = Split-Path -Parent $PSScriptRoot
$StatePath = Join-Path $RepoRoot ".demo-state.json"

if (-not (Test-Path $StatePath)) {
    Write-Host "No .demo-state.json found - nothing to stop (or start_demo.ps1 was never run)." -ForegroundColor Yellow
    exit 0
}

$state = Get-Content $StatePath -Raw | ConvertFrom-Json

function Stop-IfRunning {
    param([Nullable[int]]$ProcessId, [string]$Label)
    if (-not $ProcessId) { return }
    try {
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $ProcessId -Force
            Write-Host "Stopped $Label (PID $ProcessId)." -ForegroundColor Green
        } else {
            Write-Host "$Label (PID $ProcessId) was already stopped." -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "Could not stop $Label (PID $ProcessId): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Stop-IfRunning -ProcessId $state.tunnel_pid -Label "SSH tunnel to Ronin"
Stop-IfRunning -ProcessId $state.api_pid -Label "API server window"
Stop-IfRunning -ProcessId $state.frontend_pid -Label "frontend dev server window"

Remove-Item $StatePath -Force
Write-Host "Demo stopped." -ForegroundColor Cyan
