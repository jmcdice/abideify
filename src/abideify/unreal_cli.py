import os
import click
from pydub import AudioSegment
from .tts_service import UnrealSpeechTTSService

def chunk_text(text, chunk_size=950):
    """
    Splits `text` into chunks of approx `chunk_size` characters
    (white-space aware). Adjust logic as needed.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for w in words:
        # +1 for space
        if current_length + len(w) + 1 > chunk_size:
            # finalize current chunk
            chunks.append(" ".join(current_chunk))
            current_chunk = [w]
            current_length = len(w)
        else:
            current_chunk.append(w)
            current_length += len(w) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

@click.command()
@click.argument('input_markdown_file')
@click.argument('output_audio_file')
@click.option('--api_key', envvar='UNREAL_SPEECH_API_KEY',
              help='Unreal Speech API key. If not provided, use $UNREAL_SPEECH_API_KEY.')
@click.option('--voice', default='Scarlett',
              help='Voice ID (Scarlett, Liv, Dan, Will, Amy). Default: Scarlett')
@click.option('--chunk_size', default=950, show_default=True,
              help='Approx. number of characters per chunk.')
@click.option('--tts_audio_dir', default='tts_audio', show_default=True,
              help='Directory for debugging chunk audio files.')
@click.option('--debug_mode', is_flag=True, default=False,
              help='If set, keep each chunk WAV file in tts_audio_dir with a timestamp.')
def main(input_markdown_file, output_audio_file, api_key, voice, chunk_size, tts_audio_dir, debug_mode):
    """
    1) Read the simplified Markdown file.
    2) Chunk the text.
    3) Synthesize each chunk via UnrealSpeechTTSService.
    4) Combine to single MP3.
    """

    if not api_key:
        raise click.ClickException("No API key provided or found in UNREAL_SPEECH_API_KEY.")

    # Read your simplified text
    with open(input_markdown_file, 'r', encoding='utf-8') as f:
        text_data = f.read()

    # Split into manageable chunks
    chunks = chunk_text(text_data, chunk_size=chunk_size)
    click.echo(f"Chunked text into {len(chunks)} parts.")

    # Initialize the UnrealSpeechTTSService
    tts_service = UnrealSpeechTTSService(api_key=api_key, tts_audio_dir=tts_audio_dir)

    # We'll merge all chunks into this final AudioSegment
    final_audio = AudioSegment.silent(duration=0)

    for i, chunk in enumerate(chunks, start=1):
        click.echo(f"Synthesizing chunk {i}/{len(chunks)}...")

        # This returns a .wav file path or None if error
        chunk_wav = tts_service.synthesize_text(chunk, voice=voice, debug_mode=debug_mode)
        if not chunk_wav:
            click.echo(f"Error synthesizing chunk {i}. Skipping.")
            continue

        # Load the WAV chunk
        chunk_audio_segment = AudioSegment.from_wav(chunk_wav)

        # Append to final
        final_audio += chunk_audio_segment

        # If not in debug mode, clean up chunk file
        if not debug_mode:
            os.remove(chunk_wav)

    # Export combined audio to MP3
    final_audio.export(output_audio_file, format="mp3")
    click.echo(f"All chunks combined into {output_audio_file}")

if __name__ == "__main__":
    main()

