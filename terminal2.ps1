# StreamMoji Terminal 2 - Testing and Monitoring
# Run this in a second terminal after Terminal 1 is running

Write-Host "StreamMoji Terminal 2 - Testing" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""

# Check if services are running
Write-Host "[1] Checking services..." -ForegroundColor Yellow

# Test API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[+] Flask API is working!" -ForegroundColor Green
    }
} catch {
    Write-Host "[-] Flask API not accessible. Make sure Terminal 1 is running." -ForegroundColor Red
    exit 1
}

# Test Dashboard
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8082/dashboard.html" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[+] Dashboard is accessible!" -ForegroundColor Green
    }
} catch {
    Write-Host "[-] Dashboard not accessible. Make sure Terminal 1 is running." -ForegroundColor Red
}

Write-Host ""
Write-Host "Available Testing Options:" -ForegroundColor Cyan
Write-Host "1. Light load test (5 clients)" -ForegroundColor White
Write-Host "2. Medium load test (10 clients)" -ForegroundColor White
Write-Host "3. Heavy load test (20 clients)" -ForegroundColor White
Write-Host "4. Custom test" -ForegroundColor White
Write-Host "5. Manual emoji test" -ForegroundColor White
Write-Host "6. Monitor only" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose an option (1-6)"

switch ($choice) {
    "1" {
        Write-Host "Starting light load test..." -ForegroundColor Yellow
        python test_clients.py --num-clients 5 --min-delay 1 --max-delay 3
    }
    "2" {
        Write-Host "Starting medium load test..." -ForegroundColor Yellow
        python test_clients.py --num-clients 10 --min-delay 0.5 --max-delay 2
    }
    "3" {
        Write-Host "Starting heavy load test..." -ForegroundColor Yellow
        python test_clients.py --num-clients 20 --min-delay 0.1 --max-delay 1
    }
    "4" {
        $clients = Read-Host "Number of clients"
        $minDelay = Read-Host "Minimum delay (seconds)"
        $maxDelay = Read-Host "Maximum delay (seconds)"
        Write-Host "Starting custom test..." -ForegroundColor Yellow
        python test_clients.py --num-clients $clients --min-delay $minDelay --max-delay $maxDelay
    }
    "5" {
        Write-Host "Sending manual emoji test..." -ForegroundColor Yellow
        Write-Host "Testing emoji endpoint..." -ForegroundColor White
        # Simple test using PowerShell
        $body = @{
            user_id = "test_user_$(Get-Date -Format 'HHmmss')"
            emoji_type = "smile"
        } | ConvertTo-Json
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/emoji" -Method POST -Body $body -ContentType "application/json"
            Write-Host "[+] Emoji sent successfully! Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "Response: $($response.Content)" -ForegroundColor Cyan
        } catch {
            Write-Host "[-] Failed to send emoji: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    "6" {
        Write-Host "Monitoring mode - showing service status..." -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor White
        while ($true) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API Status: OK" -ForegroundColor Green
            } catch {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API Status: DOWN" -ForegroundColor Red
            }
            Start-Sleep 10
        }
    }
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
    }
}