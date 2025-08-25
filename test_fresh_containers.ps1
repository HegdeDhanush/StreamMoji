# Test script to verify fresh container functionality
Write-Host "Testing Fresh Container Setup..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check existing containers before cleanup
Write-Host "`n[1] Checking existing containers:" -ForegroundColor Yellow
$existingContainers = docker ps -a --filter "name=zookeeper" --filter "name=kafka" --filter "name=flask-api" --format "table {{.Names}}\t{{.Status}}"
if ($existingContainers) {
    Write-Host $existingContainers -ForegroundColor White
} else {
    Write-Host "   No existing project containers found" -ForegroundColor Gray
}

# Check existing volumes
Write-Host "`n[2] Checking existing volumes:" -ForegroundColor Yellow
$existingVolumes = docker volume ls --filter "name=streammoji" --format "table {{.Name}}"
if ($existingVolumes -and $existingVolumes -ne "NAME") {
    Write-Host $existingVolumes -ForegroundColor White
} else {
    Write-Host "   No existing project volumes found" -ForegroundColor Gray
}

Write-Host "`n[3] Ready to test fresh container creation!" -ForegroundColor Green
Write-Host "   Run: .\start_2terminal.ps1" -ForegroundColor Cyan
Write-Host "   Expected: All containers will be recreated fresh" -ForegroundColor Cyan

Write-Host "`n[INFO] This script only checks current state." -ForegroundColor Blue
Write-Host "       Use start_2terminal.ps1 to see the cleanup in action." -ForegroundColor Blue