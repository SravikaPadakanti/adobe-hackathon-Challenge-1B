
# 🚀 Adobe Hackathon Challenge 1B - Windows PowerShell Setup Guide

## 🔧 Prerequisites

### 1. Install Docker Desktop for Windows
- Download from: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Ensure Docker is running (check system tray)

### 2. Enable WSL2 (if prompted)
- Docker Desktop may require WSL2 backend
- Follow Docker's setup instructions if needed

## 📁 Project Structure (Windows)
```
adobe-hackathon-1b\
├── main.py                     # Core solution (✅ Ready)
├── Dockerfile                  # Docker configuration (✅ Ready)
├── requirements.txt            # Python dependencies (✅ Ready)
├── approach_explanation.md     # Methodology explanation (✅ Ready)
├── README.md                   # Project documentation (✅ Ready)
├── setup.ps1                   # PowerShell setup script (✅ Ready)
├── test_local.py               # Local testing utility (✅ Ready)
├── sample_challenge1b_output.json  # Sample output format (✅ Ready)
├── input\                      # Input directory (will be created)
│   ├── persona.txt            # Persona description
│   ├── job.txt               # Job description
│   ├── document1.pdf         # Your PDF files
│   ├── document2.pdf         # Your PDF files
│   └── document3.pdf         # Your PDF files
└── output\                     # Output directory (auto-created)
    └── challenge1b_output.json
```

## 🚀 Quick Setup (Windows PowerShell)

### Step 1: Create Project Directory
```powershell
# Open PowerShell as Administrator (recommended)
# Create and navigate to project directory
mkdir adobe-hackathon-1b
cd adobe-hackathon-1b
```

### Step 2: Save Project Files
Save all the provided files in your project directory:
- main.py
- Dockerfile
- requirements.txt
- approach_explanation.md
- README.md
- setup.ps1
- test_local.py
- sample_challenge1b_output.json

### Step 3: Set Execution Policy (if needed)
```powershell
# Allow PowerShell scripts to run (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or for current session only:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Step 4: Complete Setup
```powershell
# Run complete setup
.\setup.ps1 all
```

## 📋 Step-by-Step Execution

### Step 1: Verify Setup
```powershell
# Check if Docker is working
docker --version

# Verify project structure
dir
```

### Step 2: Add Your PDF Files
```powershell
# Copy your PDF files to input directory
Copy-Item "C:\path\to\your\documents\*.pdf" -Destination "input\"

# Verify files are copied
dir input\
```

### Step 3: Customize Configuration (Optional)
```powershell
# Edit persona file
notepad input\persona.txt
# Example: "Investment Analyst" or "Undergraduate Chemistry Student"

# Edit job description
notepad input\job.txt
# Example: "Analyze revenue trends" or "Identify key concepts for exam preparation"
```

### Step 4: Run the Solution
```powershell
# Execute the solution
.\setup.ps1 run

# Or check individual components:
.\setup.ps1 build    # Build Docker image only
.\setup.ps1 test     # Test local Python environment
```

### Step 5: View Results
```powershell
# Check output directory
dir output\

# View the JSON output
Get-Content output\challenge1b_output.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Or open in notepad
notepad output\challenge1b_output.json
```

## 🔧 PowerShell Commands Reference

### Basic Setup Commands
```powershell
# Complete setup
.\setup.ps1 all

# Individual steps
.\setup.ps1 setup     # Create directories and sample files
.\setup.ps1 build     # Build Docker image
.\setup.ps1 run       # Run solution
.\setup.ps1 test      # Test local environment
.\setup.ps1 help      # Show help
```

## 🎉 Final Windows Checklist

- [ ] Docker Desktop installed and running
- [ ] PowerShell execution policy allows scripts
- [ ] All project files saved in directory
- [ ] PDF files added to input\ directory
- [ ] persona.txt and job.txt customized
- [ ] Docker image builds successfully (`.\setup.ps1 build`)
- [ ] Solution runs without errors (`.\setup.ps1 run`)
- [ ] Output JSON generated in output\ directory
- [ ] Processing time under 60 seconds

## 🚀 You're Ready!

Your Windows PowerShell environment is now set up for Adobe Hackathon Challenge 1B. Use these commands to execute:

```powershell
# Complete workflow
.\setup.ps1 all          # Initial setup
# Add your PDF files to input\ directory
.\setup.ps1 run          # Execute solution
```

The system will generate `output\challenge1b_output.json` with your results! 🎯
```

#### 11. Input Configuration Files (2 files - YOU CREATE THESE)

##### `input/persona.txt`
```text
PhD Researcher in Computational Biology
```

##### `input/job.txt`
```text
Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for Graph Neural Networks in Drug Discovery
```

## 🎯 FINAL FOLDER STRUCTURE SUMMARY

```
adobe-hackathon-1b/
├── main.py                           ✅ [COPY FROM ABOVE]
├── Dockerfile                        ✅ [COPY FROM ABOVE]
├── requirements.txt                  ✅ [COPY FROM ABOVE]
├── approach_explanation.md           ✅ [COPY FROM ABOVE]
├── README.md                         ✅ [COPY FROM ABOVE]
├── setup.ps1                         ✅ [COPY FROM ABOVE]
├── setup.bat                         ✅ [COPY FROM ABOVE]
├── test_local.py                     ✅ [COPY FROM ABOVE]
├── sample_challenge1b_output.json    ✅ [COPY FROM ABOVE]
├── WINDOWS_SETUP_INSTRUCTIONS.md     ✅ [COPY FROM ABOVE]
├── input/                            📁 [AUTO-CREATED BY SETUP]
│   ├── persona.txt                   📝 [CREATE WITH YOUR PERSONA]
│   ├── job.txt                       📝 [CREATE WITH YOUR JOB]
│   └── *.pdf                         📄 [ADD YOUR PDF FILES]
└── output/                           📁 [AUTO-CREATED DURING EXECUTION]
    └── challenge1b_output.json       📊 [GENERATED RESULT]
```

## 🚀 EXECUTION STEPS

1. **Create folder**: `mkdir adobe-hackathon-1b`
2. **Copy all 10 files above** into the folder
3. **Run setup**: `.\setup.ps1 all`
4. **Add your PDFs**: Copy to `input\` folder
5. **Execute**: `.\setup.ps1 run`
6. **Get results**: Check `output\challenge1b_output.json`

That's ALL the files you need! 🎉 :eof

REM Build Docker image
:build_image
echo [INFO] Building Docker image...
docker build --platform linux/amd64 -t document-intelligence:latest .
if %errorlevel% eq 0 (
    echo [SUCCESS] Docker image built successfully
) else (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
goto