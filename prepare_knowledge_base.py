"""
prepare_knowledge_base.py

Loads all documents from DATA_DIR and generates knowledge_base.json
with smart chunking:

  - Markdown files (.md): split on '---' story separators first,
    keeping each story/section as one self-contained chunk.
    Falls back to RecursiveCharacterTextSplitter only for sections
    that exceed MAX_CHUNK_CHARS.

  - PDF files (.pdf): standard RecursiveCharacterTextSplitter
    with larger chunk_size suited for narrative text.

  - DOCX files (.docx): skipped — replaced by the cleaned
    Markdown equivalents in this directory.

Run this script once before running build_db.py or re-indexing.
Output: knowledge_base.json
"""

import json, os, re, sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR   = "data - copia"
OUTPUT     = "knowledge_base.json"
MAX_CHUNK  = 1800   # chars — stories over this get split further
PDF_CHUNK  = 1200   # chars — chunk size for PDF pages
OVERLAP    = 150    # overlap between consecutive PDF chunks

# Personal contact details to strip from CV chunks before indexing
_PERSONAL_PATTERNS = [
    re.compile(r'\+34[\s\d\-]{8,}'),                  # Spanish phone numbers
    re.compile(r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b'),  # generic phone
    re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}'),  # email
    re.compile(r'Madrid,\s*Spain\s*\|?'),            # home city line
]

def _strip_personal_info(text: str) -> str:
    for pattern in _PERSONAL_PATTERNS:
        text = pattern.sub('', text)
    text = re.sub(r'\|\s*\|', '|', text)   # clean up orphaned pipes
    text = re.sub(r'^\s*\|\s*', '', text, flags=re.MULTILINE)
    return text.strip()

# ---------------------------------------------------------------------------
# Markdown loader — story-level splitting on "---" separators
# ---------------------------------------------------------------------------

def _extract_metadata_from_section(text: str, filepath: str) -> dict:
    """Pull structured fields out of a story header line if present."""
    title_m   = re.search(r'^## (.+)$', text, re.MULTILINE)
    company_m = re.search(r'\*\*Company:\*\*\s*([^|]+)', text)
    skills_m  = re.search(r'\*\*Skills:\*\*\s*(.+)$', text, re.MULTILINE)
    year_m    = re.search(r'\*\*Year:\*\*\s*([^|]+)', text)

    return {
        "source":        filepath,
        "document_type": "professional_story" if title_m else "summary",
        "title":         title_m.group(1).strip()   if title_m   else os.path.basename(filepath),
        "company":       company_m.group(1).strip() if company_m else "",
        "skills":        skills_m.group(1).strip()  if skills_m  else "",
        "year":          year_m.group(1).strip()    if year_m    else "",
    }


def _section_chunks(text: str, metadata: dict) -> list[dict]:
    """Return one chunk per section; sub-split if section exceeds MAX_CHUNK."""
    if len(text) <= MAX_CHUNK:
        return [{"text": text, "metadata": metadata}]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK,
        chunk_overlap=OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    pieces = splitter.split_text(text)
    return [{"text": p.strip(), "metadata": metadata} for p in pieces if p.strip()]


def load_markdown(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Primary split: story/section separators (horizontal rules)
    raw_sections = re.split(r'\n---\n', content)

    # Secondary fallback: split long files that use ## headers but no --- rules
    if len(raw_sections) == 1 and len(content) > MAX_CHUNK:
        raw_sections = re.split(r'\n(?=## )', content)

    chunks = []
    for section in raw_sections:
        section = section.strip()
        if len(section) < 80:           # skip title page / empty separators
            continue
        meta = _extract_metadata_from_section(section, filepath)
        chunks.extend(_section_chunks(section, meta))

    return chunks


# ---------------------------------------------------------------------------
# PDF loader
# ---------------------------------------------------------------------------

def load_pdf(filepath: str) -> list[dict]:
    loader   = PyPDFLoader(filepath)
    pages    = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=PDF_CHUNK,
        chunk_overlap=OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    raw_chunks = splitter.split_documents(pages)
    result = []
    for c in raw_chunks:
        text = _strip_personal_info(c.page_content.strip())
        if not text:
            continue
        meta = {k: v for k, v in c.metadata.items()}
        meta["document_type"] = "cv_or_thesis"
        result.append({"text": text, "metadata": meta})
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    all_chunks = []
    skipped    = []

    for filename in sorted(os.listdir(DATA_DIR)):
        filepath = os.path.join(DATA_DIR, filename)

        if filename.endswith(".md"):
            chunks = load_markdown(filepath)
            print(f"  [MD]   {filename[:60]:60s}  -> {len(chunks):3d} chunks")
            all_chunks.extend(chunks)

        elif filename.endswith(".pdf"):
            chunks = load_pdf(filepath)
            print(f"  [PDF]  {filename[:60]:60s}  -> {len(chunks):3d} chunks")
            all_chunks.extend(chunks)

        elif filename.endswith(".docx"):
            print(f"  [SKIP] {filename[:60]:60s}  (replaced by cleaned .md)")
            skipped.append(filename)

        else:
            print(f"  [SKIP] {filename[:60]:60s}  (unsupported format)")

    print(f"\nTotal chunks: {len(all_chunks)}")
    if skipped:
        print(f"Skipped DOCX files: {skipped}")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=1)
    print(f"Saved -> {OUTPUT}")


if __name__ == "__main__":
    main()
