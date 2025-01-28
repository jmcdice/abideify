import contextlib
import io
import os
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import fitz
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

@dataclass
class ConversionPaths:
    """Data class to store paths used during conversion."""
    input_pdf: Path
    intermediate_md: Path
    output_simplified_md: Path

class PDFConverter:
    """
    A class to handle the conversion of PDF documents to simplified Markdown
    and additional local transformations (post-processing).
    """

    @staticmethod
    def create_paths(input_pdf: str, output_md: str) -> ConversionPaths:
        """
        Create and validate all necessary paths.
        """
        input_path = Path(input_pdf)
        output_path = Path(output_md)
        
        if not input_path.is_file():
            raise FileNotFoundError(f"Input PDF file does not exist: {input_pdf}")
            
        output_dir = output_path.parent
        base_name = output_path.stem
        intermediate_md = output_dir / f"{base_name}_original.md"
        
        return ConversionPaths(input_path, intermediate_md, output_path)

    def convert_pdf_to_markdown(self, paths: ConversionPaths) -> None:
        """
        Convert PDF to Markdown using DocumentConverter.
        """
        logger.info(f"Converting PDF to Markdown: {paths.input_pdf}")
        try:
            with ThreadPoolExecutor() as executor:
                with contextlib.redirect_stderr(io.StringIO()):
                    converter = DocumentConverter()
                    # Execute the conversion
                    result = converter.convert(str(paths.input_pdf))

            markdown_content = result.document.export_to_markdown()
            markdown_content = self._post_process_markdown(markdown_content)

            paths.intermediate_md.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Created intermediate Markdown: {paths.intermediate_md}")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise

    def _post_process_markdown(self, markdown_text: str) -> str:
        """
        Post-process the generated Markdown to ensure consistency and improve formatting.
        """
        # Example: Replace lines of === with # for headers
        markdown_text = re.sub(r'^(={3,})$', '#', markdown_text, flags=re.MULTILINE)
        return markdown_text

    def format_final_markdown(self, markdown_text: str) -> str:
        """
        Format the final Markdown content for consistency.
        """
        # Example: Replace multiple blank lines with a single blank line
        return re.sub(r'\n{3,}', '\n\n', markdown_text)

