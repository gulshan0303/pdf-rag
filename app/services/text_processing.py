import re


def normalize_line(line: str) -> str:
    """Normalize whitespace for comparison."""
    return re.sub(r"\s+", " ", line).strip()


def clean_text(text: str) -> str:
    """Clean common PDF extraction noise."""
    text = text.replace("\u00a0", " ")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()

def is_heading(text: str) -> bool:
    text = text.strip()

    if not text:
        return False

    # Numbered heading
    if re.match(r"^\d+\.\s+[A-Za-z].{1,100}$", text):
        return True

    # Known document-style heading
    if text.endswith(":") and len(text) <= 80:
        return True

    return False

def split_sentences(text: str) -> list[str]:
    """Basic sentence splitter."""
    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def split_long_text(
    text: str,
    max_length: int,
) -> list[str]:

    if len(text) <= max_length:
        return [text]

    sentences = split_sentences(text)

    if len(sentences) == 1:
        return [
            text[i:i + max_length]
            for i in range(0, len(text), max_length)
        ]

    chunks = []
    current = ""

    for sentence in sentences:

        if len(current) + len(sentence) + 1 <= max_length:
            current += (
                (" " if current else "")
                + sentence
            )
        else:
            if current:
                chunks.append(current)

            current = sentence

    if current:
        chunks.append(current)

    return chunks


def build_units(text: str) -> list[str]:
    """
    Convert page text into meaningful units.

    A heading is attached to the following paragraph/content.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    units = []

    i = 0

    while i < len(paragraphs):

        current = paragraphs[i]

        if is_heading(current) and i + 1 < len(paragraphs):
            next_paragraph = paragraphs[i + 1]

            units.append(
                f"{current}\n{next_paragraph}"
            )

            i += 2
            continue

        units.append(current)

        i += 1

    return units


def get_sentence_overlap(
    text: str,
    overlap_size: int,
) -> str:
    """
    Return overlap using complete sentences,
    never arbitrary characters.
    """

    sentences = split_sentences(text)

    if not sentences:
        return ""

    overlap = []

    total_length = 0

    for sentence in reversed(sentences):

        if total_length + len(sentence) > overlap_size:
            break

        overlap.insert(0, sentence)
        total_length += len(sentence)

    return " ".join(overlap)

def split_into_sections(text: str) -> list[dict]:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = []

    current_heading = None
    current_lines = []

    for line in lines:

        if is_heading(line):

            if current_lines:
                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_lines),
                })

            current_heading = line
            current_lines = []

        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_lines),
        })

    return sections

def chunk_page(
    text: str,
    page_number: int,
    chunk_size: int = 1500,
    overlap: int = 200,
) -> list[dict]:

    text = clean_text(text)

    if not text:
        return []

    units = build_units(text)

    final_units = []

    for unit in units:

        if len(unit) <= chunk_size:
            final_units.append(unit)
        else:
            final_units.extend(
                split_long_text(
                    unit,
                    chunk_size,
                )
            )

    chunks = []
    current = ""

    for unit in final_units:

        proposed_length = (
            len(current)
            + len(unit)
            + 2
        )

        if proposed_length <= chunk_size:

            current += (
                ("\n\n" if current else "")
                + unit
            )

            continue

        if current:
            chunks.append(current)

        overlap_text = get_sentence_overlap(
            current,
            overlap,
        )

        current = (
            overlap_text
            + ("\n\n" if overlap_text else "")
            + unit
        )

    if current:
        chunks.append(current)

    return [
        {
            "content": chunk,
            "page_number": page_number,
        }
        for chunk in chunks
    ]


def remove_repeated_lines(
    pages: list[str],
    min_occurrences: int = 2,
) -> list[str]:

    line_counts = {}

    for page in pages:

        seen_on_page = set()

        for line in page.splitlines():

            normalized = normalize_line(line)

            if not normalized:
                continue

            if normalized in seen_on_page:
                continue

            seen_on_page.add(normalized)

            line_counts[normalized] = (
                line_counts.get(normalized, 0) + 1
            )

    repeated_lines = {
        line
        for line, count in line_counts.items()
        if count >= min_occurrences
    }

    cleaned_pages = []

    for page in pages:

        cleaned_lines = []

        for line in page.splitlines():

            normalized = normalize_line(line)

            if normalized in repeated_lines:
                continue

            cleaned_lines.append(line)

        cleaned_pages.append(
            "\n".join(cleaned_lines)
        )

    return cleaned_pages    

def chunk_section(
    heading: str | None,
    content: str,
    page_number: int,
    chunk_size: int = 1500,
) -> list[dict]:

    prefix = f"{heading}\n" if heading else ""

    text = clean_text(content)

    sentences = split_sentences(text)

    chunks = []
    current = prefix

    for sentence in sentences:

        proposed = (
            current
            + (" " if current else "")
            + sentence
        )

        if len(proposed) <= chunk_size:
            current = proposed

        else:
            if current.strip():
                chunks.append(current.strip())

            current = (
                f"{heading}\n"
                if heading
                else ""
            )

            current += sentence

    if current.strip():
        chunks.append(current.strip())

    return [
        {
            "content": chunk,
            "page_number": page_number,
            "section": heading,
        }
        for chunk in chunks
    ]    