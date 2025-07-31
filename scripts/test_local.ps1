# test_local.ps1 - Test script for local Windows execution
Write-Host "Testing Challenge 1B locally..." -ForegroundColor Green

# Check if input directory has PDFs
$pdfFiles = Get-ChildItem -Path ".\input" -Filter "*.pdf"
if ($pdfFiles.Count -eq 0) {
    Write-Host "No PDF files found in ./input directory" -ForegroundColor Red
    Write-Host "Please add some PDF files to test" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $($pdfFiles.Count) PDF files in input directory" -ForegroundColor Green

# Create sample persona and job files if they don't exist
if (-not (Test-Path ".\input\persona.txt")) {
    "PhD Researcher in Computational Biology" | Set-Content ".\input\persona.txt"
    Write-Host "Created sample persona.txt" -ForegroundColor Yellow
}

if (-not (Test-Path ".\input\job.txt")) {
    "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks" | Set-Content ".\input\job.txt"
    Write-Host "Created sample job.txt" -ForegroundColor Yellow
}

# Run the solution
Write-Host "Running document intelligence system..." -ForegroundColor Green
$startTime = Get-Date
python main.py
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "Processing completed in $([math]::Round($duration, 2)) seconds" -ForegroundColor Green

# Check output
if (Test-Path ".\output\challenge1b_output.json") {
    Write-Host "Output file created successfully!" -ForegroundColor Green
    $outputSize = (Get-Item ".\output\challenge1b_output.json").Length
    Write-Host "Output file size: $([math]::Round($outputSize/1KB, 2)) KB" -ForegroundColor Cyan
} else {
    Write-Host "Error: Output file not created" -ForegroundColor Red
}