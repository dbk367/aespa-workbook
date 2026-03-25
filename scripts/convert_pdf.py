#!/usr/bin/env python3
"""
Convert DOCX to PDF.
Usage: python convert_pdf.py --input filename.docx --output filename.pdf
"""

import argparse
import subprocess
import os

def docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF using LibreOffice."""
    # Method 1: Using LibreOffice
    try:
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(pdf_path),
            docx_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # LibreOffice creates PDF with same name in output dir
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        temp_pdf = os.path.join(os.path.dirname(pdf_path), base_name + '.pdf')
        
        # Rename if needed
        if temp_pdf != pdf_path and os.path.exists(temp_pdf):
            os.rename(temp_pdf, pdf_path)
        
        print(f"✓ PDF saved: {pdf_path}")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Method 2: Using docx2pdf (if available)
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        print(f"✓ PDF saved: {pdf_path}")
        return True
    except ImportError:
        pass
    
    print("⚠ PDF conversion failed. Please install LibreOffice or docx2pdf.")
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert DOCX to PDF')
    parser.add_argument('--input', required=True, help='Input DOCX file')
    parser.add_argument('--output', required=True, help='Output PDF file')
    args = parser.parse_args()
    
    docx_to_pdf(args.input, args.output)
