#!/usr/bin/env python3
"""
PDF Processor

A utility that can split PDFs by bookmarks and convert them to Markdown format.
"""

import os
import re
import argparse
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('pdf_processor')

class PdfSplitter:
    def __init__(self, pdf_path: str, output_dir: str, level: int = 1):
        """Initialize the PDF splitter."""
        self.pdf_path = Path(pdf_path).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.level = level
        self.doc = None
        self.toc = []
        
        # Create output directories
        self.pdf_output_dir = self.output_dir / "Split_PDFs"
        self.md_output_dir = self.output_dir / "MD_Files"
        self.pdf_output_dir.mkdir(parents=True, exist_ok=True)
        self.md_output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_filename(self, title: str) -> str:
        """Clean a string to be used as a filename."""
        clean = re.sub(r'[^\w\s-]', '', title).strip()
        return re.sub(r'[\s_]+', '_', clean).strip('_')
    
    def split_by_bookmarks(self) -> List[Dict]:
        """Split the PDF by bookmarks at the specified level."""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.toc = self.doc.get_toc()
            
            if not self.toc:
                logger.error("No bookmarks found in the PDF.")
                return []
            
            sections = []
            for i, (level, title, page) in enumerate(self.toc):
                if level == self.level:
                    next_page = None
                    for next_item in self.toc[i+1:]:
                        if next_item[0] <= level:
                            next_page = next_item[2]
                            break
                    
                    sections.append({
                        'start_page': page - 1,
                        'end_page': next_page - 2 if next_page else None,
                        'title': title,
                        'level': level
                    })
            
            if not sections:
                available_levels = sorted({item[0] for item in self.toc})
                logger.error(f"No bookmarks found at level {self.level}. Available levels: {available_levels}")
                return []
            
            logger.info(f"Found {len(sections)} sections at level {self.level}")
            
            created_files = []
            for i, section in enumerate(sections, 1):
                new_doc = fitz.open()
                start = section['start_page']
                end = section['end_page'] if section['end_page'] is not None else len(self.doc) - 1
                
                try:
                    new_doc.insert_pdf(self.doc, from_page=start, to_page=end)
                    clean_title = self.clean_filename(section['title'])
                    output_filename = f"{i:03d}_{clean_title}.pdf"
                    output_path = self.pdf_output_dir / output_filename
                    
                    new_doc.save(output_path)
                    logger.info(f"Created: {output_path}")
                    
                    created_files.append({
                        'path': str(output_path),
                        'title': section['title'],
                        'page': section['start_page'] + 1,
                        'index': i
                    })
                except Exception as e:
                    logger.error(f"Error processing section '{section['title']}': {str(e)}")
                finally:
                    new_doc.close()
            
            return created_files
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            return []
        finally:
            if hasattr(self, 'doc') and self.doc:
                self.doc.close()

class PdfToMarkdown:
    def __init__(self, output_dir: str):
        """Initialize the PDF to Markdown converter."""
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.md_output_dir = self.output_dir / "MD_Files"
        self.md_output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
            
        replacements = {
            '\xad': '',     # Soft hyphen
            '\u2022': '•',  # Bullet point
            '\u2013': '–',  # En dash
            '\u2014': '—',  # Em dash
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2018': "'",  # Left single quote
            '\u2019': "'"   # Right single quote
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'\s+', ' ', text)
        return re.sub(r'\n\s*\n', '\n\n', text).strip()
    
    def convert_pdf(self, pdf_path: Path) -> bool:
        """Convert a single PDF file to Markdown with robust error handling."""
        doc = None
        try:
            # Open with strict=False to handle some malformed PDFs
            doc = fitz.open(pdf_path)
            
            # Simple text extraction as fallback
            try:
                # First try fast text extraction
                text = ''
                for page in doc:
                    text += page.get_text("text") + "\n\n"
                
                # If we got some text, save it
                if text.strip():
                    output_path = self.md_output_dir / f"{pdf_path.stem}.md"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(f"---\ntitle: {pdf_path.stem}\nsource: {pdf_path.name}\n---\n\n{text}")
                    return True
                
            except Exception as e:
                logger.debug(f"Simple text extraction failed, falling back to block processing: {str(e)}")
            
            # If simple extraction failed, try block processing
            markdown_lines = [
                "---",
                f"title: {pdf_path.stem}",
                f"source: {pdf_path.name}",
                "---\n"
            ]
            
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    markdown_lines.append(f"\n---\n### Page {page_num + 1}\n---\n")
                    
                    # Extract text blocks with minimal processing
                    try:
                        text = page.get_text("text")
                        if text.strip():
                            markdown_lines.append(f"{text}\n\n")
                    except Exception as e:
                        logger.debug(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    
                except Exception as e:
                    logger.debug(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
            
            # Save the Markdown file
            if len(''.join(markdown_lines)) > 100:  # Only save if we have substantial content
                output_path = self.md_output_dir / f"{pdf_path.stem}.md"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(''.join(markdown_lines))
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error in convert_pdf for {pdf_path.name}: {str(e)}")
            return False
        finally:
            if doc:
                doc.close()

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the program header."""
    clear_screen()
    header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                            PDF-LLMizer v1.0                                  ║
║          Split PDFs by bookmarks and convert to LLM-friendly Markdown        ║
║                                                                              ║
║                          Ali Rajabpour Sanati                                ║
║                          https://Rajabpour.com                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(header)

def main():
    print_header()
    parser = argparse.ArgumentParser(description='Process PDF files by splitting them by bookmarks and converting to Markdown.')
    
    # Required arguments
    parser.add_argument('input_pdf', type=str, help='Path to the input PDF file')
    
    # Optional arguments
    parser.add_argument('-o', '--output', type=str, default='output',
                      help='Base output directory (default: ./output)')
    parser.add_argument('-l', '--level', type=int, default=1,
                      help='Bookmark level to split on (1=top level, 2=second level, etc.)')
    
    args = parser.parse_args()
    
    # Step 1: Split the PDF by bookmarks
    logger.info(f"Splitting {args.input_pdf} by level {args.level} bookmarks...")
    splitter = PdfSplitter(args.input_pdf, args.output, args.level)
    created_files = splitter.split_by_bookmarks()
    
    if not created_files:
        logger.error("No files were created. Exiting.")
        return 1
    
    # Step 2: Convert each split PDF to Markdown with progress bar
    logger.info("\nConverting split PDFs to Markdown...")
    converter = PdfToMarkdown(args.output)
    
    # Initialize progress tracking
    total_files = len(created_files)
    success_count = 0
    
    print("\n" + "="*50)
    print(f"Converting {total_files} PDF files to Markdown:")
    print("="*50)
    
    # Track start time
    import time
    start_time = time.time()
    
    for i, file_info in enumerate(created_files, 1):
        pdf_path = Path(file_info['path'])
        
        # Show progress
        progress = i / total_files * 100
        elapsed = time.time() - start_time
        avg_time = elapsed / i if i > 0 else 0
        remaining = avg_time * (total_files - i) if i > 0 else 0
        
        print(f"\r[{'#' * int(progress/2):<50}] {i}/{total_files} ({progress:.1f}%) | "
              f"Elapsed: {elapsed//60:.0f}m {elapsed%60:.0f}s | "
              f"ETA: {remaining//60:.0f}m {remaining%60:.0f}s | "
              f"Processing: {pdf_path.name[:30]}...", end="")
        
        try:
            if converter.convert_pdf(pdf_path):
                success_count += 1
        except Exception as e:
            logger.error(f"\nError processing {pdf_path.name}: {str(e)}")
    
    # Print final status
    print("\n\n" + "="*50)
    print(f"Conversion complete!")
    print(f"Successfully converted: {success_count}/{total_files} files")
    print(f"Total time: {time.time() - start_time:.1f} seconds")
    print("="*50)
    
    logger.info(f"Processing complete. Files saved to: {args.output}")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())