import json
import os
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
import PyPDF2
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    def __init__(self):
        # Initialize lightweight sentence transformer model (~23MB)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))
        
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF page by page"""
        text_by_page = {}
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_by_page[page_num] = text
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
        return text_by_page
    
    def identify_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Identify sections within the text based on formatting patterns"""
        sections = []
        
        # Enhanced patterns for section headers
        patterns = [
            r'^[A-Z][A-Za-z\s\-,]+:',  # Title with colon
            r'^\d+\.?\s+[A-Z][A-Za-z\s\-,]+',  # Numbered sections
            r'^[IVX]+\.?\s+[A-Z][A-Za-z\s\-,]+',  # Roman numerals
            r'^[A-Z][A-Z\s]{3,}$',  # ALL CAPS headers (min 3 chars)
            r'^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$',  # Title case headers
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+',  # Two capitalized words
            r'^\d+\.\d+\s+[A-Z]',  # Subsection numbering (1.1, 2.3, etc.)
        ]
        
        lines = text.split('\n')
        current_section = {"title": "Content", "content": [], "page": page_num}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            # Check if line matches header patterns and is reasonably short
            for pattern in patterns:
                if re.match(pattern, line) and 5 <= len(line) <= 120:
                    # Additional validation: shouldn't be all uppercase unless it's short
                    if line.isupper() and len(line) > 50:
                        continue
                    is_header = True
                    break
            
            if is_header:
                if current_section["content"]:
                    current_section["content"] = " ".join(current_section["content"])
                    sections.append(current_section)
                current_section = {"title": line, "content": [], "page": page_num}
            else:
                current_section["content"].append(line)
        
        # Add the last section
        if current_section["content"]:
            current_section["content"] = " ".join(current_section["content"])
            sections.append(current_section)
        
        return sections
    
    def calculate_relevance_score(self, text: str, section_title: str, persona: str, job: str) -> float:
        """Calculate relevance score using multiple factors"""
        try:
            # Combine title and content for better context
            full_text = f"{section_title} {text}"
            context = f"{persona} needs to {job}"
            
            # Semantic similarity using sentence transformers
            text_embedding = self.model.encode([full_text])
            context_embedding = self.model.encode([context])
            semantic_score = cosine_similarity(text_embedding, context_embedding)[0][0]
            
            # Keyword matching score
            job_keywords = self.extract_keywords(job.lower())
            persona_keywords = self.extract_keywords(persona.lower())
            all_keywords = job_keywords + persona_keywords
            
            text_lower = full_text.lower()
            keyword_matches = sum(1 for keyword in all_keywords if keyword in text_lower)
            keyword_score = min(keyword_matches / max(len(all_keywords), 1), 1.0)
            
            # Length penalty (prefer substantial content)
            length_score = min(len(text.split()) / 100.0, 1.0)
            
            # Title relevance boost
            title_boost = 0.1 if any(keyword in section_title.lower() for keyword in all_keywords) else 0
            
            # Combine scores with weights
            final_score = (0.5 * semantic_score + 
                          0.3 * keyword_score + 
                          0.1 * length_score + 
                          title_boost)
            
            return float(final_score)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.0
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and len(word) > 2 and word not in self.stop_words]
        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(15)]
    
    def refine_subsection_text(self, text: str, max_length: int = 200) -> str:
        """Refine and clean subsection text"""
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        if len(text) <= max_length:
            return text
        
        # If text is too long, try to break at sentence boundaries
        sentences = sent_tokenize(text)
        result = ""
        for sentence in sentences:
            if len(result + sentence) <= max_length:
                result += sentence + " "
            else:
                break
        
        return result.strip() if result else text[:max_length].strip()
    
    def process_documents(self, input_dir: str) -> Dict[str, Any]:
        """Process all documents in the input directory"""
        
        # Read configuration files
        persona_file = os.path.join(input_dir, "persona.txt")
        job_file = os.path.join(input_dir, "job.txt")
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = f.read().strip()
        except FileNotFoundError:
            persona = "General Reader"
            logger.warning("persona.txt not found, using default persona")
        
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job = f.read().strip()
        except FileNotFoundError:
            job = "Extract key information from documents"
            logger.warning("job.txt not found, using default job")
        
        documents = []
        all_sections = []
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        pdf_files.sort()  # Ensure consistent ordering
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        logger.info(f"Persona: {persona}")
        logger.info(f"Job: {job}")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_dir, pdf_file)
            logger.info(f"Processing {pdf_file}")
            
            # Extract text from PDF
            text_by_page = self.extract_text_from_pdf(pdf_path)
            documents.append(pdf_file)
            
            # Process each page
            for page_num, text in text_by_page.items():
                sections = self.identify_sections(text, page_num)
                
                for section in sections:
                    if len(section["content"]) < 50:  # Skip very short sections
                        continue
                        
                    relevance_score = self.calculate_relevance_score(
                        section["content"], section["title"], persona, job
                    )
                    
                    section_data = {
                        "document": pdf_file,
                        "page": page_num,
                        "section_title": section["title"],
                        "content": section["content"],
                        "relevance_score": relevance_score
                    }
                    all_sections.append(section_data)
        
        # Sort by relevance score (descending)
        all_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Create output structure
        result = {
            "metadata": {
                "input_documents": documents,
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "sub_section_analysis": []
        }
        
        # Add top relevant sections (limit to top 15 for quality)
        top_sections = all_sections[:15]
        
        for i, section in enumerate(top_sections):
            result["extracted_sections"].append({
                "document": section["document"],
                "page_number": section["page"],
                "section_title": section["section_title"],
                "importance_rank": i + 1
            })
        
        # Create refined sub-sections
        for section in top_sections[:10]:  # Top 10 sections for sub-analysis
            # Split content into meaningful chunks
            sentences = sent_tokenize(section["content"])
            
            # Score sentences individually
            sentence_scores = []
            for sentence in sentences:
                if len(sentence.strip()) > 30:  # Filter very short sentences
                    score = self.calculate_relevance_score(sentence, section["section_title"], persona, job)
                    sentence_scores.append((sentence, score))
            
            # Sort sentences by relevance and take top 2-3 per section
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            for sentence, score in sentence_scores[:3]:
                refined_text = self.refine_subsection_text(sentence)
                result["sub_section_analysis"].append({
                    "document": section["document"],
                    "section_title": section["section_title"],
                    "refined_text": refined_text,
                    "page_number": section["page"]
                })
        
        logger.info(f"Processed {len(all_sections)} sections, selected top {len(result['extracted_sections'])}")
        return result

def main():
    """Main execution function"""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialize the system
        logger.info("Initializing Document Intelligence System...")
        system = DocumentIntelligenceSystem()
        
        # Process documents
        logger.info("Processing documents...")
        result = system.process_documents(input_dir)
        
        # Save result
        output_file = os.path.join(output_dir, "challenge1b_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete. Output saved to {output_file}")
        logger.info(f"Found {len(result['extracted_sections'])} relevant sections")
        logger.info(f"Generated {len(result['sub_section_analysis'])} sub-section analyses")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()