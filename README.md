# PDF-LLMizer

A powerful Python tool for splitting PDFs by bookmarks and converting them to Markdown format, optimized for LLM consumption.

## Features

- **PDF Splitting**: Split large PDFs by bookmark levels
- **Markdown Conversion**: Convert PDFs to clean, well-structured Markdown
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

### Examples:

1. Process a single PDF:
   ```bash
   python PDF-LLMizer.py document.pdf
   ```

2. Process all PDFs in a folder:
   ```bash
   python PDF-LLMizer.py ./my_pdfs_folder
   ```

3. Specify output directory and bookmark level:
   ```bash
   python PDF-LLMizer.py document.pdf -o ./my_output -l 2
   ```

4. Process folder with custom settings:
   ```bash
   python PDF-LLMizer.py ./pdf_collection -o ./results -l 1
   ```

## Output Structure

### Single PDF Processing:
The script creates two directories in the specified output folder:
- `output/Split_PDFs/`: Contains PDFs split by bookmarks
- `output/MD_Files/`: Contains converted Markdown files

### Folder Processing:
When processing a folder, the script creates a separate subfolder for each PDF:
- `output/PDF1_Name/Split_PDFs/`: Split PDFs from first PDF
- `output/PDF1_Name/MD_Files/`: Markdown files from first PDF
- `output/PDF2_Name/Split_PDFs/`: Split PDFs from second PDF
- `output/PDF2_Name/MD_Files/`: Markdown files from second PDF
- etc.

## Requirements

- Python 3.8+
- PyMuPDF (fitz)

## License

MIT

---

Created by [Ali Rajabpour Sanati](https://rajabpour.com)
