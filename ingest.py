"""
ingest.py — Loads documents from data/raw/, chunks them, embeds each chunk
with a local MiniLM model (via ChromaDB's built-in ONNX embedding function,
so no separate PyTorch install is needed), and stores everything in a
persistent local ChromaDB collection.

Each source .txt file is expected to start with a small metadata header:

    SOURCE_TITLE: <title>
    SOURCE_URL: <url>
    CATEGORY: <category>

    <body text...>

Run:
    python ingest.py
"""

import os
import re
import glob
import chromadb
from chromadb.utils import embedding_functions

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma")
COLLECTION_NAME = "denhaag_municipality_docs"

CHUNK_SIZE = 900       # characters per chunk (roughly ~150-200 tokens)
CHUNK_OVERLAP = 150    # character overlap between consecutive chunks


def parse_document(path):
    """Split the header metadata from the body text."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    meta = {"source_title": "", "source_url": "", "category": ""}
    lines = raw.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(SOURCE_TITLE|SOURCE_URL|CATEGORY):\s*(.*)$", line.strip())
        if m:
            key, val = m.group(1).lower(), m.group(2).strip()
            meta[key] = val
            body_start = i + 1
        elif line.strip() == "" and body_start > 0:
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()
    return meta, body


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Simple sliding-window chunker that tries to break on paragraph/sentence
    boundaries where possible, so chunks stay readable and citable."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > chunk_size:
                # paragraph itself too long -> hard-split with overlap
                start = 0
                while start < len(para):
                    end = start + chunk_size
                    chunks.append(para[start:end])
                    start = end - overlap
                current = ""
            else:
                current = para
    if current:
        chunks.append(current)

    return chunks


def main():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.txt")))
    if not files:
        print(f"No .txt files found in {RAW_DIR}")
        return

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Fresh start each run so re-ingesting doesn't duplicate chunks
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    embedding_fn = embedding_functions.DefaultEmbeddingFunction()  # local MiniLM (ONNX)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    all_ids, all_docs, all_metas = [], [], []

    for path in files:
        meta, body = parse_document(path)
        if not body:
            print(f"  [skip] {os.path.basename(path)} has no body text")
            continue

        chunks = chunk_text(body)
        fname = os.path.basename(path)
        print(f"  {fname}: {len(chunks)} chunk(s) — {meta.get('source_title')}")

        for i, chunk in enumerate(chunks):
            all_ids.append(f"{fname}::chunk{i}")
            all_docs.append(chunk)
            all_metas.append({
                "source_title": meta.get("source_title", fname),
                "source_url": meta.get("source_url", ""),
                "category": meta.get("category", ""),
                "file": fname,
                "chunk_index": i,
            })

    collection.add(ids=all_ids, documents=all_docs, metadatas=all_metas)

    print(f"\nIngested {len(all_docs)} chunks from {len(files)} document(s) "
          f"into ChromaDB collection '{COLLECTION_NAME}' at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
