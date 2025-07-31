# validate_output.ps1 - Validate output JSON
param(
    [string]$OutputFile = ".\output\challenge1b_output.json"
)

Write-Host "Validating output file: $OutputFile" -ForegroundColor Green

if (-not (Test-Path $OutputFile)) {
    Write-Host "Output file not found!" -ForegroundColor Red
    exit 1
}

try {
    # Read and parse JSON
    $jsonContent = Get-Content $OutputFile -Raw | ConvertFrom-Json
    
    # Check required fields
    $requiredFields = @("metadata", "extracted_sections", "subsection_analysis")
    foreach ($field in $requiredFields) {
        if (-not $jsonContent.PSObject.Properties.Name.Contains($field)) {
            Write-Host "Missing required field: $field" -ForegroundColor Red
            exit 1
        }
    }
    
    # Check metadata
    $metadata = $jsonContent.metadata
    $metadataFields = @("input_documents", "persona", "job_to_be_done", "processing_timestamp")
    foreach ($field in $metadataFields) {
        if (-not $metadata.PSObject.Properties.Name.Contains($field)) {
            Write-Host "Missing metadata field: $field" -ForegroundColor Red
            exit 1
        }
    }
    
    # Check sections
    $sections = $jsonContent.extracted_sections
    if ($sections.Count -eq 0) {
        Write-Host "No extracted sections found" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Found $($sections.Count) extracted sections" -ForegroundColor Green
    Write-Host "Found $($jsonContent.subsection_analysis.Count) subsection analyses" -ForegroundColor Green
    
    # Check processing time
    if ($metadata.PSObject.Properties.Name.Contains("processing_time_seconds")) {
        $processingTime = $metadata.processing_time_seconds
        Write-Host "Processing time: $processingTime seconds" -ForegroundColor Cyan
        
        if ($processingTime -gt 60) {
            Write-Host "Warning: Processing time exceeds 60 seconds constraint" -ForegroundColor Yellow
        }
    }
    
    Write-Host "Output validation passed!" -ForegroundColor Green
    
} catch {
    Write-Host "Invalid JSON format: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}