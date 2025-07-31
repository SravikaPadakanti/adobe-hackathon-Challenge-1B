# main.py
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple
import re

# PDF processing
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ML/NLP libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    def __init__(self):
        """Initialize the document intelligence system"""
        self.setup_nltk()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def setup_nltk(self):
        """Download required NLTK data if not present"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text content from PDF with page information"""
        try:
            doc = fitz.open(pdf_path)
            pages_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Extract potential headings (lines with larger fonts or bold text)
                blocks = page.get_text("dict")
                headings = self.extract_headings_from_blocks(blocks, page_num + 1)
                
                pages_content.append({
                    'page_number': page_num + 1,
                    'text': text,
                    'headings': headings
                })
            
            doc.close()
            return {
                'filename': os.path.basename(pdf_path),
                'pages': pages_content,
                'total_pages': len(pages_content)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None
    
    def extract_headings_from_blocks(self, blocks: Dict, page_num: int) -> List[Dict]:
        """Extract headings from PDF blocks based on font properties"""
        headings = []
        
        if 'blocks' not in blocks:
            return headings
            
        for block in blocks['blocks']:
            if 'lines' not in block:
                continue
                
            for line in block['lines']:
                if 'spans' not in line:
                    continue
                    
                for span in line['spans']:
                    text = span.get('text', '').strip()
                    if not text or len(text) < 3:
                        continue
                    
                    font_size = span.get('size', 0)
                    font_flags = span.get('flags', 0)
                    
                    # Check if it's likely a heading (larger font or bold)
                    is_bold = font_flags & 2**4  # Bold flag
                    is_heading = font_size > 12 or is_bold
                    
                    if is_heading and self.is_likely_heading(text):
                        headings.append({
                            'text': text,
                            'page': page_num,
                            'font_size': font_size,
                            'is_bold': bool(is_bold)
                        })
        
        return headings
    
    def is_likely_heading(self, text: str) -> bool:
        """Determine if text is likely a heading"""
        # Filter out very long texts, numbers only, and common non-heading patterns
        if len(text) > 100 or text.isdigit():
            return False
        
        # Common heading patterns
        heading_patterns = [
            r'^[A-Z][a-z]+.*',  # Starts with capital
            r'^\d+\.?\s+[A-Z]',  # Numbered heading
            r'^[IVX]+\.?\s+',    # Roman numerals
            r'^Chapter\s+\d+',   # Chapter headings
            r'^Section\s+\d+',   # Section headings
        ]
        
        return any(re.match(pattern, text) for pattern in heading_patterns)
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token.isalpha() and token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def extract_sections_from_document(self, doc_content: Dict) -> List[Dict]:
        """Extract sections from document based on headings and content"""
        sections = []
        pages = doc_content['pages']
        
        for page in pages:
            headings = page['headings']
            page_text = page['text']
            
            if headings:
                # Use headings to define sections
                for heading in headings:
                    # Extract text around the heading (rough approximation)
                    heading_text = heading['text']
                    section_text = self.extract_section_text(page_text, heading_text)
                    
                    sections.append({
                        'document': doc_content['filename'],
                        'page_number': page['page_number'],
                        'section_title': heading_text,
                        'content': section_text,
                        'preprocessed_content': self.preprocess_text(section_text)
                    })
            else:
                # If no headings, treat entire page as a section
                sections.append({
                    'document': doc_content['filename'],
                    'page_number': page['page_number'],
                    'section_title': f"Page {page['page_number']} Content",
                    'content': page_text,
                    'preprocessed_content': self.preprocess_text(page_text)
                })
        
        return sections
    
    def extract_section_text(self, page_text: str, heading_text: str) -> str:
        """Extract text content for a section based on heading"""
        lines = page_text.split('\n')
        section_lines = []
        found_heading = False
        
        for line in lines:
            if heading_text.lower() in line.lower():
                found_heading = True
                section_lines = [line]
                continue
            
            if found_heading:
                # Stop at next potential heading or collect content
                if len(section_lines) > 20:  # Limit section size
                    break
                section_lines.append(line)
        
        return '\n'.join(section_lines) if section_lines else page_text[:500]
    
    def calculate_relevance_scores(self, sections: List[Dict], persona: str, job: str) -> List[Dict]:
        """Calculate relevance scores for sections based on persona and job"""
        # Combine persona and job to create query
        query = f"{persona} {job}"
        query_processed = self.preprocess_text(query)
        
        # Prepare documents for TF-IDF
        documents = [section['preprocessed_content'] for section in sections]
        documents.append(query_processed)  # Add query to corpus
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity with query
        query_vector = tfidf_matrix[-1]  # Last vector is the query
        doc_vectors = tfidf_matrix[:-1]  # All but last are documents
        
        similarities = cosine_similarity(doc_vectors, query_vector).flatten()
        
        # Add scores to sections
        for i, section in enumerate(sections):
            section['relevance_score'] = float(similarities[i])
        
        return sections
    
    def rank_sections(self, sections: List[Dict]) -> List[Dict]:
        """Rank sections by relevance score"""
        return sorted(sections, key=lambda x: x['relevance_score'], reverse=True)
    
    def extract_subsections(self, sections: List[Dict], top_n: int = 10) -> List[Dict]:
        """Extract and refine top subsections"""
        top_sections = sections[:top_n]
        subsections = []
        
        for section in top_sections:
            content = section['content']
            sentences = sent_tokenize(content)
            
            # Take most relevant sentences (simplified approach)
            if len(sentences) > 3:
                # Keep first sentence and middle sentences
                refined_text = '. '.join([sentences[0]] + sentences[1:4])
            else:
                refined_text = content
            
            subsections.append({
                'document': section['document'],
                'page_number': section['page_number'],
                'section_title': section['section_title'],
                'refined_text': refined_text[:500],  # Limit length
                'relevance_score': section['relevance_score']
            })
        
        return subsections
    
    def process_documents(self, input_dir: str, persona: str, job: str) -> Dict[str, Any]:
        """Main processing function"""
        start_time = time.time()
        
        # Find all PDF files
        pdf_files = list(Path(input_dir).glob("*.pdf"))
        if not pdf_files:
            raise ValueError("No PDF files found in input directory")
        
        logger.info(f"Processing {len(pdf_files)} PDF files")
        
        # Extract content from all PDFs
        all_sections = []
        document_info = []
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            doc_content = self.extract_text_from_pdf(str(pdf_file))
            
            if doc_content:
                document_info.append(doc_content['filename'])
                sections = self.extract_sections_from_document(doc_content)
                all_sections.extend(sections)
        
        # Calculate relevance scores
        logger.info("Calculating relevance scores")
        scored_sections = self.calculate_relevance_scores(all_sections, persona, job)
        
        # Rank sections
        ranked_sections = self.rank_sections(scored_sections)
        
        # Extract top subsections
        top_subsections = self.extract_subsections(ranked_sections, top_n=15)
        
        # Prepare output
        output = {
            "metadata": {
                "input_documents": document_info,
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(time.time() - start_time, 2)
            },
            "extracted_sections": [
                {
                    "document": section['document'],
                    "page_number": section['page_number'],
                    "section_title": section['section_title'],
                    "importance_rank": idx + 1,
                    "relevance_score": round(section['relevance_score'], 4)
                }
                for idx, section in enumerate(ranked_sections[:15])
            ],
            "subsection_analysis": [
                {
                    "document": subsection['document'],
                    "page_number": subsection['page_number'],
                    "section_title": subsection['section_title'],
                    "refined_text": subsection['refined_text'],
                    "importance_rank": idx + 1,
                    "relevance_score": round(subsection['relevance_score'], 4)
                }
                for idx, subsection in enumerate(top_subsections)
            ]
        }
        
        return output

def main():
    """Main execution function"""
    try:
        # Setup paths
        input_dir = "/app/input"
        output_dir = "/app/output"
        
        # For Windows testing
        if os.name == 'nt':  # Windows
            input_dir = "./input"
            output_dir = "./output"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Read persona and job from input file or use defaults
        persona_file = os.path.join(input_dir, "persona.txt")
        job_file = os.path.join(input_dir, "job.txt")
        
        if os.path.exists(persona_file):
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = f.read().strip()
        else:
            persona = "Research Analyst"
        
        if os.path.exists(job_file):
            with open(job_file, 'r', encoding='utf-8') as f:
                job = f.read().strip()
        else:
            job = "Analyze and summarize key findings from the provided documents"
        
        # Initialize system
        system = DocumentIntelligenceSystem()
        
        # Process documents
        logger.info(f"Starting document processing with persona: {persona}")
        logger.info(f"Job to be done: {job}")
        
        result = system.process_documents(input_dir, persona, job)
        
        # Save output
        output_file = os.path.join(output_dir, "challenge1b_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing completed in {result['metadata']['processing_time_seconds']} seconds")
        logger.info(f"Output saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()