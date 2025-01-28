# Abideify

> Take 'er easy with your PDFs man - convert, simplify, and listen to your documents

Abideify is a powerful document processing pipeline that transforms complex PDF documents into simplified Markdown text and optional podcast-style audio. Named after The Dude, Abideify helps you process and consume content with minimal hassle.

## Key Features

- **PDF to Markdown Conversion**: Seamlessly transform PDF documents into clean Markdown using `docling`
- **AI-Powered Text Simplification**: Leverage OpenAI models to make complex content more accessible
- **Text-to-Speech Generation**: Create professional audio versions using Unreal Speech (it's cheap)
- **Smart Document Processing**: Automatically handle large documents through intelligent chunking and merging

## Prerequisites

- Python 3.11 (only use 3.11, not 3.13)
- FFmpeg installation (brew install ffmpeg)
- OpenAI API key (for text simplification)
- Unreal Speech API key (optional, for text-to-speech)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jmcdice/abideify.git
   cd abideify
   ```

2. Set up a Python virtual environment (only use python 3.11!):
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate 
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Configure API keys:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export UNREAL_SPEECH_API_KEY="your-unrealspeech-key"
   ```

## Quick Start

Convert a PDF with default settings:

```bash
python -m abideify.cli your_document.pdf
```

Full example with all features enabled:

```bash
python -m abideify.cli pdf/DeepSeek_R1.pdf \
    --model gpt-3.5-turbo \
    --max_chunk_size 6000 \
    --tts \
    --voice Scarlett
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_pdf` | Path to input PDF file | Required |
| `output_md` | Output Markdown file path | `outputs/<pdf_name>/simplified.md` |
| `--model` | OpenAI model (gpt-3.5-turbo/gpt-4) | `gpt-3.5-turbo` |
| `--max_chunk_size` | AI processing chunk size | 6000 |
| `--tts` | Enable text-to-speech | False |
| `--voice` | TTS voice (Scarlett/Liv/Dan/Will/Amy) | Scarlett |
| `--tts_chunk_size` | TTS processing chunk size | 1000 |
| `--debug_mode` | Keep intermediate files | False |

## Output Files

Processing generates the following files in `outputs/<pdf_name>/`:

- `original.md`: Initial Markdown conversion
- `simplified.md`: AI-simplified version
- `simplified.mp3`: Audio version (if TTS enabled)

## Project Structure

```
abideify/
├── src/abideify/
│   ├── ai_processor.py    # AI simplification logic
│   ├── converter.py       # PDF conversion
│   ├── cli.py            # Command line interface
│   ├── tts_service.py    # Text-to-speech service
│   └── prompts.py        # AI system prompts
├── pdf/                   # Sample PDFs
└── outputs/              # Generated files
```

## Advanced Usage

### Handling Large Documents

Abideify automatically manages large documents by:

1. Splitting content into processable chunks
2. Processing each chunk independently
3. Intelligently merging results

Adjust chunk sizes with:
- `--max_chunk_size`: For AI processing (default: 6000)
- `--tts_chunk_size`: For TTS generation (max: 1000)

### Concurrent Processing

Control parallel processing with:
```bash
python -m abideify.cli input.pdf --concurrent_requests 5
```

## Troubleshooting

Common issues and solutions:

1. **Missing API Keys**
   - Error: "OpenAI API key not found"
   - Solution: Set `OPENAI_API_KEY` environment variable

2. **FFmpeg Not Found**
   - Error: "FFmpeg command not found"
   - Solution: Install FFmpeg using your system's package manager

3. **TTS Chunk Size Too Large**
   - Error: "Chunk size exceeds UnrealSpeech limit"
   - Solution: Keep `--tts_chunk_size` ≤ 1000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork
5. Submit a pull request

We welcome contributions! Please include:
- Clear commit messages
- Updated documentation

## License

MIT License - See [LICENSE](LICENSE) file for details

---

> The Dude abides, and so do your PDFs. Take it easy out there, man.
