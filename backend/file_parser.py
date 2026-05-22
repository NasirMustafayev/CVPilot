"""
PDF and DOCX file parsing utilities.
Extracts text from various file formats.
"""

import io
import pdfplumber
from docx import Document
from typing import Optional


class FileParser:
    """Parse PDF and DOCX files and extract text."""

    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Extract text from PDF file."""
        text = []
        
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        
        return '\n'.join(text)

    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """Extract text from DOCX file."""
        text = []
        
        try:
            doc = Document(io.BytesIO(file_content))
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
        
        return '\n'.join(text)

    @staticmethod
    def parse_doc(file_content: bytes) -> str:
        """
        Extract text from DOC file.
        Note: Basic support - may not handle complex formatting.
        """
        try:
            import docx2txt
            text = docx2txt.process(io.BytesIO(file_content))
            return text
        except Exception:
            # Fallback: try basic parsing
            try:
                return file_content.decode('utf-8', errors='ignore')
            except Exception as e:
                raise ValueError(f"Failed to parse DOC: {str(e)}")

    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> str:
        """
        Parse file based on extension and return extracted text.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename with extension
        
        Returns:
            Extracted text from file
        
        Raises:
            ValueError: If file format is not supported or parsing fails
        """
        ext = filename.lower().split('.')[-1]
        
        if ext == 'pdf':
            return FileParser.parse_pdf(file_content)
        elif ext == 'docx':
            return FileParser.parse_docx(file_content)
        elif ext == 'doc':
            return FileParser.parse_doc(file_content)
        else:
            raise ValueError(f"Unsupported file format: .{ext}")
