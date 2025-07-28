# Adobe India Hackathon 2025 - Challenge 1B Solution
## Persona-Driven Document Intelligence

### Overview
This solution implements an intelligent document analysis system that extracts and prioritizes relevant sections from PDF collections based on specific personas and their job-to-be-done requirements.

### Key Features
- **Multi-PDF Processing**: Handles 3-10 related documents simultaneously
- **Semantic Understanding**: Uses sentence transformers for contextual relevance
- **Persona-Aware Ranking**: Tailors results to specific user roles and objectives
- **Offline Operation**: No internet dependencies during execution
- **Efficient Performance**: Optimized for CPU-only execution under 60 seconds

### Solution Architecture

#### Core Components
1. **DocumentIntelligenceSystem**: Main processing engine
2. **PDF Text Extractor**: Page-by-page content extraction
3. **Section Identifier**: Pattern-based document structure detection
4. **Relevance Scorer**: Multi-factor relevance calculation
5. **Sub-section Analyzer**: Granular content refinement

#### Models & Libraries Used
- **SentenceTransformers**: all-MiniLM-L6-v2 (~23MB) for semantic similarity
- **PyPDF2**: PDF text extraction
- **NLTK**: Natural language processing utilities
- **scikit-learn**: Cosine similarity calculations
- **PyTorch CPU**: Backend for transformer models

### Input Format
The system expects the following input structure:
```
/app/input/
├── document1.pdf
├── document2.pdf
├── document3.pdf
├── persona.txt          # Role description
└── job.txt             # Task description
```

### Output Format
Generates `challenge1b_output.json` with:
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare comprehensive literature review",
    "processing_timestamp": "2025-07-24T..."
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 1,
      "section_title": "Methodology",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "section_title": "Methodology",
      "refined_text": "The proposed approach utilizes...",
      "page_number": 1
    }
  ]
}
```

### Building and Running

#### Build Docker Image
```bash
docker build --platform linux/amd64 -t document-intelligence:latest .
```

#### Run Solution
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  document-intelligence:latest
```

### Performance Specifications
- **Execution Time**: ≤ 60 seconds for 3-5 documents
- **Model Size**: ≤ 1GB (actual: ~200MB)
- **Architecture**: CPU-only (amd64)
- **Memory**: Optimized for 16GB RAM systems
- **Network**: Completely offline operation

### Testing
1. Place PDF documents and configuration files in `input/` directory
2. Ensure `persona.txt` and `job.txt` contain appropriate descriptions
3. Run the Docker container
4. Check `output/challenge1b_output.json` for results

### Project Structure
```
├── main.py                 # Core implementation
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── approach_explanation.md # Detailed methodology
└── README.md             # This file
```

### Troubleshooting
- Ensure input PDFs are readable and not password-protected
- Verify persona.txt and job.txt exist and contain meaningful descriptions
- Check Docker platform compatibility (linux/amd64)
- Monitor execution time and adjust document count if needed

For questions or issues, refer to the approach_explanation.md for detailed technical information.
```

### 🪟 WINDOWS FILES (3 files)
