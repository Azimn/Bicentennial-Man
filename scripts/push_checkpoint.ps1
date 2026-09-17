param(
    [string]$Message = "Checkpoint Bicentennial Man run"
)

$ErrorActionPreference = "Stop"

git add checkpoints/*.json configs/*.json
$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "No checkpoint changes to commit."
    exit 0
}

git commit -m $Message
git push
