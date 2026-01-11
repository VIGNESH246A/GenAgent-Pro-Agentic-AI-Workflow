"""
File Reader Tool
Reads content from PDF, TXT, CSV, DOCX files
"""

import os
from pathlib import Path
from typing import Dict, Any
import PyPDF2
import pandas as pd
from docx import Document
from .base_tool import BaseTool
from loguru import logger


class FileReaderTool(BaseTool):
    """Read and extract content from various file formats"""
    
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            name="file_reader",
            description="Read content from PDF, TXT, CSV, DOCX, or XLSX files"
        )
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.supported_formats = ['.pdf', '.txt', '.csv', '.docx', '.xlsx']
    
    def execute(self, file_path: str) -> Dict[str, Any]:
        """
        Read file and extract content
        
        Args:
            file_path: Path to file to read
        
        Returns:
            Dict with file content and metadata
        """
        try:
            path = Path(file_path)
            
            # Validation
            if not path.exists():
                return self._error_response(f"File not found: {file_path}", "FileNotFoundError")
            
            if not path.is_file():
                return self._error_response(f"Path is not a file: {file_path}", "ValueError")
            
            file_size = path.stat().st_size
            if file_size > self.max_size_bytes:
                return self._error_response(
                    f"File too large: {file_size / 1024 / 1024:.2f}MB (max {self.max_size_bytes / 1024 / 1024}MB)",
                    "FileSizeError"
                )
            
            extension = path.suffix.lower()
            if extension not in self.supported_formats:
                return self._error_response(
                    f"Unsupported format: {extension}. Supported: {self.supported_formats}",
                    "FormatError"
                )
            
            logger.info(f"[FileReader] Reading {extension} file: {path.name}")
            
            # Read based on format
            if extension == '.pdf':
                content = self._read_pdf(path)
            elif extension == '.txt':
                content = self._read_txt(path)
            elif extension == '.csv':
                content = self._read_csv(path)
            elif extension == '.docx':
                content = self._read_docx(path)
            elif extension == '.xlsx':
                content = self._read_excel(path)
            else:
                return self._error_response(f"Handler not implemented for {extension}", "NotImplementedError")
            
            metadata = {
                "filename": path.name,
                "extension": extension,
                "size_bytes": file_size,
                "size_kb": round(file_size / 1024, 2),
                "lines": content.count('\n') + 1 if isinstance(content, str) else 0
            }
            
            logger.info(f"[FileReader] Successfully read {path.name} ({metadata['size_kb']}KB)")
            return self._success_response(result=content, metadata=metadata)
            
        except Exception as e:
            return self._error_response(f"Failed to read file: {str(e)}", "ReadError")
    
    def _read_pdf(self, path: Path) -> str:
        """Extract text from PDF"""
        text = []
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                text.append(f"--- Page {page_num + 1} ---\n{page.extract_text()}")
        return '\n\n'.join(text)
    
    def _read_txt(self, path: Path) -> str:
        """Read plain text file"""
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _read_csv(self, path: Path) -> str:
        """Read CSV and convert to formatted text"""
        df = pd.read_csv(path)
        return f"CSV Summary:\n{df.describe().to_string()}\n\nFirst 10 rows:\n{df.head(10).to_string()}"
    
    def _read_docx(self, path: Path) -> str:
        """Read DOCX file"""
        doc = Document(path)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    def _read_excel(self, path: Path) -> str:
        """Read Excel file"""
        xl = pd.ExcelFile(path)
        result = []
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            result.append(f"=== Sheet: {sheet_name} ===\n{df.to_string()}")
        return '\n\n'.join(result)