#!/usr/bin/env python3
"""
Advanced Document Converter with OCR Support
Converts documents in project/ and unit/ folders to Markdown format
with enhanced OCR capabilities for scanned PDFs.

Features:
- PyMuPDF for advanced PDF text extraction and OCR
- PaddleOCR for Chinese/English OCR
- Pandoc for standard document conversion
- Fallback mechanisms for robust conversion
- Apple Silicon optimized

Requirements:
- PyMuPDF for PDF processing
- PaddleOCR for OCR (optional)
- pandoc system command
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging
import json
from typing import Optional, Dict, Any
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    logger.info("PyMuPDF imported successfully")
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available - PDF OCR will be limited")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
    logger.info("PaddleOCR imported successfully")
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.warning("PaddleOCR not available - will use PyMuPDF OCR only")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")

class AdvancedDocumentConverter:
    def __init__(self, base_dir=None):
        """Initialize the advanced document converter."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.paddle_ocr = None
        self.supported_extensions = {
            '.pdf': self._convert_pdf_advanced,
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
        
        # Initialize PaddleOCR if available
        if PADDLEOCR_AVAILABLE:
            try:
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}")
                self.paddle_ocr = None
    
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
    
    def _extract_text_with_pymupdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF with OCR fallback."""
        if not PYMUPDF_AVAILABLE:
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # First try standard text extraction
                text = page.get_text()
                
                # If no text found or very little text, try OCR
                if len(text.strip()) < 50:
                    logger.info(f"Page {page_num + 1}: Using OCR (low text content)")
                    try:
                        # Get page as image
                        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                        pix = page.get_pixmap(matrix=mat)
                        img_data = pix.tobytes("png")
                        
                        # Use PaddleOCR if available
                        if self.paddle_ocr:
                            import io
                            from PIL import Image
                            img = Image.open(io.BytesIO(img_data))
                            ocr_result = self.paddle_ocr.ocr(img, cls=True)
                            
                            ocr_text = []
                            for line in ocr_result:
                                if line:
                                    for word_info in line:
                                        if len(word_info) >= 2:
                                            ocr_text.append(word_info[1][0])
                            text = '\n'.join(ocr_text)
                        else:
                            # Fallback to PyMuPDF's built-in OCR if available
                            try:
                                text = page.get_textpage_ocr().extractText()
                            except:
                                text = f"[OCR not available for page {page_num + 1}]"
                    
                    except Exception as e:
                        logger.warning(f"OCR failed for page {page_num + 1}: {e}")
                        text = f"[OCR failed for page {page_num + 1}]"
                
                if text.strip():
                    text_content.append(f"## Page {page_num + 1}\n\n{text}\n\n")
            
            doc.close()
            return ''.join(text_content)
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return ""
    
    def _extract_text_with_pypdf2(self, pdf_path: Path) -> str:
        """Fallback PDF text extraction using PyPDF2."""
        if not PYPDF2_AVAILABLE:
            return ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(f"## Page {page_num + 1}\n\n{text}\n\n")
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                
                return ''.join(text_content)
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def _convert_pdf_advanced(self, input_file: Path, output_file: Path) -> bool:
        """Advanced PDF conversion with OCR support."""
        try:
            logger.info(f"Converting PDF: {input_file.name}")
            
            # Try PyMuPDF first (best OCR support)
            text_content = ""
            if PYMUPDF_AVAILABLE:
                text_content = self._extract_text_with_pymupdf(input_file)
            
            # Fallback to PyPDF2 if PyMuPDF failed or unavailable
            if not text_content and PYPDF2_AVAILABLE:
                logger.info("Falling back to PyPDF2")
                text_content = self._extract_text_with_pypdf2(input_file)
            
            # If still no content, create placeholder
            if not text_content:
                text_content = "## Unable to extract text\n\nThis PDF may contain only images or require advanced OCR processing."
            
            # Write markdown file
            with open(output_file, 'w', encoding='utf-8') as md_file:
                md_file.write(f"# {input_file.stem}\n\n")
                md_file.write("*Converted from PDF with OCR support*\n\n")
                md_file.write(text_content)
            
            logger.info(f"PDF converted successfully: {input_file.name} -> {output_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting PDF {input_file}: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def _convert_with_pandoc(self, input_file: Path, output_file: Path, format_from: Optional[str] = None) -> bool:
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
    
    def _convert_docx(self, input_file: Path, output_file: Path) -> bool:
        """Convert Word document to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_doc(self, input_file: Path, output_file: Path) -> bool:
        """Convert older Word document to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_pptx(self, input_file: Path, output_file: Path) -> bool:
        """Convert PowerPoint presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_ppt(self, input_file: Path, output_file: Path) -> bool:
        """Convert older PowerPoint presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_xlsx(self, input_file: Path, output_file: Path) -> bool:
        """Convert Excel file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_xls(self, input_file: Path, output_file: Path) -> bool:
        """Convert older Excel file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_txt(self, input_file: Path, output_file: Path) -> bool:
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
    
    def _convert_rtf(self, input_file: Path, output_file: Path) -> bool:
        """Convert RTF file to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_odt(self, input_file: Path, output_file: Path) -> bool:
        """Convert OpenDocument Text to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_odp(self, input_file: Path, output_file: Path) -> bool:
        """Convert OpenDocument Presentation to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def _convert_ods(self, input_file: Path, output_file: Path) -> bool:
        """Convert OpenDocument Spreadsheet to Markdown."""
        return self._convert_with_pandoc(input_file, output_file)
    
    def convert_directory(self, input_dir: str) -> bool:
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
    
    def generate_summary_report(self, directories: list) -> Dict[str, Any]:
        """Generate a summary report of the conversion process."""
        report = {
            "conversion_timestamp": str(Path.cwd()),
            "directories_processed": directories,
            "system_info": {
                "pymupdf_available": PYMUPDF_AVAILABLE,
                "paddleocr_available": PADDLEOCR_AVAILABLE,
                "pypdf2_available": PYPDF2_AVAILABLE,
                "pandoc_available": self._check_pandoc()
            },
            "capabilities": {
                "pdf_ocr": PYMUPDF_AVAILABLE and self.paddle_ocr is not None,
                "standard_pdf": PYMUPDF_AVAILABLE or PYPDF2_AVAILABLE,
                "office_documents": self._check_pandoc()
            }
        }
        
        # Save report
        report_file = self.base_dir / "conversion_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversion report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report
    
    def convert_all(self, directories: Optional[list] = None) -> bool:
        """Convert all documents in specified directories."""
        if not self._check_pandoc():
            logger.error("Pandoc is required but not available. Exiting.")
            return False
        
        if directories is None:
            directories = ['project', 'unit']
        
        logger.info("Starting advanced document conversion with OCR support...")
        logger.info(f"PyMuPDF available: {PYMUPDF_AVAILABLE}")
        logger.info(f"PaddleOCR available: {PADDLEOCR_AVAILABLE}")
        logger.info(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
        
        success = True
        for directory in directories:
            logger.info(f"Processing directory: {directory}")
            if not self.convert_directory(directory):
                success = False
        
        # Generate summary report
        self.generate_summary_report(directories)
        
        logger.info("Advanced document conversion process completed!")
        return success

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Document Converter with OCR Support')
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
    converter = AdvancedDocumentConverter(base_dir=args.base_dir)
    
    # Run conversion
    success = converter.convert_all(directories=args.dirs)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
