
#!/usr/bin/env python3
"""
Local testing script for Challenge 1B solution
This script helps test the solution locally before Docker deployment
"""

import os
import sys
import json
import tempfile
import shutil
from main import DocumentIntelligenceSystem

def create_test_files():
    """Create sample test files for local testing"""
    test_dir = "test_input"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create sample persona.txt
    with open(os.path.join(test_dir, "persona.txt"), "w") as f:
        f.write("PhD Researcher in Computational Biology")
    
    # Create sample job.txt
    with open(os.path.join(test_dir, "job.txt"), "w") as f:
        f.write("Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks")
    
    print(f"Created test configuration files in {test_dir}/")
    print("Please add your PDF files to this directory before running the test.")
    return test_dir

def test_solution():
    """Test the solution locally"""
    input_dir = "test_input"
    output_dir = "test_output"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print("Creating test input directory...")
        create_test_files()
        return
    
    # Check for PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {input_dir}/")
        print("Please add PDF files to test the solution.")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("Initializing Document Intelligence System...")
        system = DocumentIntelligenceSystem()
        
        print(f"Processing {len(pdf_files)} PDF files...")
        result = system.process_documents(input_dir)
        
        # Save result
        output_file = os.path.join(output_dir, "challenge1b_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Success! Output saved to {output_file}")
        print(f"📊 Found {len(result['extracted_sections'])} relevant sections")
        print(f"🔍 Generated {len(result['sub_section_analysis'])} sub-section analyses")
        
        # Display top 3 sections
        print("\n📋 Top 3 Most Relevant Sections:")
        for i, section in enumerate(result['extracted_sections'][:3]):
            print(f"  {i+1}. {section['section_title']} (Page {section['page_number']}, {section['document']})")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

def validate_output(output_file):
    """Validate the output JSON format"""
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        required_keys = ['metadata', 'extracted_sections', 'sub_section_analysis']
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Validate metadata
        metadata_keys = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
        for key in metadata_keys:
            if key not in data['metadata']:
                print(f"❌ Missing metadata key: {key}")
                return False
        
        print("✅ Output format validation passed!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Output file not found: {output_file}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_test_files()
    elif len(sys.argv) > 1 and sys.argv[1] == "validate":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "test_output/challenge1b_output.json"
        validate_output(output_file)
    else:
        test_solution()


### 🎯 UTILITY FILES (3 files)
