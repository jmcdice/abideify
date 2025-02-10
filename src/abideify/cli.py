# cli.py
import argparse
import asyncio
import logging
import os
import sys
import re
from pathlib import Path

from pydub import AudioSegment

from .converter import PDFConverter, ConversionPaths
from .ai_processor import AIProcessor
from .tts_service import UnrealSpeechTTSService

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """
    Lowercases, removes .pdf, .md, or .markdown extension, and replaces non-alphanumeric
    characters with underscores.
    """
    name = filename.lower()
    name = re.sub(r'\.(pdf|md|markdown)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^a-z0-9]+', '_', name)
    return name.strip('_')

async def main_async(args) -> None:
    input_path = Path(args.input_file)
    safe_name = sanitize_filename(input_path.name)
    outdir = Path("outputs") / safe_name
    outdir.mkdir(parents=True, exist_ok=True)

    # Set default output paths
    final_md = outdir / "simplified.md"
    final_mp3 = outdir / "simplified.mp3"
    if args.output_md:
        final_md = Path(args.output_md)
    if args.output_mp3:
        final_mp3 = Path(args.output_mp3)

    converter = PDFConverter()
    if input_path.suffix.lower() == ".pdf":
        # PDF input: convert PDF to Markdown.
        intermediate_md = outdir / "original.md"
        paths = ConversionPaths(
            input_pdf=input_path,
            intermediate_md=intermediate_md,
            output_simplified_md=final_md,
        )
        converter.convert_pdf_to_markdown(paths)
    elif input_path.suffix.lower() in [".md", ".markdown"]:
        # Markdown input: use it as-is.
        intermediate_md = input_path
    else:
        logger.error("Unsupported file type. Please provide a PDF or Markdown file.")
        sys.exit(1)

    # Simplify using AI.
    ai = AIProcessor(
        max_chunk_size=args.max_chunk_size,
        concurrent_requests=args.concurrent_requests,
        model_name=args.model
    )
    await ai.initialize_client()

    text = intermediate_md.read_text(encoding="utf-8")
    if not text.strip():
        logger.error("No text was extracted from the Markdown.")
        sys.exit(1)

    chunks = ai.split_text_into_chunks(text)
    logger.info(f"Processing {len(chunks)} chunks...")

    tasks = [ai.process_chunk_with_ai(chunk) for chunk in chunks]
    simplified_list = await asyncio.gather(*tasks)
    simplified_content = "\n\n".join(filter(None, simplified_list))
    simplified_content = converter.format_final_markdown(simplified_content)

    # Write final simplified Markdown.
    final_md.write_text(simplified_content, encoding="utf-8")
    logger.info(f"Simplified Markdown saved to: {final_md}")

    # Optional TTS synthesis.
    if args.tts:
        logger.info("Starting TTS synthesis...")
        api_key = args.api_key or os.environ.get("UNREAL_SPEECH_API_KEY")
        if not api_key:
            logger.error("No UnrealSpeech API key found; set --api_key or UNREAL_SPEECH_API_KEY.")
            sys.exit(1)

        from .unreal_cli import chunk_text  # reuse chunking logic
        text_chunks = chunk_text(simplified_content, chunk_size=args.tts_chunk_size)
        logger.info(f"Chunked text into {len(text_chunks)} parts for TTS.")

        tts_service = UnrealSpeechTTSService(
            api_key=api_key,
            tts_audio_dir=args.tts_audio_dir
        )

        final_audio = AudioSegment.silent(duration=0)

        for i, chunk in enumerate(text_chunks, start=1):
            logger.info(f"Synthesizing chunk {i}/{len(text_chunks)}...")
            chunk_wav = tts_service.synthesize_text(chunk, voice=args.voice, debug_mode=args.debug_mode)
            if not chunk_wav:
                logger.error(f"Error synthesizing chunk {i}. Skipping.")
                continue

            segment = AudioSegment.from_wav(chunk_wav)
            final_audio += segment

            if not args.debug_mode:
                os.remove(chunk_wav)

        final_audio.export(final_mp3, format="mp3")
        logger.info(f"TTS completed! Combined MP3 saved to {final_mp3}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF or Markdown to simplified Markdown with optional TTS."
    )
    parser.add_argument("input_file", help="Path to the input PDF or Markdown file")
    parser.add_argument("--output_md", default=None, help="Override default final .md path")
    parser.add_argument("--max_chunk_size", type=int, default=7000,
                        help="Max chunk size in characters for AI simplification.")
    parser.add_argument("--concurrent_requests", type=int, default=5,
                        help="Number of concurrent OpenAI requests.")
    parser.add_argument("--model", type=str, default="gpt-4",
                        help="OpenAI model name (e.g. gpt-3.5-turbo or gpt-4).")

    # TTS options.
    parser.add_argument("--tts", action="store_true",
                        help="Enable text-to-speech after simplification.")
    parser.add_argument("--api_key", default=None,
                        help="UnrealSpeech API key (or set UNREAL_SPEECH_API_KEY).")
    parser.add_argument("--voice", type=str, default="Scarlett",
                        help="Voice ID (Scarlett, Liv, Dan, Will, Amy).")
    parser.add_argument("--tts_chunk_size", type=int, default=950,
                        help="Chunk size in characters for TTS calls.")
    parser.add_argument("--output_mp3", default=None,
                        help="Override final MP3 file path.")
    parser.add_argument("--tts_audio_dir", default="tts_audio",
                        help="Directory to save chunk WAV files if debug.")
    parser.add_argument("--debug_mode", action="store_true", default=False,
                        help="Keep chunk WAV files in tts_audio_dir with timestamps.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        asyncio.run(main_async(args))
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()


