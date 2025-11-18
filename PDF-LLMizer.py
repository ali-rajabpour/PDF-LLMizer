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
from typing import List, Dict, Tuple
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
    
    def process_whole_pdf(self) -> List[Dict]:
        """Process the entire PDF as a single file (no splitting)."""
        try:
            self.doc = fitz.open(self.pdf_path)
            filename = self.pdf_path.stem
            
            output_filename = f"{self.clean_filename(filename)}.pdf"
            output_path = self.pdf_output_dir / output_filename
            
            # Save the entire PDF
            self.doc.save(output_path)
            logger.info(f"Created: {output_path}")
            
            return [{
                'path': str(output_path),
                'title': filename,
                'page': 1,
                'index': 1
            }]
            
        except Exception as e:
            logger.error(f"Error processing whole PDF: {str(e)}")
            return []
        finally:
            if hasattr(self, 'doc') and self.doc:
                self.doc.close()
    
    def split_by_page_ranges(self, page_ranges: List[Tuple[int, int, str]]) -> List[Dict]:
        """Split PDF by custom page ranges."""
        try:
            self.doc = fitz.open(self.pdf_path)
            created_files = []
            
            for i, (start_page, end_page, title) in enumerate(page_ranges, 1):
                new_doc = fitz.open()
                
                try:
                    # Adjust for 0-based indexing
                    start = max(0, start_page - 1)
                    end = min(end_page - 1, len(self.doc) - 1)
                    
                    new_doc.insert_pdf(self.doc, from_page=start, to_page=end)
                    clean_title = self.clean_filename(title)
                    output_filename = f"{i:03d}_{clean_title}.pdf"
                    output_path = self.pdf_output_dir / output_filename
                    
                    new_doc.save(output_path)
                    logger.info(f"Created: {output_path}")
                    
                    created_files.append({
                        'path': str(output_path),
                        'title': title,
                        'page': start_page,
                        'index': i
                    })
                except Exception as e:
                    logger.error(f"Error processing page range '{title}': {str(e)}")
                finally:
                    new_doc.close()
            
            return created_files
            
        except Exception as e:
            logger.error(f"Error splitting PDF by page ranges: {str(e)}")
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

def process_single_pdf(pdf_path: str, output_dir: str, level: int, mode: str = 'bookmarks', separate_folders: bool = True) -> List[Dict]:
    """Process a single PDF file."""
    logger.info(f"Processing {pdf_path} in {mode} mode...")
    
    # Determine the actual output directory based on separate_folders setting
    if separate_folders:
        pdf_name = Path(pdf_path).stem
        actual_output_dir = Path(output_dir) / pdf_name
    else:
        actual_output_dir = output_dir
    
    splitter = PdfSplitter(pdf_path, str(actual_output_dir), level)
    
    if mode == 'bookmarks':
        # Try bookmarks first
        result = splitter.split_by_bookmarks()
        if result:
            return result
        else:
            # Fallback to whole PDF if no bookmarks found
            logger.warning("No bookmarks found, falling back to whole PDF processing")
            return splitter.process_whole_pdf()
    elif mode == 'whole':
        return splitter.process_whole_pdf()
    elif mode == 'pages':
        # For now, split into individual pages
        doc = fitz.open(pdf_path)
        page_ranges = [(i+1, i+1, f"page_{i+1}") for i in range(len(doc))]
        doc.close()
        return splitter.split_by_page_ranges(page_ranges)
    else:
        logger.error(f"Unknown processing mode: {mode}")
        return []

def process_folder(folder_path: str, output_dir: str, level: int, mode: str = 'bookmarks', separate_folders: bool = True) -> List[Dict]:
    """Process all PDF files in a folder."""
    folder = Path(folder_path).expanduser().resolve()
    pdf_files = list(folder.glob("*.pdf")) + list(folder.glob("*.PDF"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in folder: {folder_path}")
        return []
    
    logger.info(f"Found {len(pdf_files)} PDF files in folder: {folder_path}")
    all_created_files = []
    
    for pdf_file in pdf_files:
        logger.info(f"\nProcessing: {pdf_file.name}")
        # Process each PDF with the specified mode and folder structure
        created_files = process_single_pdf(str(pdf_file), output_dir, level, mode, separate_folders)
        all_created_files.extend(created_files)
    
    return all_created_files

def convert_files_to_markdown(created_files: List[Dict], output_dir: str) -> int:
    """Convert created PDF files to Markdown format."""
    if not created_files:
        logger.error("No files were created. Skipping conversion.")
        return 0
    
    logger.info("\nConverting split PDFs to Markdown...")
    converter = PdfToMarkdown(output_dir)
    
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
    
    return success_count

def main():
    print_header()
    parser = argparse.ArgumentParser(description='Process PDF files by splitting them by bookmarks and converting to Markdown.')
    
    # Required arguments - now accepts file or folder
    parser.add_argument('input_path', type=str, help='Path to the input PDF file or folder containing PDFs')
    
    # Optional arguments
    parser.add_argument('-o', '--output', type=str, default='output',
                      help='Base output directory (default: ./output)')
    parser.add_argument('-l', '--level', type=int, default=1,
                      help='Bookmark level to split on (1=top level, 2=second level, etc.)')
    parser.add_argument('-m', '--mode', type=str, default='bookmarks', choices=['bookmarks', 'whole', 'pages'],
                      help='Processing mode: bookmarks (split by bookmarks), whole (process entire PDF), pages (split into individual pages) (default: bookmarks)')
    parser.add_argument('--separate-folders', action='store_true', default=True,
                      help='Create separate folders for each PDF (default: True)')
    parser.add_argument('--combined-folder', action='store_true', default=False,
                      help='Put all output in the same folder (overrides --separate-folders)')
    
    args = parser.parse_args()
    
    # Determine folder structure preference
    separate_folders = not args.combined_folder  # If combined-folder is True, separate_folders should be False
    
    # Determine if input is a file or folder
    input_path = Path(args.input_path).expanduser().resolve()
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {args.input_path}")
        return 1
    
    # Process based on input type
    if input_path.is_file():
        # Single PDF file
        if not input_path.suffix.lower() == '.pdf':
            logger.error(f"Input file is not a PDF: {args.input_path}")
            return 1
        
        created_files = process_single_pdf(str(input_path), args.output, args.level, args.mode, separate_folders)
        
        if not created_files:
            logger.error("No files were created. Exiting.")
            return 1
        
        convert_files_to_markdown(created_files, args.output)
        
    elif input_path.is_dir():
        # Folder containing PDFs
        created_files = process_folder(str(input_path), args.output, args.level, args.mode, separate_folders)
        
        if not created_files:
            logger.error("No files were created. Exiting.")
            return 1
        
        convert_files_to_markdown(created_files, args.output)
        
    else:
        logger.error(f"Input path is neither a file nor a directory: {args.input_path}")
        return 1
    
    logger.info(f"Processing complete. Files saved to: {args.output}")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())