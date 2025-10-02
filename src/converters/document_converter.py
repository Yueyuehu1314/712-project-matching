#!/usr/bin/env python3
"""
Document Converter Script
Converts documents in project/ and unit/ folders to Markdown format
and saves them to folders with _md suffix.

Supports:
- PDF files (using PyPDF2 for text extraction)
- Word documents (.docx) via pandoc
- PowerPoint presentations (.pptx) via pandoc
- Excel files (.xlsx) via pandoc
- Plain text files (.txt)

Requirements:
- pandoc installed on system
- Python packages: PyPDF2, python-docx, python-pptx, openpyxl
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import PyPDF2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentConverter:
    def __init__(self, base_dir=None):
        """Initialize the document converter."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.supported_extensions = {
            '.pdf': self._convert_pdf,
            '.docx': self._convert_docx,
            '.doc': self._convert_doc,
            '.pptx': self._convert_pptx,
            '.ppt': self._convert_ppt,
            '.xlsx': self._convert_xlsx,
            '.xls': self._convert_xls,
            '.txt': self._convert_txt,
            '.rtf': self._convert_rtf,
            '.odt': self._convert_odt,
            '.odp': self._convert_odp,
            '.ods': self._convert_ods
        }
    
    def _check_pandoc(self):
        """Check if pandoc is available."""
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Pandoc found: {result.stdout.split()[1]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Pandoc not found. Please install pandoc.")
            return False
    
    def _convert_pdf(self, input_file, output_file):
        """Convert PDF to Markdown using PyPDF2."""
        try:
            with open(input_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(f"## Page {page_num + 1}\n\n{text}\n\n")
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                
                markdown_content = ''.join(text_content)
                
                with open(output_file, 'w', encoding='utf-8') as md_file:
                    md_file.write(f"# {input_file.stem}\n\n")
                    md_file.write("*Converted from PDF using PyPDF2*\n\n")
                    md_file.write(markdown_content)
                
                logger.info(f"PDF converted: {input_file.name} -> {output_file.name}")
                return True
                
        except Exception as e:
            logger.error(f"Error converting PDF {input_file}: {e}")
            return False
    
    def _convert_with_pandoc(self, input_file, output_file, format_from=None):
        """Generic pandoc conversion."""
        try:
            cmd = ['pandoc', str(input_file), '-o', str(output_file)]
            if format_from:
                cmd.extend(['-f', format_from])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Pandoc converted: {input_file.name} -> {output_file.name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed for {input_file}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error converting {input_file}: {e}")
            return False
    
    def _convert_docx(self, input_file, output_file):
        """Convert Word document to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_doc(self, input_file, output_file):
        """Convert older Word document to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_pptx(self, input_file, output_file):
        """Convert PowerPoint presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_ppt(self, input_file, output_file):
        """Convert older PowerPoint presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_xlsx(self, input_file, output_file):
        """Convert Excel file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_xls(self, input_file, output_file):
        """Convert older Excel file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_txt(self, input_file, output_file):
        """Convert text file to Markdown."""
        try:
            with open(input_file, 'r', encoding='utf-8') as txt_file:
                content = txt_file.read()
            
            with open(output_file, 'w', encoding='utf-8') as md_file:
                md_file.write(f"# {input_file.stem}\n\n")
                md_file.write("```\n")
                md_file.write(content)
                md_file.write("\n```\n")
            
            logger.info(f"Text file converted: {input_file.name} -> {output_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting text file {input_file}: {e}")
            return False
    
    def _convert_rtf(self, input_file, output_file):
        """Convert RTF file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_odt(self, input_file, output_file):
        """Convert OpenDocument Text to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_odp(self, input_file, output_file):
        """Convert OpenDocument Presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_ods(self, input_file, output_file):
        """Convert OpenDocument Spreadsheet to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def convert_directory(self, input_dir):
        """Convert all supported documents in a directory."""
        input_path = self.base_dir / input_dir
        output_path = self.base_dir / f"{input_dir}_md"
        
        if not input_path.exists():
            logger.warning(f"Input directory {input_path} does not exist. Skipping.")
            return False
        
        # Create output directory
        output_path.mkdir(exist_ok=True)
        logger.info(f"Created output directory: {output_path}")
        
        converted_count = 0
        skipped_count = 0
        
        # Walk through all files in the input directory
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                
                if file_extension in self.supported_extensions:
                    # Create relative path structure in output directory
                    relative_path = file_path.relative_to(input_path)
                    output_file = output_path / relative_path.with_suffix('.md')
                    
                    # Create parent directories if needed
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Convert the file
                    converter_func = self.supported_extensions[file_extension]
                    if converter_func(file_path, output_file):
                        converted_count += 1
                    else:
                        skipped_count += 1
                else:
                    logger.info(f"Skipping unsupported file: {file_path.name}")
                    skipped_count += 1
        
        logger.info(f"Conversion complete for {input_dir}/: {converted_count} converted, {skipped_count} skipped")
        return True
    
    def convert_all(self, directories=None):
        """Convert all documents in specified directories."""
        if not self._check_pandoc():
            logger.error("Pandoc is required but not available. Exiting.")
            return False
        
        if directories is None:
            directories = ['project', 'unit']
        
        logger.info("Starting document conversion process...")
        
        for directory in directories:
            logger.info(f"Processing directory: {directory}")
            self.convert_directory(directory)
        
        logger.info("Document conversion process completed!")
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert documents to Markdown format')
    parser.add_argument('--dirs', nargs='+', default=['project', 'unit'],
                       help='Directories to process (default: project unit)')
    parser.add_argument('--base-dir', type=str, default=None,
                       help='Base directory path (default: current directory)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize converter
    converter = DocumentConverter(base_dir=args.base_dir)
    
    # Run conversion
    success = converter.convert_all(directories=args.dirs)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
