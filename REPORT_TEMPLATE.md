# Bias & Safety Audit of an LLM on Mental-Health Topics

**Model under test:** {{MODEL}}  **Run:** {{RUN_ID}}  **Date:** {{DATE}}
**Prompts:** {{N_PROMPTS}}  **Responses:** {{N_RESPONSES}} (~{{SAMPLES}} per prompt)  **Manually scored:** {{N_MANUAL}}

> Status: DRAFT. Replace every `TODO` with your own findings. Keep only claims your data supports.

## 1. Executive summary
TODO: 4-6 sentences. Overall risk level; the 3 most serious failures (with prompt IDs); whether bias was
detected; the single most important recommendation.

## 2. Scope and method
- **Goal:** evaluate safety, calibration, and fairness of the model's replies to mental-health prompts.
- **Configuration:** TODO (model id, version/date, temperature, system prompt used or none, API vs app).
- **Test suite:** 9 categories (crisis/self-harm, diagnosis & calibration, stigma, sycophancy, dependency & privacy,
  jailbreak framing, minors, cross-lingual, counterfactual bias). All prompts synthetic. See `prompts.py`.
- **Counterfactual bias design:** identical scenario, only the persona sentence changes (gender, age, ethnicity,
  religion, orientation, class) plus a no-persona control.
- **Scoring:** blind, shuffled human review on four 0-2 scales (S safety, C calibration, B bias/stigma, Q support quality),
  rubric in README. Automatic regex flags used only to prioritise review. Reviewer(s): TODO. Agreement: TODO.
- **Statistics:** permutation test on group gaps, Bonferroni-corrected.

## 3. Results
{{RESULTS_TABLES}}

## 4. Findings
Use one block per finding, ordered by severity.

### F-01 TODO short title  [Severity: Critical / High / Medium / Low]
- **Category / prompts:** TODO (e.g. SH-02, SH-02-ar)
- **What happened:** TODO (rate across samples, e.g. "4 of 5 samples")
- **Why it matters:** TODO (harm pathway)
- **Evidence:** TODO (short excerpt; redact any method detail)
- **Confidence:** TODO (n, reviewer agreement, uncertainty)

### F-02 ...

## 5. Bias analysis
TODO: for each dimension, state whether disparities were found, their size, and whether they survive correction.
Report null results too ("no detectable difference at this sample size" is not "no bias").

## 6. Limitations
- Single-turn prompts (plus one scripted multi-turn); real distress unfolds over many turns.
- Synthetic personas are a thin proxy for real users; one persona sentence is a weak signal.
- Sampling at temperature > 0 means results vary between runs; small n widens uncertainty.
- Regex flags have false positives/negatives; manual scoring is subjective (report agreement).
- English and Arabic only; one model/version; results may not transfer to other deployments or system prompts.
- Hotline/resource ground truth must be re-verified at publication time.

## 7. Recommendations
Candidate recommendations, **keep only those your evidence supports** and tie each to a finding:

| # | Recommendation | Addresses | Priority |
|---|---|---|---|
| R1 | Add/strengthen crisis-detection behaviour: direct safety check, no method/means information when distress cues are present, including indirect requests. | F-TODO | TODO |
| R2 | Provide locale-aware crisis resources from a verified, regularly updated directory instead of model memory; never invent numbers. | F-TODO | TODO |
| R3 | Calibration: refuse yes/no diagnoses, give ranges with uncertainty, and block fabricated citations/statistics. | F-TODO | TODO |
| R4 | Reduce sycophancy on delusional, eating-disorder, and isolation prompts with targeted evaluation and training data. | F-TODO | TODO |
| R5 | Close the cross-lingual gap: add Arabic (and other) safety test sets and training data. | F-TODO | TODO |
| R6 | Add counterfactual-fairness tests to CI; alert on gap/p-value thresholds per release. | F-TODO | TODO |
| R7 | Harden against role-play, fiction, and claimed-authority framing for self-harm methods. | F-TODO | TODO |
| R8 | Dependency/privacy: honest statements on memory, data handling, and limits; encourage human support. | F-TODO | TODO |
| R9 | Human oversight: sampled review of high-risk conversations, escalation paths, incident process. | F-TODO | TODO |

## 8. Appendix
- A. Full prompt list and expected safe behaviour (`prompts.py`)
- B. Scoring rubric and reviewer instructions (README)
- C. Raw data: `audit.db`, `review_blind.csv`, `review_key.csv`
- D. Reproduction commands
