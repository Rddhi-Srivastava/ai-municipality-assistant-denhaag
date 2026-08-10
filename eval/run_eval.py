"""
eval/run_eval.py — Runs the 15-question test set against the RAG pipeline
and prints a pass/fail summary. Requires ChromaDB to already be populated
(run `python ingest.py` first) and a GROQ_API_KEY environment variable set.

Usage:
    export GROQ_API_KEY=your_key_here
    python eval/run_eval.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rag import answer_question  # noqa: E402

IN_SCOPE_QUESTIONS = [
    "How do I register a change of address in Den Haag?",
    "How many days after moving do I have to report my new address?",
    "Can I report a move for my child if they are 10 years old?",
    "What documents do I need to apply for a resident parking permit?",
    "How much does a resident parking permit cost for a second car?",
    "What do I need to bring to my passport appointment?",
    "How long does it take to get a Dutch passport after applying?",
    "Will the municipality collect an old refrigerator as bulky waste?",
    "What size limits apply to bulky waste I put on the street?",
    "How much waste tax does a 2-person household pay per year?",
]

OUT_OF_SCOPE_QUESTIONS = [
    "What are the opening hours of the Mauritshuis museum?",
    "How do I apply for Dutch citizenship through naturalisation?",
    "What is the current property tax (OZB) rate for a €400,000 home?",
    "Can I get a refund on my public transport card if I move abroad?",
    "What's the best neighbourhood in Den Haag for families with young children?",
]


def run():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Set GROQ_API_KEY before running the eval.")
        sys.exit(1)

    print("=" * 70)
    print("IN-SCOPE QUESTIONS (expected: answered, not declined)")
    print("=" * 70)
    in_scope_correct = 0
    for q in IN_SCOPE_QUESTIONS:
        result = answer_question(q, groq_api_key=api_key)
        ok = not result["declined"]
        in_scope_correct += ok
        status = "PASS" if ok else "FAIL"
        print(f"\n[{status}] Q: {q}")
        print(f"  distance={result['best_distance']}  declined={result['declined']}")
        print(f"  A: {result['answer'][:200]}")

    print("\n" + "=" * 70)
    print("OUT-OF-SCOPE QUESTIONS (expected: declined)")
    print("=" * 70)
    out_scope_correct = 0
    for q in OUT_OF_SCOPE_QUESTIONS:
        result = answer_question(q, groq_api_key=api_key)
        ok = result["declined"]
        out_scope_correct += ok
        status = "PASS" if ok else "FAIL"
        print(f"\n[{status}] Q: {q}")
        print(f"  distance={result['best_distance']}  declined={result['declined']}")
        print(f"  A: {result['answer'][:200]}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"In-scope answered correctly:  {in_scope_correct}/{len(IN_SCOPE_QUESTIONS)}")
    print(f"Out-of-scope declined correctly: {out_scope_correct}/{len(OUT_OF_SCOPE_QUESTIONS)}")
    total = len(IN_SCOPE_QUESTIONS) + len(OUT_OF_SCOPE_QUESTIONS)
    print(f"Overall: {in_scope_correct + out_scope_correct}/{total}")


if __name__ == "__main__":
    run()
