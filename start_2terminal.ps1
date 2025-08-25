# StreamMoji 2-Terminal Setup
# Terminal 1: Run this script for Docker services and dashboard

Write-Host "StreamMoji 2-Terminal Setup" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host ""

# Step 1: Check Docker
Write-Host "[1] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[+] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[-] Docker not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Step 2: Clean up existing containers and start fresh
Write-Host "[2] Cleaning up existing containers and resources..." -ForegroundColor Yellow
try {
    # Stop and remove existing containers with volumes
    Write-Host "   Stopping and removing containers with volumes..." -ForegroundColor Yellow
    docker-compose -f docker-compose.working.yml down -v --remove-orphans 2>$null
    
    # Remove any dangling containers related to our project
    $containers = docker ps -a --filter "name=zookeeper" --filter "name=kafka" --filter "name=flask-api" --filter "name=streammoji" -q 2>$null
    if ($containers) {
        Write-Host "   Removing remaining project containers..." -ForegroundColor Yellow
        docker rm -f $containers 2>$null
    }
    
    # Clean up project-specific volumes
    $volumes = docker volume ls --filter "name=streammoji" -q 2>$null
    if ($volumes) {
        Write-Host "   Removing project volumes..." -ForegroundColor Yellow
        docker volume rm $volumes 2>$null
    }
    
    # Clean up dangling volumes
    $danglingVolumes = docker volume ls -f dangling=true -q 2>$null
    if ($danglingVolumes) {
        Write-Host "   Cleaning dangling volumes..." -ForegroundColor Yellow
        docker volume rm $danglingVolumes 2>$null
    }
    
    # Clean up any dangling images from our project
    $images = docker images --filter "dangling=true" --filter "reference=*streammoji*" -q 2>$null
    if ($images) {
        Write-Host "   Cleaning dangling images..." -ForegroundColor Yellow
        docker rmi $images 2>$null
    }
    
    # Clean up unused networks
    Write-Host "   Pruning unused networks..." -ForegroundColor Yellow
    docker network prune -f 2>$null
    
    Write-Host "[+] Complete cleanup finished - Fresh environment ready" -ForegroundColor Green
} catch {
    Write-Host "[!] Some cleanup operations failed, but continuing..." -ForegroundColor Yellow
}

# Step 3: Start Docker services with fresh containers
Write-Host "[3] Starting fresh Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.working.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] Fresh Docker services started successfully" -ForegroundColor Green
} else {
    Write-Host "[-] Failed to start Docker services" -ForegroundColor Red
    exit 1
}

# Step 4: Wait for services
Write-Host "[4] Waiting for fresh services to be ready..." -ForegroundColor Yellow
Start-Sleep 20

# Step 5: Test API
Write-Host "[5] Testing Flask API..." -ForegroundColor Yellow
$apiReady = $false
for ($i = 1; $i -le 6; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "[+] Flask API is working!" -ForegroundColor Green
            $data = $response.Content | ConvertFrom-Json
            Write-Host "   Status: $($data.status)" -ForegroundColor Green
            Write-Host "   Kafka: $($data.kafka_servers -join ', ')" -ForegroundColor Green
            $apiReady = $true
            break
        }
    } catch {
        Write-Host "[-] API test attempt $i/6 failed, retrying..." -ForegroundColor Yellow
        Start-Sleep 5
    }
}

if (-not $apiReady) {
    Write-Host "[-] Flask API is not responding after multiple attempts" -ForegroundColor Red
    Write-Host "    Check Docker logs: docker-compose -f docker-compose.working.yml logs flask-api" -ForegroundColor Yellow
}

# Step 6: Start Dashboard Server
Write-Host "[6] Starting Dashboard Server..." -ForegroundColor Yellow
Write-Host "   This will start the dashboard on port 8082..." -ForegroundColor Green

# Display status
Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
Write-Host "StreamMoji Services Status:" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
if ($apiReady) {
    Write-Host "[+] Flask API: http://localhost:5000 (Working)" -ForegroundColor Green
    Write-Host "[+] API Health: http://localhost:5000/health" -ForegroundColor Green
} else {
    Write-Host "[-] Flask API: http://localhost:5000 (Not Ready)" -ForegroundColor Red
}
Write-Host "[*] Dashboard: http://localhost:8082/dashboard.html (Starting...)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Magenta
Write-Host "1. Dashboard will open automatically" -ForegroundColor White
Write-Host "2. Use Terminal 2 for testing: python test_clients.py --num-clients 5" -ForegroundColor White
Write-Host "3. Fresh containers created - All data reset for clean testing" -ForegroundColor White
Write-Host "4. To stop: docker-compose -f docker-compose.working.yml down" -ForegroundColor White
Write-Host ""

# Start dashboard server
Write-Host "Starting dashboard server..." -ForegroundColor Yellow
python simple_server.py