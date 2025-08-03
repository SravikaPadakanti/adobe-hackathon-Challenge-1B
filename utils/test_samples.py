import os
import json
from pathlib import Path

def create_test_data():
    """Create sample test files for development"""
    
    # Create directories
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("test_data", exist_ok=True)
    
    # Sample persona configurations
    test_cases = [
        {
            "name": "academic_research",
            "persona": "PhD Researcher in Computational Biology",
            "job": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
        },
        {
            "name": "business_analysis", 
            "persona": "Investment Analyst",
            "job": "Analyze revenue trends, R&D investments, and market positioning strategies"
        },
        {
            "name": "student_study",
            "persona": "Undergraduate Chemistry Student", 
            "job": "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
        }
    ]
    
    # Create test case files
    for case in test_cases:
        case_dir = f"test_data/{case['name']}"
        os.makedirs(case_dir, exist_ok=True)
        
        with open(f"{case_dir}/persona.txt", 'w', encoding='utf-8') as f:
            f.write(case['persona'])
            
        with open(f"{case_dir}/job.txt", 'w', encoding='utf-8') as f:
            f.write(case['job'])
    
    print("Test data structure created successfully!")
    print("Add PDF files to test_data/<case_name>/ directories for testing")

if __name__ == "__main__":
    create_test_data()