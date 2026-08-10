"""
rag.py — Core retrieval-augmented generation logic for the AI Municipality
Assistant (Den Haag).

Pipeline:
    question -> embed -> ChromaDB top-k similarity search
             -> confidence check on the best match
             -> if confident: build a strictly-grounded prompt with the
                retrieved chunks and call the LLM (Groq)
             -> if not confident: decline and point to denhaag.nl directly
             -> always return the answer plus the exact source chunks used

This module has no UI code — app.py (Streamlit) imports it.
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma")
COLLECTION_NAME = "denhaag_municipality_docs"

TOP_K = 4

# Cosine DISTANCE from Chroma (0 = identical, 2 = opposite). Below this
# threshold on the best-matching chunk, we trust the retrieval enough to
# let the LLM attempt an answer. This is a simple, uncalibrated heuristic —
# see README "Limitations" for why that matters.
DISTANCE_THRESHOLD = 0.75

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are the AI Municipality Assistant for the city of Den Haag (The Hague).

STRICT RULES — follow these exactly:
1. Answer ONLY using the CONTEXT provided below. Do not use any outside knowledge,
   even if you believe you know the answer.
2. If the CONTEXT does not contain enough information to answer the question,
   respond with exactly: "I don't know — please check denhaag.nl directly or
   contact the municipality." Do not guess, and do not fill gaps with
   general knowledge about the Netherlands or other municipalities.
3. Never invent deadlines, fees, phone numbers, or procedures that are not
   explicitly stated in the CONTEXT.
4. Keep answers concise and practical — a resident should be able to act on
   your answer immediately.
5. When you do answer, do not mention "the context" or "the documents" —
   answer naturally, as the municipality would."""


def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)


def retrieve(question, top_k=TOP_K):
    """Return top_k chunks with their metadata and distances."""
    collection = _get_collection()
    results = collection.query(query_texts=[question], n_results=top_k)

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        chunks.append({"text": doc, "metadata": meta, "distance": dist})
    return chunks


def build_prompt(question, chunks):
    context_blocks = []
    for i, c in enumerate(chunks):
        title = c["metadata"].get("source_title", "Unknown source")
        context_blocks.append(f"[Source {i+1}: {title}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_blocks)

    user_prompt = f"""CONTEXT:
{context}

QUESTION: {question}

Answer the question using only the CONTEXT above, following the strict rules."""
    return user_prompt


def call_llm(question, chunks, groq_api_key=None):
    client = Groq(api_key=groq_api_key or os.environ.get("GROQ_API_KEY"))
    user_prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content


def answer_question(question, groq_api_key=None):
    """Full pipeline: retrieve -> confidence check -> answer or decline.

    Returns a dict:
        {
            "answer": str,
            "declined": bool,          # True if we declined on low confidence
            "sources": [ {title, url, snippet, distance}, ... ],
            "best_distance": float,
        }
    """
    chunks = retrieve(question)

    if not chunks:
        return {
            "answer": "I don't know — please check denhaag.nl directly or contact the municipality.",
            "declined": True,
            "sources": [],
            "best_distance": None,
        }

    best_distance = chunks[0]["distance"]
    sources = [
        {
            "title": c["metadata"].get("source_title", ""),
            "url": c["metadata"].get("source_url", ""),
            "snippet": c["text"][:400],
            "distance": round(c["distance"], 3),
        }
        for c in chunks
    ]

    if best_distance > DISTANCE_THRESHOLD:
        return {
            "answer": (
                "I don't know — this doesn't look like it's covered in my "
                "current documents. Please check denhaag.nl directly or "
                "contact the municipality (tel. 14070)."
            ),
            "declined": True,
            "sources": sources,
            "best_distance": round(best_distance, 3),
        }

    answer = call_llm(question, chunks, groq_api_key=groq_api_key)
    declined = answer.strip().lower().startswith("i don't know")

    return {
        "answer": answer,
        "declined": declined,
        "sources": sources,
        "best_distance": round(best_distance, 3),
    }
