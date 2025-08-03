# setup.ps1 - Initial setup script for Windows
Write-Host "Setting up Challenge 1B environment..." -ForegroundColor Green

# Create project structure
New-Item -ItemType Directory -Force -Path ".\input"
New-Item -ItemType Directory -Force -Path ".\output"
New-Item -ItemType Directory -Force -Path ".\test_data"

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements_windows.txt

# Download NLTK data
Write-Host "Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "Place your PDF files in the './input' directory"
Write-Host "Optionally, create 'persona.txt' and 'job.txt' files in the input directory"