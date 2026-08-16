<#
.SYNOPSIS
    Starts everything needed for a live negotiation demo: an SSH tunnel to the Ronin GPU
    instance (for fast Ollama inference), a pre-warm call to absorb cold-start model-load
    latency before anyone's watching, the API server, and the frontend dev server.

.DESCRIPTION
    Run this from the repo root or from scripts/ - it resolves paths relative to itself.
    If Ronin is unreachable within the timeout (no network at the venue, instance stopped,
    etc.), this falls back to local Ollama automatically rather than failing outright - a
    slower demo beats a broken one. It never opens a raw port on Ronin; inference traffic
    only ever goes over the SSH tunnel, same as every other Ronin use in this project.

    Deliberately does NOT pass --reload to uvicorn: a reload wipes the in-memory session
    store (api/sessions.py) mid-negotiation, which is exactly what you don't want to risk
    while presenting.

.EXAMPLE
    .\scripts\start_demo.ps1
    .\scripts\start_demo.ps1 -SkipRonin        # go straight to local Ollama
    .\scripts\start_demo.ps1 -ApiPort 8001
#>

param(
    [string]$RoninHost = "shreyas-negotiation.ronin.manchester.ac.uk",
    [string]$RoninUser = "ubuntu",
    [int]$LocalOllamaPort = 11500,
    [int]$ApiPort = 8000,
    [int]$TunnelTimeoutSec = 15,
    [switch]$SkipRonin
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PemPath = Join-Path $RepoRoot "shreyas-negotiation.pem"
$StatePath = Join-Path $RepoRoot ".demo-state.json"

Write-Host "=== Procurement Dispute Negotiation - Demo Startup ===" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"

$state = @{
    tunnel_pid = $null
    ollama_host = $null
}

function Test-OllamaReady {
    param([string]$BaseUrl)
    try {
        $resp = Invoke-RestMethod -Uri "$BaseUrl/api/tags" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# --- Step 1: try the Ronin GPU tunnel, unless explicitly skipped ------------------------
$useRonin = $false

if (-not $SkipRonin) {
    if (-not (Test-Path $PemPath)) {
        Write-Host "No key found at $PemPath - skipping Ronin, falling back to local Ollama." -ForegroundColor Yellow
    } else {
        $localOllamaBase = "http://127.0.0.1:$LocalOllamaPort"

        if (Test-OllamaReady -BaseUrl $localOllamaBase) {
            Write-Host "Port $LocalOllamaPort is already answering - reusing an existing tunnel." -ForegroundColor Green
            $useRonin = $true
        } else {
            Write-Host "Opening SSH tunnel to $RoninHost (local port $LocalOllamaPort -> remote 11434)..."
            $sshArgs = @(
                "-i", $PemPath,
                "-N",
                "-L", "${LocalOllamaPort}:localhost:11434",
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=10",
                "-o", "ServerAliveInterval=30",
                "$RoninUser@$RoninHost"
            )
            $tunnelProc = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -WindowStyle Hidden -PassThru

            $waited = 0
            $ready = $false
            while ($waited -lt $TunnelTimeoutSec) {
                Start-Sleep -Seconds 1
                $waited++
                if (Test-OllamaReady -BaseUrl $localOllamaBase) {
                    $ready = $true
                    break
                }
            }

            if ($ready) {
                Write-Host "Tunnel is up ($waited sec)." -ForegroundColor Green
                $state.tunnel_pid = $tunnelProc.Id
                $useRonin = $true
            } else {
                Write-Host "Tunnel did not come up within ${TunnelTimeoutSec}s - falling back to local Ollama." -ForegroundColor Yellow
                try { Stop-Process -Id $tunnelProc.Id -Force -ErrorAction SilentlyContinue } catch {}
            }
        }
    }
} else {
    Write-Host "Skipping Ronin (-SkipRonin passed)." -ForegroundColor Yellow
}

# --- Step 2: pre-warm the model if we're on Ronin, so cold-start load isn't live --------
if ($useRonin) {
    $ollamaBase = "http://127.0.0.1:$LocalOllamaPort"
    $state.ollama_host = $ollamaBase
    Write-Host "Pre-warming llama3.1 on Ronin (absorbs the ~40s cold-load now, not during the demo)..."
    $warmStart = Get-Date
    try {
        Invoke-RestMethod -Uri "$ollamaBase/api/generate" -Method Post -TimeoutSec 90 -ContentType "application/json" `
            -Body '{"model":"llama3.1","prompt":"Say OK","stream":false}' | Out-Null
        $elapsed = [math]::Round(((Get-Date) - $warmStart).TotalSeconds, 1)
        Write-Host "Model warm ($elapsed sec)." -ForegroundColor Green
    } catch {
        Write-Host "Pre-warm call failed - continuing anyway, first live call may be slow. ($($_.Exception.Message))" -ForegroundColor Yellow
    }
} else {
    Write-Host "Using local Ollama (http://localhost:11434) - no GPU speedup. Make sure 'ollama serve' is running." -ForegroundColor Yellow
}

# --- Step 3: start the API server in its own visible window -----------------------------
# Set env vars in THIS process first, rather than building a -Command string that sets
# them - a child process inherits its parent's environment block automatically, and
# stuffing env-var assignments into a Start-Process -ArgumentList string is fragile
# (quoting through the Win32 CreateProcess command-line rebuild silently dropped the
# assignment during testing, so the API server connected straight to local Ollama
# instead of the tunnel with no error - caught by checking netstat, not by inspection).
Write-Host "Starting API server on port $ApiPort..."
$env:PYTHONIOENCODING = "utf-8"
if ($state.ollama_host) {
    $env:OLLAMA_HOST = $state.ollama_host
}
$apiCommand = "cd '$RepoRoot'; python -m uvicorn api.main:app --port $ApiPort"
$apiProc = Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $apiCommand) -PassThru
$state.api_pid = $apiProc.Id

# --- Step 4: start the frontend dev server in its own visible window --------------------
Write-Host "Starting frontend dev server..."
$frontendDir = Join-Path $RepoRoot "frontend"
$frontendCommand = "cd '$frontendDir'; npm run dev"
$frontendProc = Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $frontendCommand) -PassThru
$state.frontend_pid = $frontendProc.Id

# --- Step 5: save state for stop_demo.ps1, print summary --------------------------------
$state | ConvertTo-Json | Set-Content -Path $StatePath -Encoding utf8

Write-Host ""
Write-Host "=== Demo is starting ===" -ForegroundColor Cyan
if ($useRonin) {
    Write-Host "Inference: Ronin GPU (via tunnel, port $LocalOllamaPort)" -ForegroundColor Green
} else {
    Write-Host "Inference: local Ollama (slower - no GPU)" -ForegroundColor Yellow
}
Write-Host "API:      http://localhost:$ApiPort  (opened in its own window)"
Write-Host "Frontend: check the new window's output for its port (usually http://localhost:5173)"
Write-Host ""
Write-Host "Give the frontend/API windows a few seconds to finish starting up."
Write-Host "When you're done: .\scripts\stop_demo.ps1"
