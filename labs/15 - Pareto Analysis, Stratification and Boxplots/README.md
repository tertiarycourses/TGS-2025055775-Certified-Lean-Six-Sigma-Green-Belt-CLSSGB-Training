# Lab 15 — Pareto Analysis, Stratification and Boxplots

**DMAIC phase:** ANALYZE  |  **Lab type:** Core  |  **Course:** Certified Lean Six Sigma Green Belt (CLSSGB) Training (TGS-2025055775)

## Objective

Prioritise the vital few causes using Pareto and stratified analysis (A3).

## Scenario

Northwind Retail Distribution Centre fulfils online orders from a 12,000 sqm warehouse. Customers are complaining about late deliveries and the company is receiving negative feedback on social media. The Distribution Manager has asked you, as Green Belt, to lead a DMAIC project on the order-fulfilment process — from order release to carrier handover.

## What you will build

A Pareto chart with cumulative line, stratified Pareto charts and comparative boxplots.

**Tools and techniques:** Pareto principle, Pareto chart, cumulative percentage, stratification, boxplot, quartiles, outliers

## Data for this lab

Open the workbook(s) below from this lab's `data/` folder. Every lab uses the same Northwind baseline month, so the figures reconcile across the whole course.

- **[`lab15-late-causes-pareto.xlsx`](data/lab15-late-causes-pareto.xlsx)** — Every one of the 357 late orders assigned to a root-cause category, with the cost impact — the input to the Pareto chart and the vital-few decision.
- **[`lab15-late-by-stratum.xlsx`](data/lab15-late-by-stratum.xlsx)** — The same 357 late orders cut by shift and by carrier, to test whether the problem is uniform across the operation or concentrated in particular cells.

**Working with `lab15-late-causes-pareto.xlsx`:**

- Sort descending by count, compute the cumulative percentage, then draw the 80% cut line.
- Identify the VITAL FEW — the causes to the left of the 80% line.
- Then stratify the same 357 late orders by shift and by carrier and see whether the picture changes.

**Working with `lab15-late-by-stratum.xlsx`:**

- A stratification that shows one cell far worse than the others has found you a root cause.
- Use this to decide where the Fishbone in Lab 16 should focus.

## Steps

### Step 1

Open lab15-late-causes-pareto.xlsx — all 357 late orders already assigned to a root-cause category with their cost impact.

### Step 2

Count the frequency of each category and sort the categories in descending order of frequency.

### Step 3

Calculate the cumulative percentage across the sorted categories.

### Step 4

Draw the Pareto chart: descending bars on the left axis, cumulative percentage line on the right axis.

### Step 5

Read where the cumulative line crosses 80% — the categories to the left of that point are your vital few.

### Step 6

Open lab15-late-by-stratum.xlsx and rebuild the Pareto separately for each shift and each carrier.

### Step 7

Compare the stratified charts. If one shift or carrier dominates, the problem is concentrated and your project scope should narrow to it.

### Step 8

Build a boxplot of cycle time by stratification factor — read the median, the interquartile box, the whiskers and any outliers.

### Step 9

Use the boxplots to compare groups visually: if the boxes barely overlap, the groups are probably genuinely different — a hypothesis you will test formally in Lab 17.

### Step 10

Write your prioritisation conclusion: which categories you will pursue and which you are explicitly deferring.

## Check your work

Your Pareto identifies the vital few crossing 80% cumulative, and your stratified charts show whether the problem is universal or concentrated in a subgroup.

## Deliverable

Save your output — it forms part of your Northwind improvement package and is your revision material for the assessment.

---

*Certified Lean Six Sigma Green Belt (CLSSGB) Training · TGS-2025055775 · Version v5 · © 2026 Tertiary Infotech Academy Pte Ltd*
