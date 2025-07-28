
@echo off
setlocal EnableDelayedExpansion

REM Adobe Hackathon Challenge 1B - Windows Batch Setup Script
echo.
echo 🚀 Adobe Hackathon Challenge 1B - Windows Batch Setup
echo ============================================================

set "action=%~1"
if "%action%"=="" set "action=help"

REM Check if Docker is installed
:check_docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows from:
    echo https://www.docker.com/products/docker-desktop/
    exit /b 1
)
echo [SUCCESS] Docker is installed

REM Create project structure
:create_structure
echo [INFO] Creating project structure...
if not exist "input" mkdir "input"
if not exist "output" mkdir "output"
if not exist "test_input" mkdir "test_input"
if not exist "test_output" mkdir "test_output"
echo [SUCCESS] Project directories created
goto :eof

REM Create sample input files
:create_sample_input
echo [INFO] Creating sample input files...

echo PhD Researcher in Computational Biology > "input\persona.txt"
echo Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for Graph Neural Networks in Drug Discovery > "input\job.txt"

echo [SUCCESS] Sample input files created in input\ directory
echo [WARNING] Please add your PDF files to the input\ directory
goto :eof

REM Test local installation
:test_local
echo [INFO] Testing local Python environment...
python -c "import PyPDF2, sentence_transformers, sklearn, nltk; print('All packages available')" >nul 2>&1
if %errorlevel% eq 0 (
    echo [SUCCESS] All required Python packages are available
    echo [INFO] You can test locally using: python test_local.py
) else (
    echo [WARNING] Some Python packages are missing. Docker execution is recommended.
)
goto :eof

REM Run solution
:run_solution
echo [INFO] Running Document Intelligence Solution...

REM Check if input directory exists and has PDF files
if not exist "input" (
    echo [ERROR] Input directory not found
    echo [INFO] Please run: setup.bat setup
    exit /b 1
)

dir "input\*.pdf" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No PDF files found in input\ directory
    echo [INFO] Please add PDF files to input\ directory and run again
    exit /b 1
)

REM Get current directory for volume mapping
set "currentdir=%cd%"

REM Run Docker container
echo [INFO] Starting Docker container...
docker run --rm -v "%currentdir%\input:/app/input" -v "%currentdir%\output:/app/output" --network none document-intelligence:latest

if %errorlevel% eq 0 (
    echo [SUCCESS] Solution executed successfully!
    echo [INFO] Check output\challenge1b_output.json for results
    
    REM Show basic stats if output exists
    if exist "output\challenge1b_output.json" (
        echo.
        echo 📊 Results generated in output\challenge1b_output.json
    )
) else (
    echo [ERROR] Solution execution failed
)
goto :eof

REM Display usage information
:show_usage
echo.
echo Usage: setup.bat [ACTION]
echo.
echo Actions:
echo   setup     - Initial setup (create directories, sample files)
echo   build     - Build Docker image
echo   run       - Run the solution
echo   test      - Test local Python environment
echo   all       - Complete setup (setup + build + sample files)
echo   help      - Show this help message
echo.
echo Examples:
echo   setup.bat all       # Complete setup
echo   setup.bat run       # Run solution
echo   setup.bat build     # Build Docker image only
echo.
goto :eof

REM Main execution
if /i "%action%"=="setup" (
    call :check_docker
    call :create_structure
    call :create_sample_input
) else if /i "%action%"=="build" (
    call :check_docker
    call :build_image
) else if /i "%action%"=="run" (
    call :check_docker
    call :run_solution
) else if /i "%action%"=="test" (
    call :test_local
) else if /i "%action%"=="all" (
    call :check_docker
    call :create_structure
    call :create_sample_input
    call :build_image
    if %errorlevel% eq 0 (
        echo [SUCCESS] Setup complete! Add your PDF files to input\ directory and run: setup.bat run
    )
) else if /i "%action%"=="help" (
    call :show_usage
) else (
    echo [ERROR] Unknown action: %action%
    call :show_usage
    exit /b 1
)

echo.
echo Done!
