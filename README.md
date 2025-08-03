# Challenge 1B: Persona-Driven Document Intelligence

## Approach Explanation

### Overview
This solution implements a comprehensive document intelligence system that analyzes PDF collections based on specific personas and their job requirements. The system uses a combination of traditional NLP techniques and machine learning to extract, analyze, and rank document sections.

### Methodology

#### 1. PDF Text Extraction
- **PyMuPDF (fitz)**: Used for robust PDF text extraction with page-level granularity
- **Heading Detection**: Analyzes font properties (size, bold formatting) to identify potential headings
- **Structure Recognition**: Maintains document structure with page numbers and section boundaries

#### 2. Content Preprocessing
- **Text Normalization**: Removes extra whitespace and standardizes formatting
- **Tokenization**: Uses NLTK for sentence and word tokenization
- **Stopword Removal**: Filters common English stopwords
- **Stemming**: Applies Porter Stemmer for word normalization

#### 3. Relevance Scoring
- **TF-IDF Vectorization**: Converts text to numerical vectors using Term Frequency-Inverse Document Frequency
- **Cosine Similarity**: Measures semantic similarity between document sections and persona+job query
- **N-gram Features**: Includes both unigrams and bigrams for better context capture

#### 4. Section Ranking and Analysis
- **Importance Ranking**: Sorts sections by relevance scores in descending order
- **Subsection Refinement**: Extracts key sentences from top-ranked sections
- **Content Summarization**: Provides refined text snippets for easy consumption

### Libraries and Models Used

#### Core Dependencies
- **PyMuPDF (1.23.8)**: PDF processing and text extraction
- **NLTK (3.8.1)**: Natural language processing toolkit
- **scikit-learn (1.3.2)**: Machine learning algorithms (TF-IDF, cosine similarity)
- **NumPy (1.24.3)**: Numerical computing support

#### Model Specifications
- **TF-IDF Vectorizer**: Max 1000 features, 1-2 gram range
- **Dimensionality**: Controlled to stay within memory constraints
- **No external models**: All processing uses lightweight, built-in algorithms

### Performance Optimizations

#### Speed Optimizations
- **Efficient PDF parsing**: Direct text extraction without image processing
- **Limited feature space**: TF-IDF capped at 1000 features
- **Batch processing**: Processes all documents in memory simultaneously
- **Early stopping**: Limits section extraction to prevent infinite loops

#### Memory Management
- **Lightweight models**: No heavy neural networks or large language models
- **Streaming processing**: Processes documents one at a time when possible
- **Garbage collection**: Explicit cleanup of large objects

### Architecture Design

#### Modular Structure
```
DocumentIntelligenceSystem
├── PDF Processing Module
├── Text Preprocessing Module  
├── Relevance Scoring Module
└── Output Generation Module
```

#### Error Handling
- **Robust PDF parsing**: Handles corrupted or complex PDFs gracefully
- **Fallback mechanisms**: Uses page-level sections when headings unavailable
- **Logging system**: Comprehensive logging for debugging and monitoring

### Windows PowerShell Integration

#### Local Development
- **setup.ps1**: Automated environment setup
- **test_local.ps1**: Local testing without Docker
- **validate_output.ps1**: Output format validation

#### Docker Support
- **build_docker.ps1**: Cross-platform Docker image building
- **AMD64 compatibility**: Ensures Linux compatibility from Windows

## How to Build and Run

### Prerequisites
- Python 3.9+
- Docker Desktop (for containerized execution)
- PowerShell (Windows)

### Local Windows Setup
```powershell
# Initial setup
.\setup.ps1

# Place PDF files in ./input directory
# Optionally create persona.txt and job.txt in input directory

# Run locally
.\test_local.ps1

# Validate output
.\validate_output.ps1
```

### Docker Execution
```powershell
# Build and test Docker image
.\build_docker.ps1

# Manual Docker run
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none challenge1b:latest
```

### Input Format
```
input/
├── document1.pdf
├── document2.pdf
├── document3.pdf
├── persona.txt (optional)
└── job.txt (optional)
```

### Output Format
The system generates `challenge1b_output.json` with:
- **Metadata**: Processing information, timestamps, input documents
- **Extracted Sections**: Ranked document sections with importance scores
- **Subsection Analysis**: Refined text snippets from top sections

### Constraints Compliance
- ✅ **CPU Only**: No GPU dependencies
- ✅ **Model Size**: <1GB (actually <50MB with lightweight models)
- ✅ **Processing Time**: <60 seconds for 3-5 documents
- ✅ **No Internet**: All processing offline
- ✅ **AMD64 Compatible**: Docker builds for linux/amd64

### Error Recovery
The system includes comprehensive error handling:
- Skips corrupted PDFs with logging
- Falls back to page-level processing if heading detection fails
- Continues processing even if individual documents fail
- Provides detailed error messages for debugging

This solution balances accuracy, performance, and reliability while meeting all specified constraints for the Windows PowerShell environment.