# Lab 22 — FMEA, Risk Priority Numbers, DOE and Piloting

**DMAIC phase:** IMPROVE  |  **Lab type:** Core  |  **Course:** Certified Lean Six Sigma Green Belt (CLSSGB) Training (TGS-2025055775)

## Objective

Risk-assess and pilot the selected solution before full rollout (A5).

## Scenario

Northwind Retail Distribution Centre fulfils online orders from a 12,000 sqm warehouse. Customers are complaining about late deliveries and the company is receiving negative feedback on social media. The Distribution Manager has asked you, as Green Belt, to lead a DMAIC project on the order-fulfilment process — from order release to carrier handover.

## What you will build

A completed FMEA with RPN scores, a DOE plan and a pilot plan with success criteria.

**Tools and techniques:** FMEA, severity, occurrence, detection, RPN, DOE factors and levels, pilot design, rollback plan

## Data for this lab

Open the workbook(s) below from this lab's `data/` folder. Every lab uses the same Northwind baseline month, so the figures reconcile across the whole course.

- **[`lab22-fmea-worksheet.xlsx`](data/lab22-fmea-worksheet.xlsx)** — Failure modes for the selected solution, ready to be scored for Severity, Occurrence and Detection, plus the factors and levels for the DOE.
- **[`lab22-doe-pilot-results.xlsx`](data/lab22-doe-pilot-results.xlsx)** — The four runs of the 2x2 full factorial pilot, each run for one week, with the resulting mean lead time and late percentage.

**Working with `lab22-fmea-worksheet.xlsx`:**

- RPN = Severity x Occurrence x Detection. Score each 1-10 using the scales in the slides.
- Any RPN above 100, or any Severity of 9-10 regardless of RPN, needs a mitigation before go-live.
- DOE: factors are Replen Trigger Level (low/high) and Night Replenisher (absent/present).
- A 2-factor, 2-level full factorial needs 4 runs. Why vary both together rather than one at a time?

**Working with `lab22-doe-pilot-results.xlsx`:**

- Calculate the main effect of each factor, then the interaction effect.
- Run 4 beats the 3.0% target — but is the improvement more than the sum of the two main effects?
- That difference IS the interaction, and it is invisible to one-factor-at-a-time testing.

## Steps

### Step 1

List every process step of the NEW improved process in the FMEA worksheet.

### Step 2

For each step, identify the potential failure modes — the ways this step could go wrong.

### Step 3

For each failure mode, record the potential effect on the customer and the potential cause.

### Step 4

Open lab22-fmea-worksheet.xlsx — six failure modes for the selected solution with blank Sev/Occ/Det columns. Score Severity 1-10: how serious is the effect on the customer?

### Step 5

Score Occurrence 1-10: how likely is this cause to happen?

### Step 6

Score Detection 1-10, remembering the scale is inverted — 1 means it is almost certainly caught, 10 means it escapes undetected.

### Step 7

Calculate the Risk Priority Number in the workbook's RPN column: RPN = Severity x Occurrence x Detection.

### Step 8

Sort by RPN descending and address the highest scores first. Treat any Severity of 9 or 10 as requiring action regardless of its RPN.

### Step 9

Write the recommended action for each high-RPN row, assign an owner and a date, then recalculate the projected RPN after the action.

### Step 10

Plan a designed experiment for the settings you must optimise: list the factors, choose two levels (high and low) for each, and note that a 2^k design tests all combinations.

### Step 11

Record why DOE beats one-factor-at-a-time testing: OFAT cannot reveal the INTERACTION between two factors, only their individual effects.

### Step 12

Design the pilot: define the scope (one shift, one product family), the duration, the success criteria and the measurement method.

### Step 13

Set the pilot success criteria against your measured baseline from Lab 12 and 13 — the pilot must beat the baseline by a stated margin.

### Step 14

Write the rollback plan: what triggers stopping the pilot and how the process reverts safely.

### Step 15

Run the pilot, collect data using the same operational definitions as your baseline, and compare like with like.

### Step 16

Decide: scale up, adjust and re-pilot, or stop. Record the decision and the evidence behind it.

## Check your work

Every FMEA row has an RPN, the highest RPNs have owned actions with dates, and your pilot has quantified success criteria measured against the Lab 13 baseline.

## Deliverable

Save your output — it forms part of your Northwind improvement package and is your revision material for the assessment.

---

*Certified Lean Six Sigma Green Belt (CLSSGB) Training · TGS-2025055775 · Version v5 · © 2026 Tertiary Infotech Academy Pte Ltd*
