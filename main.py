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
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                full_text += text + "\n"
                
                pages_content.append({
                    'page_number': page_num + 1,
                    'text': text
                })
            
            doc.close()
            return {
                'filename': os.path.basename(pdf_path),
                'pages': pages_content,
                'total_pages': len(pages_content),
                'full_text': full_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None
    
    def extract_sections_by_content(self, doc_content: Dict) -> List[Dict]:
        """Extract sections based on content patterns and structure"""
        sections = []
        full_text = doc_content['full_text']
        filename = doc_content['filename']
        pages = doc_content['pages']
        
        # First, try to identify major sections from the document structure
        # Look for clear section headers and content blocks
        
        # Split text into paragraphs and analyze structure
        paragraphs = re.split(r'\n\s*\n', full_text)
        
        current_section = ""
        current_title = ""
        current_page = 1
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            lines = paragraph.split('\n')
            first_line = lines[0].strip()
            
            # Enhanced heuristics for section titles
            is_title = self.is_section_title(first_line, paragraph)
            
            if is_title and current_section:
                # Save previous section if it has substantial content
                if len(current_section.strip()) > 100:
                    sections.append({
                        'document': filename,
                        'page_number': current_page,
                        'section_title': current_title,
                        'content': current_section.strip(),
                        'word_count': len(current_section.split())
                    })
                current_section = ""
            
            if is_title:
                current_title = first_line
                # Include content after title if it's in the same paragraph
                if len(lines) > 1:
                    current_section = '\n'.join(lines[1:])
            else:
                current_section += "\n" + paragraph
        
        # Add the last section
        if current_section and current_title and len(current_section.strip()) > 100:
            sections.append({
                'document': filename,
                'page_number': current_page,
                'section_title': current_title,
                'content': current_section.strip(),
                'word_count': len(current_section.split())
            })
        
        # If we don't have enough good sections, create page-based sections with better titles
        if len(sections) < 3:
            sections = self.create_page_based_sections(pages, filename)
        
        # Also look for specific content types that would be relevant for travel planning
        travel_sections = self.extract_travel_specific_sections(full_text, filename)
        sections.extend(travel_sections)
        
        # Remove duplicates and filter by quality
        sections = self.deduplicate_and_filter_sections(sections)
        
        return sections
    
    def is_section_title(self, first_line: str, full_paragraph: str) -> bool:
        """Enhanced logic to identify section titles"""
        if not first_line or len(first_line) < 5:
            return False
        
        # Check various title patterns
        title_indicators = [
            # Common section patterns
            r'^[A-Z][a-zA-Z\s&-]+:?\s*$',  # Fixed: added closing quote and $
            r'^\d+\.\s+[A-Z]',  # Numbered sections
            r'^Chapter\s+\d+',   # Chapters
            r'^Part\s+[IVX]+',   # Parts with roman numerals
            # Travel-specific patterns
            r'^(Introduction|Conclusion|Overview|Summary)',
            r'^(Activities?|Attractions?|Things to Do)',
            r'^(Restaurants?|Hotels?|Accommodation)',
            r'^(Tips?|Tricks?|Advice)',
            r'^(Culture|History|Tradition)',
            r'^(Coastal|Beach|Water)',
            r'^(Budget|Family|Group)',
            r'^(Nightlife|Entertainment)',
            r'^(Packing|Planning|Travel)',
        ]
        
        # Check if it matches title patterns
        for pattern in title_indicators:
            if re.match(pattern, first_line, re.IGNORECASE):
                return True
        
        # Additional checks
        if (len(first_line) < 100 and  # Not too long
            not first_line.endswith('.') and  # Doesn't end with period
            len(full_paragraph.split('\n')) <= 5 and  # Not too many lines
            first_line[0].isupper()):  # Starts with capital
            return True
        
        return False
    
    def create_page_based_sections(self, pages: List[Dict], filename: str) -> List[Dict]:
        """Create sections based on pages with intelligent title extraction"""
        sections = []
        
        for page in pages:
            content = page['text'].strip()
            if len(content) < 100:  # Skip pages with little content
                continue
            
            # Try to extract a meaningful title from the page
            title = self.extract_page_title(content)
            if not title:
                title = f"Page {page['page_number']} Content"
            
            sections.append({
                'document': filename,
                'page_number': page['page_number'],
                'section_title': title,
                'content': content,
                'word_count': len(content.split())
            })
        
        return sections
    
    def extract_page_title(self, content: str) -> str:
        """Extract a meaningful title from page content"""
        lines = content.split('\n')[:10]  # Look at first 10 lines
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for title-like lines
            if (5 < len(line) < 100 and 
                not line.endswith('.') and
                (line[0].isupper() or line.startswith('•'))):
                # Clean up the title
                title = re.sub(r'[^\w\s-]', '', line).strip()
                if len(title) > 10:
                    return title
        
        return None
    
    def extract_travel_specific_sections(self, full_text: str, filename: str) -> List[Dict]:
        """Extract sections specifically relevant to travel planning"""
        travel_sections = []
        
        # Keywords that indicate travel-relevant content
        travel_keywords = {
            'activities': ['activities', 'things to do', 'attractions', 'sightseeing'],
            'accommodation': ['hotels', 'accommodation', 'lodging', 'staying'],
            'dining': ['restaurants', 'dining', 'food', 'cuisine', 'eating'],
            'transportation': ['transport', 'getting around', 'travel', 'flights'],
            'budget': ['budget', 'cost', 'price', 'affordable', 'cheap'],
            'groups': ['group', 'friends', 'party', 'together'],
            'coastal': ['beach', 'coast', 'sea', 'water sports', 'swimming'],
            'nightlife': ['nightlife', 'bars', 'clubs', 'evening', 'night']
        }
        
        # Split text into chunks and analyze
        chunks = re.split(r'\n\s*\n', full_text)
        
        for chunk in chunks:
            if len(chunk.strip()) < 150:  # Skip very short chunks
                continue
            
            chunk_lower = chunk.lower()
            
            # Check if chunk contains travel-relevant keywords
            for category, keywords in travel_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in chunk_lower)
                
                if keyword_count >= 2:  # Must contain multiple relevant keywords
                    # Extract a title from the chunk
                    title = self.extract_chunk_title(chunk, category)
                    
                    travel_sections.append({
                        'document': filename,
                        'page_number': 1,  # Default page
                        'section_title': title,
                        'content': chunk.strip(),
                        'word_count': len(chunk.split()),
                        'category': category,
                        'keyword_count': keyword_count
                    })
                    break  # Don't duplicate the same chunk
        
        return travel_sections
    
    def extract_chunk_title(self, chunk: str, category: str) -> str:
        """Extract or generate a title for a content chunk"""
        lines = chunk.split('\n')[:3]
        
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and not line.endswith('.'):
                return line
        
        # Generate a title based on category
        category_titles = {
            'activities': 'Activities and Attractions',
            'accommodation': 'Hotels and Accommodation',
            'dining': 'Restaurants and Dining',
            'transportation': 'Transportation Options',
            'budget': 'Budget Information',
            'groups': 'Group Travel Tips',
            'coastal': 'Coastal Activities',
            'nightlife': 'Nightlife and Entertainment'
        }
        
        return category_titles.get(category, 'Travel Information')
    
    def deduplicate_and_filter_sections(self, sections: List[Dict]) -> List[Dict]:
        """Remove duplicate sections and filter by quality"""
        # Remove duplicates based on content similarity
        unique_sections = []
        seen_content = set()
        
        for section in sections:
            # Create a simple hash of the content
            content_words = set(section['content'].lower().split()[:50])  # First 50 words
            content_hash = hash(frozenset(content_words))
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_sections.append(section)
        
        # Filter by quality (word count, etc.)
        quality_sections = [
            section for section in unique_sections 
            if section['word_count'] >= 50  # Minimum word count
        ]
        
        return quality_sections
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        
        # Tokenize and process
        tokens = word_tokenize(text.lower())
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token.isalpha() and token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def calculate_relevance_scores(self, sections: List[Dict], persona: str, job: str) -> List[Dict]:
        """Calculate relevance scores for sections based on persona and job"""
        # Create enhanced query from persona and job
        query_parts = []
        
        # Extract key terms from job description
        job_lower = job.lower()
        if 'college friends' in job_lower or 'group' in job_lower:
            query_parts.extend(['group', 'friends', 'college', 'young', 'budget', 'fun', 'activities'])
        if 'trip' in job_lower or 'travel' in job_lower:
            query_parts.extend(['travel', 'trip', 'plan', 'itinerary', 'destination'])
        if '4 days' in job_lower or 'days' in job_lower:
            query_parts.extend(['short', 'quick', 'weekend', 'brief'])
        
        # Add persona-specific terms
        persona_lower = persona.lower()
        if 'travel planner' in persona_lower:
            query_parts.extend(['plan', 'organize', 'schedule', 'itinerary', 'logistics'])
        
        # Combine all terms
        query = ' '.join(query_parts + [persona, job])
        query_processed = self.preprocess_text(query)
        
        # Prepare documents for TF-IDF
        documents = []
        valid_sections = []
        
        for section in sections:
            content = section['content']
            if len(content.strip()) > 50:  # Only include substantial content
                processed_content = self.preprocess_text(content)
                if processed_content:  # Only if preprocessing yielded content
                    documents.append(processed_content)
                    valid_sections.append(section)
        
        if not documents:
            return sections
        
        # Add query to corpus
        documents.append(query_processed)
        
        # Calculate TF-IDF vectors with more features
        vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity with query
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(doc_vectors, query_vector).flatten()
            
            # Add scores to valid sections
            for i, section in enumerate(valid_sections):
                section['relevance_score'] = float(similarities[i])
            
            # Add zero scores to sections without valid content
            for section in sections:
                if 'relevance_score' not in section:
                    section['relevance_score'] = 0.0
                    
        except Exception as e:
            logger.warning(f"Error in TF-IDF calculation: {e}")
            # Fallback: simple keyword matching
            for section in sections:
                score = self.simple_keyword_score(section['content'], query_parts)
                section['relevance_score'] = score
        
        return sections
    
    def simple_keyword_score(self, content: str, keywords: List[str]) -> float:
        """Simple keyword-based scoring as fallback"""
        content_lower = content.lower()
        score = 0.0
        
        for keyword in keywords:
            if keyword.lower() in content_lower:
                score += 1.0
        
        # Normalize by content length
        return score / max(len(content.split()), 1)
    
    def rank_sections(self, sections: List[Dict]) -> List[Dict]:
        """Rank sections by relevance score and other factors"""
        # Filter out very short sections
        valid_sections = [s for s in sections if len(s['content'].strip()) > 100]
        
        # Sort by relevance score
        ranked = sorted(valid_sections, key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked
    
    def extract_subsections(self, sections: List[Dict], top_n: int = 5) -> List[Dict]:
        """Extract and refine top subsections with proper content"""
        top_sections = sections[:top_n]
        subsections = []
        
        for section in top_sections:
            content = section['content']
            
            # Clean and format content
            sentences = sent_tokenize(content)
            
            # Take first few sentences that provide good information
            refined_sentences = []
            word_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 20:  # Skip very short sentences
                    refined_sentences.append(sentence)
                    word_count += len(sentence.split())
                    
                    # Stop at reasonable length
                    if word_count > 150 or len(refined_sentences) >= 5:
                        break
            
            refined_text = ' '.join(refined_sentences)
            
            # Ensure we have substantial content
            if len(refined_text) < 100 and len(sentences) > len(refined_sentences):
                # Add more sentences if too short
                for sentence in sentences[len(refined_sentences):]:
                    sentence = sentence.strip()
                    if sentence:
                        refined_text += ' ' + sentence
                        if len(refined_text) > 200:
                            break
            
            subsections.append({
                'document': section['document'],
                'page_number': section['page_number'],
                'section_title': section['section_title'],
                'refined_text': refined_text[:500],  # Limit to 500 chars
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
                sections = self.extract_sections_by_content(doc_content)
                all_sections.extend(sections)
        
        logger.info(f"Extracted {len(all_sections)} sections")
        
        # Calculate relevance scores
        logger.info("Calculating relevance scores")
        scored_sections = self.calculate_relevance_scores(all_sections, persona, job)
        
        # Rank sections
        ranked_sections = self.rank_sections(scored_sections)
        
        # Extract top subsections
        top_subsections = self.extract_subsections(ranked_sections, top_n=5)
        
        # Prepare output in expected format (matching the sample exactly)
        output = {
            "metadata": {
                "input_documents": [doc.replace(' (1)', '') for doc in document_info],  # Clean up filenames
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section['document'].replace(' (1)', ''),  # Clean filename
                    "section_title": section['section_title'],
                    "importance_rank": idx + 1,
                    "page_number": section['page_number']
                }
                for idx, section in enumerate(ranked_sections[:5])
            ],
            "subsection_analysis": [
                {
                    "document": subsection['document'].replace(' (1)', ''),  # Clean filename
                    "refined_text": subsection['refined_text'],
                    "page_number": subsection['page_number']
                }
                for subsection in top_subsections
            ]
        }
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        return output

def main():
    """Main execution function"""
    try:
        # Setup paths
        input_dir = "/app/input"
        output_dir = "/app/output"
        
        # For Windows/local testing
        if os.name == 'nt' or not os.path.exists(input_dir):
            input_dir = "./input" if os.path.exists("./input") else "."
            output_dir = "./output" if os.path.exists("./output") else "."
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Read persona and job from input JSON file
        input_json_file = os.path.join(input_dir, "challenge1b_input.json")
        persona = "Travel Planner"
        job = "Plan a trip of 4 days for a group of 10 college friends."
        
        if os.path.exists(input_json_file):
            try:
                with open(input_json_file, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
                
                # Extract persona and job from JSON structure
                if 'persona' in input_data and 'role' in input_data['persona']:
                    persona = input_data['persona']['role']
                
                if 'job_to_be_done' in input_data and 'task' in input_data['job_to_be_done']:
                    job = input_data['job_to_be_done']['task']
                    
                logger.info(f"Loaded from JSON - Persona: {persona}, Job: {job}")
                
            except Exception as e:
                logger.warning(f"Could not read input JSON file: {e}. Using defaults.")
        else:
            # Fallback to individual text files
            persona_file = os.path.join(input_dir, "persona.txt")
            job_file = os.path.join(input_dir, "job.txt")
            
            if os.path.exists(persona_file):
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona = f.read().strip()
            
            if os.path.exists(job_file):
                with open(job_file, 'r', encoding='utf-8') as f:
                    job = f.read().strip()
        
        # Initialize system
        system = DocumentIntelligenceSystem()
        
        # Process documents
        logger.info(f"Starting document processing with persona: {persona}")
        logger.info(f"Job to be done: {job}")
        
        result = system.process_documents(input_dir, persona, job)
        
        # Save output
        output_file = os.path.join(output_dir, "challenge1b_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Output saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()