# prompts.py

DEFAULT_PROMPT = """\
Your task is to translate this technical document into approachable language.
Convert the following text to simpler language in a conversational tone.
Replace technical or complex terms with simpler alternatives (add brief parenthetical explanations if needed).

Please do the following:
1. Remove all authors, human names, figure or table references (e.g. "Figure 1", "Table of Contents"), headings, section numbers, and table-of-contents lists.
2. Do not include any markdown or formatting symbols (no hashes, asterisks, etc.).
3. Return only plain text, nothing else.
4. Do not summarize or reference the text; just convert it directly to simpler language while preserving as much original context as possible.
5. Make the text suitable for a podcast, so it should read naturally aloud, return only readable paragraphs that can be read aloud in a human voice.

Text:
"""

DEFAULT_PROMPT_1 = """\
Your task is to translate this technical document to approachable language.
Convert the following text to simpler language, preserving its original structure.
Replace technical or complex terms with simpler alternatives, adding brief
parenthetical explanations for medical/technical terms when needed. Maintain
the same flow and format as the original text, but make it easier to understand.
This will be read aloud so remove the authors and just ignore tables. Don't
summarize or reference the text—just convert it directly to simpler language.
Return only the formatted markdown, nothing else.

Text:
"""

