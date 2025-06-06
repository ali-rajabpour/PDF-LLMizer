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
python PDF-LLMizer.py input.pdf [options]
```

### Options:
- `-o, --output`: Output directory (default: `./output`)
- `-l, --level`: Bookmark level to split on (default: 1)

### Examples:

1. Basic usage:
   ```bash
   python PDF-LLMizer.py document.pdf
   ```

2. Specify output directory and bookmark level:
   ```bash
   python PDF-LLMizer.py document.pdf -o ./my_output -l 2
   ```

## Output Structure

The script creates two directories:
- `output/Split_PDFs/`: Contains PDFs split by bookmarks
- `output/MD_Files/`: Contains converted Markdown files

## Requirements

- Python 3.8+
- PyMuPDF (fitz)

## License

MIT

---

Created by [Ali Rajabpour Sanati](https://rajabpour.com)
