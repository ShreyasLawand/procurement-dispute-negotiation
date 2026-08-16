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
    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Host "$Label (PID $ProcessId) was already stopped." -ForegroundColor DarkGray
        return
    }
    # api_pid/frontend_pid are the WRAPPER powershell -NoExit window, not the actual
    # python/npm process running inside it - Stop-Process on just that PID leaves the
    # real server (and, for the frontend, npm's child node.exe) orphaned and still bound
    # to its port, invisible with no window. Found by testing a full start/stop cycle:
    # stop_demo.ps1 reported success, but port 8000/5173 were still LISTENING afterward.
    # taskkill /T kills the whole process tree, not just the one PID.
    taskkill /T /F /PID $ProcessId | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Stopped $Label (PID $ProcessId, including child processes)." -ForegroundColor Green
    } else {
        Write-Host "Could not fully stop $Label (PID $ProcessId) - check Task Manager." -ForegroundColor Yellow
    }
}

Stop-IfRunning -ProcessId $state.tunnel_pid -Label "SSH tunnel to Ronin"
Stop-IfRunning -ProcessId $state.api_pid -Label "API server window"
Stop-IfRunning -ProcessId $state.frontend_pid -Label "frontend dev server window"

Remove-Item $StatePath -Force
Write-Host "Demo stopped." -ForegroundColor Cyan
