# PDF-LLMizer

A powerful Python tool for splitting PDFs by bookmarks and converting them to Markdown format, optimized for LLM consumption.

## Features

- **PDF Processing Modes**: 
  - **Bookmarks**: Split PDFs by bookmark levels (original functionality)
  - **Whole**: Process entire PDFs without splitting (new!)
  - **Pages**: Split PDFs into individual pages (new!)
- **Flexible Output**: Choose between separate folders per PDF or combined output
- **Batch Processing**: Process single files or entire folders
- **Progress Tracking**: Real-time progress bar with ETA
- **Robust Processing**: Handles various PDF formats gracefully
- **Metadata Preservation**: Maintains document structure and formatting

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ali-rajabpour/PDF-LLMizer.git
   cd PDF-LLMizer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python PDF-LLMizer.py input_path [options]
```

### Arguments:
- `input_path`: Path to a single PDF file OR a folder containing PDF files

### Options:
- `-o, --output`: Output directory (default: `./output`)
- `-l, --level`: Bookmark level to split on (default: 1)
- `-m, --mode`: Processing mode: `bookmarks` (default), `whole`, or `pages`
- `--separate-folders`: Create separate folders for each PDF (default behavior)
- `--combined-folder`: Put all output in the same folder

### Examples:

1. Process a single PDF in default bookmarks mode:
   ```bash
   python PDF-LLMizer.py document.pdf
   ```

2. Process all PDFs in a folder without bookmarks (whole mode):
   ```bash
   python PDF-LLMizer.py ./my_pdfs_folder -m whole
   ```

3. Split PDFs into individual pages:
   ```bash
   python PDF-LLMizer.py document.pdf -m pages
   ```

4. Use combined folder structure:
   ```bash
   python PDF-LLMizer.py ./pdf_collection --combined-folder
   ```

5. Specify output directory and bookmark level:
   ```bash
   python PDF-LLMizer.py document.pdf -o ./my_output -l 2
   ```

## Output Structure

### Folder Structure Options:

**Separate Folders Mode** (default):
- Each PDF gets its own subfolder
- Organized by source document
- Example: `output/PDF_Name/Split_PDFs/`, `output/PDF_Name/MD_Files/`

**Combined Folder Mode**:
- All PDFs processed together in the same output directory
- Useful for batch processing into a single collection
- Example: `output/Split_PDFs/`, `output/MD_Files/`

### Processing Mode Output:

**Bookmarks Mode** (default):
- Creates `Split_PDFs/` and `MD_Files/` directories
- Each bookmark section becomes a separate file

**Whole Mode**:
- Processes entire PDF as single file
- Creates one output file per input PDF

**Pages Mode**:
- Splits PDF into individual pages
- Creates one file per page

### Single PDF Processing:
The script creates two directories in the specified output folder:
- `output/Split_PDFs/`: Contains PDFs split by bookmarks (or whole PDFs/pages)
- `output/MD_Files/`: Contains converted Markdown files

## Requirements

- Python 3.8+
- PyMuPDF (fitz)

## License

MIT

---

Created by [Ali Rajabpour Sanati](https://rajabpour.com)
