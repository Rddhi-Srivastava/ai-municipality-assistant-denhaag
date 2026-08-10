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

| # | Question | Expected | Actual | Correct? |
|---|----------|----------|--------|----------|
| 1 | Change of address | Answered | _run eval_ | |
| 2 | 5-day reporting window | Answered | _run eval_ | |
| 3 | Child moving report | Answered | _run eval_ | |
| 4 | Parking permit documents | Answered | _run eval_ | |
| 5 | 2nd car permit fee | Answered | _run eval_ | |
| 6 | Passport appointment items | Answered | _run eval_ | |
| 7 | Passport processing time | Answered | _run eval_ | |
| 8 | Bulky waste - fridge | Answered | _run eval_ | |
| 9 | Bulky waste size limits | Answered | _run eval_ | |
| 10 | Waste tax, 2-person household | Answered | _run eval_ | |
| 11 | Museum opening hours | Declined | _run eval_ | |
| 12 | Naturalisation process | Declined | _run eval_ | |
| 13 | OZB rate calculation | Declined | _run eval_ | |
| 14 | Public transport refund | Declined | _run eval_ | |
| 15 | Best neighbourhood (opinion) | Declined | _run eval_ | |

**Headline stat (fill in after running):** X/10 in-scope answered correctly
grounded in the right source, Y/5 out-of-scope correctly declined, 0
hallucinated facts observed.
