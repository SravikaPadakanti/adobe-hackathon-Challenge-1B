import re
import os
from pathlib import Path
from typing import List, Dict

def validate_pdf_files(input_dir: str) -> List[str]:
    """Validate PDF files in input directory"""
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    if not pdf_files:
        raise ValueError("No PDF files found in input directory")
    
    if len(pdf_files) > 10:
        raise ValueError(f"Too many PDF files ({len(pdf_files)}). Maximum is 10.")
    
    # Check file sizes
    large_files = []
    for pdf_file in pdf_files:
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        if size_mb > 50:  # Assuming ~1MB per page, 50MB = ~50 pages
            large_files.append(f"{pdf_file.name} ({size_mb:.1f}MB)")
    
    if large_files:
        print(f"Warning: Large files detected: {', '.join(large_files)}")
    
    return [str(f) for f in pdf_files]

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    # Remove very short lines (likely artifacts)
    lines = text.split('\n')
    lines = [line.strip() for line in lines if len(line.strip()) > 3]
    
    return '\n'.join(lines)

def estimate_processing_time(num_documents: int, avg_pages_per_doc: int = 10) -> float:
    """Estimate processing time based on document count"""
    # Rough estimates based on typical performance
    base_time = 5  # Base overhead
    time_per_page = 0.3  # Seconds per page
    
    total_pages = num_documents * avg_pages_per_doc
    estimated_time = base_time + (total_pages * time_per_page)
    
    return estimated_time
