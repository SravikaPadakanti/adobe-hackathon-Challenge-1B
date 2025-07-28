# Adobe Hackathon Challenge 1B - PowerShell Setup Script

param(
    [Parameter(Position=0)]
    [string]$Action = "help"
)

$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}
function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}
function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}
function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-Docker {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Success "Docker is installed: $dockerVersion"
            return $true
        }
    } catch {
        Write-Error "Docker is not installed or not in PATH."
        return $false
    }
    return $false
}

function New-ProjectStructure {
    Write-Status "Creating project structure..."
    $directories = @("input", "output", "test_input", "test_output")
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir" -ForegroundColor Gray
        }
    }
    Write-Success "Project directories created"
}

function Build-DockerImage {
    Write-Status "Building Docker image..."
    try {
        docker build --platform linux/amd64 -t document-intelligence:latest .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker image built successfully"
            return $true
        } else {
            Write-Error "Docker build failed"
            return $false
        }
    } catch {
        Write-Error "Error building Docker image: $_"
        return $false
    }
}

function New-SampleInput {
    Write-Status "Creating sample input files..."
    "PhD Researcher in Computational Biology" | Out-File -FilePath "input\persona.txt" -Encoding UTF8
    "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for Graph Neural Networks in Drug Discovery" | Out-File -FilePath "input\job.txt" -Encoding UTF8
    Write-Success "Sample input files created"
    Write-Warning "Please add your PDF files to the input\ directory"
}

function Start-Solution {
    Write-Status "Running Document Intelligence Solution..."

    if (!(Test-Path "input")) {
        Write-Error "Input directory not found"
        return
    }

    $pdfFiles = Get-ChildItem -Path "input" -Filter "*.pdf"
    if ($pdfFiles.Count -eq 0) {
        Write-Error "No PDF files found in input\ directory"
        return
    }

    $currentDir = (Get-Location).Path

    try {
        docker run --rm `
            -v "${currentDir}\input:/app/input" `
            -v "${currentDir}\output:/app/output" `
            --network none `
            document-intelligence:latest

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Solution executed successfully!"
            if (Test-Path "output\challenge1b_output.json") {
                try {
                    $output = Get-Content "output\challenge1b_output.json" | ConvertFrom-Json
                    Write-Host ""
                    Write-Host "📊 Results Summary:" -ForegroundColor Green
                    Write-Host "   📋 Extracted sections: $($output.extracted_sections.Count)"
                    Write-Host "   🔍 Sub-section analyses: $($output.sub_section_analysis.Count)"
                    Write-Host "   📄 Documents processed: $($output.metadata.input_documents.Count)"
                } catch {
                    Write-Warning "Could not parse output JSON for summary"
                }
            }
        } else {
            Write-Error "Solution execution failed"
        }
    } catch {
        Write-Error "Error running Docker container: $_"
    }
}

function Test-LocalEnvironment {
    Write-Status "Testing local Python environment..."
    try {
        python -c "import PyPDF2, sentence_transformers, sklearn, nltk; print('All packages available')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All required Python packages are available"
        } else {
            Write-Warning "Some Python packages are missing."
        }
    } catch {
        Write-Warning "Python not found or packages missing."
    }
}

function Show-Usage {
    Write-Host ""
    Write-Host "🚀 Adobe Hackathon Challenge 1B - PowerShell Setup" -ForegroundColor Green
    Write-Host "============================================================"
    Write-Host "Usage: .\setup.ps1 [ACTION]" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  setup     - Initial setup (create directories, sample files)"
    Write-Host "  build     - Build Docker image"
    Write-Host "  run       - Run the solution"
    Write-Host "  test      - Test local Python environment"
    Write-Host "  all       - Complete setup (setup + build + sample files)"
    Write-Host "  help      - Show this help message"
    Write-Host ""
}

# Entry Point
switch ($Action.ToLower()) {
    "setup" {
        if (Test-Docker) {
            New-ProjectStructure
            New-SampleInput
        }
    }
    "build" {
        if (Test-Docker) {
            Build-DockerImage
        }
    }
    "run" {
        if (Test-Docker) {
            Start-Solution
        }
    }
    "test" {
        Test-LocalEnvironment
    }
    "all" {
        if (Test-Docker) {
            New-ProjectStructure
            New-SampleInput
            if (Build-DockerImage) {
                Write-Success "Setup complete! Add your PDF files to input\ and run: .\setup.ps1 run"
            }
        }
    }
    "help" {
        Show-Usage
    }
    default {
        Write-ErrorMsg "Unknown action: $Action"
        Show-Usage
    }
}