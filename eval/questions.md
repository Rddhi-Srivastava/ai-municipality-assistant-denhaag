# Evaluation Question Set

15 questions used to test the assistant: 10 in-scope (answerable from the
5 ingested denhaag.nl pages) and 5 out-of-scope (should be correctly declined).

Run `python eval/run_eval.py` to execute all of these automatically and
regenerate the results table below.

## In-scope questions (should be answered, grounded in a cited source)

1. How do I register a change of address in Den Haag?
2. How many days after moving do I have to report my new address?
3. Can I report a move for my child if they are 10 years old?
4. What documents do I need to apply for a resident parking permit?
5. How much does a resident parking permit cost for a second car?
6. What do I need to bring to my passport appointment?
7. How long does it take to get a Dutch passport after applying?
8. Will the municipality collect an old refrigerator as bulky waste?
9. What size limits apply to bulky waste I put on the street?
10. How much waste tax does a 2-person household pay per year?

## Out-of-scope questions (should be declined with "I don't know")

11. What are the opening hours of the Mauritshuis museum?
12. How do I apply for Dutch citizenship through naturalisation?
13. What is the current property tax (OZB) rate for a €400,000 home?
14. Can I get a refund on my public transport card if I move abroad?
15. What's the best neighbourhood in Den Haag for families with young children?

## Results

Run on a fresh ingest, Groq `llama-3.3-70b-versatile`, distance threshold 0.75.

| # | Question | Expected | Distance | Declined? | Correct? |
|---|----------|----------|----------|-----------|----------|
| 1 | Change of address | Answered | 0.510 | No | ✅ |
| 2 | 5-day reporting window | Answered | 0.252 | No | ✅ |
| 3 | Child moving report | Answered | 0.274 | No | ✅ |
| 4 | Parking permit documents | Answered | 0.435 | No | ✅ |
| 5 | 2nd car permit fee | Answered | 0.389 | No | ✅ |
| 6 | Passport appointment items | Answered | 0.442 | No | ✅ |
| 7 | Passport processing time | Answered | 0.381 | No | ✅ |
| 8 | Bulky waste - fridge | Answered | 0.360 | No | ✅ |
| 9 | Bulky waste size limits | Answered | 0.388 | No | ✅ |
| 10 | Waste tax, 2-person household | Answered | 0.461 | No | ✅ |
| 11 | Museum opening hours | Declined | 0.754 | Yes (distance) | ✅ |
| 12 | Naturalisation process | Declined | 0.329 | Yes (LLM) | ✅ |
| 13 | OZB rate calculation | Declined | 0.539 | Yes (LLM) | ✅ |
| 14 | Public transport refund | Declined | 0.592 | Yes (LLM) | ✅ |
| 15 | Best neighbourhood (opinion) | Declined | 0.778 | Yes (distance) | ✅ |

**Headline stat: 15/15 (100%).** 10/10 in-scope questions answered
correctly and grounded in the right source; 5/5 out-of-scope questions
correctly declined; 0 hallucinated facts observed.

**Notable finding:** the two hallucination defenses catch different failure
modes. Questions 11 and 15 were declined by the *distance threshold* alone:
nothing in the corpus was lexically close enough to even reach the LLM.
Questions 12–14 had *low* distance (0.33–0.59, well under the 0.75
threshold), meaning retrieval found topically-adjacent chunks, but the
LLM itself declined because the retrieved context didn't actually answer
the question (e.g. naturalisation is briefly mentioned on the "moving"
page's navigation but never explained). This shows the prompt-level
grounding rule is doing real, independent work beyond the similarity
threshold. Without it, a topically-close-but-non-answering chunk could
tempt the LLM into an unsupported answer.
