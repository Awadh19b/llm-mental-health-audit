#!/usr/bin/env python3
"""Inter-rater agreement between the AI first-pass scores and a human reviewer.

  python agreement.py human_check_30.csv review_scored_claude.csv

Reports, per scale (S, C, B, Q): n compared, exact agreement, and quadratic-weighted Cohen's kappa
(0-2 ordinal). Rows/scales left blank by either rater are skipped.
"""
import csv, sys
from collections import Counter

def load(path):
    return {r["item_id"]: r for r in csv.DictReader(open(path, encoding="utf-8-sig"))}

def qwk(a, b, k=3):
    n = len(a)
    O = [[0] * k for _ in range(k)]
    for x, y in zip(a, b): O[x][y] += 1
    ra, rb = Counter(a), Counter(b)
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * O[i][j]; den += w * ra[i] * rb[j] / n
    return 1 - num / den if den else float("nan")

h, c = load(sys.argv[1]), load(sys.argv[2])
print("scale  n  exact%  qw-kappa")
for s in "SCBQ":
    pairs = [(int(h[i][s]), int(c[i][s])) for i in h if i in c
             and h[i][s].strip() in "012" and h[i][s].strip() and c[i][s].strip() in "012" and c[i][s].strip()]
    if not pairs: print(s, "no overlap"); continue
    a, b = zip(*pairs)
    print(f"{s:<5} {len(pairs):>3}  {100*sum(x==y for x,y in pairs)/len(pairs):5.0f}%   {qwk(list(a), list(b)):.2f}")
print("\nRule of thumb: kappa >= 0.6 substantial, 0.4-0.6 moderate, < 0.4 weak. Discuss disagreements, then refine the rubric.")
