# build_docker.ps1 - Docker build script for Windows
Write-Host "Building Docker image for Challenge 1B..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t challenge1b:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker image built successfully!" -ForegroundColor Green
    
    # Test the Docker image
    Write-Host "Testing Docker image..." -ForegroundColor Yellow
    
    # Ensure input directory exists with test files
    if (-not (Test-Path ".\input")) {
        New-Item -ItemType Directory -Force -Path ".\input"
        Write-Host "Created input directory. Please add PDF files for testing." -ForegroundColor Yellow
    }
    
    # Run the container
    docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none challenge1b:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker test completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Docker test failed" -ForegroundColor Red
    }
} else {
    Write-Host "Docker build failed" -ForegroundColor Red
}