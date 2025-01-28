import asyncio
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import markdown
import markdownify
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .prompts import DEFAULT_PROMPT

logger = logging.getLogger(__name__)

class AIProcessor:
    """
    A class to handle splitting text into chunks and processing those chunks
    via the OpenAI API.
    """
    def __init__(
        self,
        max_chunk_size: int = 7000,
        concurrent_requests: int = 5,
        model_name: str = "gpt-4"
    ):
        self.max_chunk_size = max_chunk_size
        self.semaphore = asyncio.Semaphore(concurrent_requests)
        self.client: Optional[AsyncOpenAI] = None
        self.model_name = model_name

    async def initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self.client = AsyncOpenAI()
            logger.info("OpenAI client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks while preserving sentence boundaries.

        Args:
            text (str): The text to split.

        Returns:
            List[str]: A list of text chunks.
        """
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks: List[str] = []
        current_chunk = ""

        for sentence in sentences:
            # +1 for the space
            if len(current_chunk) + len(sentence) + 1 <= self.max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    async def process_chunk_with_ai(self, chunk: str) -> str:
        """
        Process a single chunk of text using OpenAI's API.

        Args:
            chunk (str): The text chunk to process.

        Returns:
            str: The simplified Markdown text.
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        prompt = f"{DEFAULT_PROMPT}{chunk}\n"
        
        try:
            async with self.semaphore:
                response: ChatCompletion = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.5,
                )
                simplified_text = response.choices[0].message.content
                return self._validate_markdown(simplified_text)
        except Exception as e:
            logger.error(f"AI processing failed for chunk: {e}")
            return ""

    def _validate_markdown(self, markdown_text: str) -> str:
        """
        Validate and optionally format the Markdown text.
        Returns validated and (optionally) corrected Markdown.
        """
        try:
            # Just parse to see if it's valid
            html = markdown.markdown(markdown_text)
            # If needed, we could re-convert to MD with markdownify here
            # markdown_text = markdownify.markdownify(html, heading_style="ATX")
        except Exception as e:
            logger.warning(f"Markdown validation failed: {e}")

        return markdown_text

