#!/usr/bin/env python3
"""
Test script for the Document Intelligence System
"""

import json
import os
import sys
from pathlib import Path

def create_test_input():
    """Create a test input JSON file in the correct format"""
    test_input = {
        "challenge_info": {
            "challenge_id": "round_1b_002",
            "test_case_name": "travel_planner",
            "description": "France Travel"
        },
        "documents": [
            {
                "filename": "South of France - Cities.pdf",
                "title": "South of France - Cities"
            },
            {
                "filename": "South of France - Cuisine.pdf",
                "title": "South of France - Cuisine"
            },
            {
                "filename": "South of France - History.pdf",
                "title": "South of France - History"
            },
            {
                "filename": "South of France - Restaurants and Hotels.pdf",
                "title": "South of France - Restaurants and Hotels"
            },
            {
                "filename": "South of France - Things to Do.pdf",
                "title": "South of France - Things to Do"
            },
            {
                "filename": "South of France - Tips and Tricks.pdf",
                "title": "South of France - Tips and Tricks"
            },
            {
                "filename": "South of France - Traditions and Culture.pdf",
                "title": "South of France - Traditions and Culture"
            }
        ],
        "persona": {
            "role": "Travel Planner"
        },
        "job_to_be_done": {
            "task": "Plan a trip of 4 days for a group of 10 college friends."
        }
    }
    
    # Create input directory if it doesn't exist
    os.makedirs("input", exist_ok=True)
    
    # Save the input file
    with open("input/challenge1b_input.json", "w", encoding="utf-8") as f:
        json.dump(test_input, f, indent=4)
    
    print("✅ Created test input file: input/challenge1b_input.json")

def validate_output(output_file: str):
    """Validate the output format"""
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            output = json.load(f)
        
        # Check required fields
        required_fields = ['metadata', 'extracted_sections', 'subsection_analysis']
        for field in required_fields:
            if field not in output:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check metadata
        metadata = output['metadata']
        metadata_fields = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
        for field in metadata_fields:
            if field not in metadata:
                print(f"❌ Missing metadata field: {field}")
                return False
        
        # Check extracted sections format
        sections = output['extracted_sections']
        if not isinstance(sections, list) or len(sections) == 0:
            print("❌ extracted_sections should be a non-empty list")
            return False
        
        section_fields = ['document', 'section_title', 'importance_rank', 'page_number']
        for i, section in enumerate(sections):
            for field in section_fields:
                if field not in section:
                    print(f"❌ Missing field '{field}' in extracted_sections[{i}]")
                    return False
        
        # Check subsection analysis format
        subsections = output['subsection_analysis']
        if not isinstance(subsections, list) or len(subsections) == 0:
            print("❌ subsection_analysis should be a non-empty list")
            return False
        
        subsection_fields = ['document', 'refined_text', 'page_number']
        for i, subsection in enumerate(subsections):
            for field in subsection_fields:
                if field not in subsection:
                    print(f"❌ Missing field '{field}' in subsection_analysis[{i}]")
                    return False
        
        print("✅ Output format validation passed")
        print(f"📊 Found {len(sections)} extracted sections")
        print(f"📊 Found {len(subsections)} subsection analyses")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating output: {e}")
        return False

def run_test():
    """Run the complete test"""
    print("🧪 Starting Document Intelligence System Test")
    print("=" * 50)
    
    # Step 1: Create test input
    create_test_input()
    
    # Step 2: Check if PDF files exist
    pdf_files = list(Path("input").glob("*.pdf"))
    if not pdf_files:
        print("⚠️  Warning: No PDF files found in input directory")
        print("   Please ensure your PDF files are in the 'input' directory")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Step 3: Run the main system
    print("\n🚀 Running document processing...")
    try:
        # Import and run the main system
        from main import main
        main()
        print("✅ Processing completed successfully")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return
    
    # Step 4: Validate output
    print("\n🔍 Validating output...")
    output_file = "output/challenge1b_output.json"
    if validate_output(output_file):
        print("🎉 Test completed successfully!")
        
        # Show sample output
        with open(output_file, 'r', encoding='utf-8') as f:
            output = json.load(f)
        
        print("\n📋 Sample extracted sections:")
        for i, section in enumerate(output['extracted_sections'][:3]):
            print(f"   {i+1}. {section['section_title']} ({section['document']})")
        
    else:
        print("❌ Test failed - output validation errors")

if __name__ == "__main__":
    run_test()
