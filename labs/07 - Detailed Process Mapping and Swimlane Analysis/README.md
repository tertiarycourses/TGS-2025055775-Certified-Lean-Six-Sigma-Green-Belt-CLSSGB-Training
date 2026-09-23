# Lab 7 — Detailed Process Mapping and Swimlane Analysis

**DMAIC phase:** MEASURE  |  **Lab type:** Core  |  **Course:** Certified Lean Six Sigma Green Belt (CLSSGB) Training (TGS-2025055775)

## Objective

Map the as-is process to expose handoffs, delays and rework loops (A2).

## Scenario

Northwind Retail Distribution Centre fulfils online orders from a 12,000 sqm warehouse. Customers are complaining about late deliveries and the company is receiving negative feedback on social media. The Distribution Manager has asked you, as Green Belt, to lead a DMAIC project on the order-fulfilment process — from order release to carrier handover.

## What you will build

A detailed process map and a swimlane map with pain points and handoffs marked.

**Tools and techniques:** SIPOC & Process Map Builder, process symbols, flowchart, swimlane map, handoff analysis, pain points

## Data for this lab

Open the workbook(s) below from this lab's `data/` folder. Every lab uses the same Northwind baseline month, so the figures reconcile across the whole course.

- **[`lab07-process-steps-timing.xlsx`](data/lab07-process-steps-timing.xlsx)** — A gemba walk record of the 14 as-is process steps, with the actor, system, observed elapsed time and whether the step crosses to a new actor (a handoff).

**Working with `lab07-process-steps-timing.xlsx`:**

- Count every 'Yes' in the Handoff column — each one is a queue and a risk of information loss.
- Steps 7 and 9 are the rework loops; 22% of orders take step 7 and 9% take step 9.

### Online tools used in this lab

- **SIPOC & Process Map Builder** — https://alfredang.github.io/sipoc/

## Steps

### Step 1

Review the standard process symbols: oval for start/stop, rectangle for activity, diamond for decision, D-shape for delay, and the document symbol.

### Step 2

Walk the process physically (go to gemba) and record every step in sequence as it actually happens — not as the SOP says it should.

### Step 3

Open lab07-process-steps-timing.xlsx — a gemba walk record of all 14 as-is steps with actor, system, elapsed time and handoff flag. Build the detailed process map from it.

### Step 4

Continue in the SIPOC & Process Map Builder — assign an actor to each step and it generates the swimlane and the handoff table for you.

Open the tool: <https://alfredang.github.io/sipoc/>

### Step 5

Redraw the same flow as a swimlane map, giving each actor or department its own lane.

### Step 6

Count the handoffs in the workbook's Handoff column — every lane crossing is a queue and a risk of information loss.

### Step 7

Mark every decision diamond that creates a rework loop and note what percentage of work takes the rework path.

### Step 8

Tag pain points: delays, rework, unclear ownership, duplicate data entry and waiting for approval.

### Step 9

Identify the three steps you suspect consume the most elapsed time — you will test that suspicion with data in Lab 9.

## Check your work

Every lane crossing on your swimlane map is marked as a handoff with a named owner on both sides, and every rework loop is labelled with its percentage.

## Deliverable

Save your output — it forms part of your Northwind improvement package and is your revision material for the assessment.

---

*Certified Lean Six Sigma Green Belt (CLSSGB) Training · TGS-2025055775 · Version v5 · © 2026 Tertiary Infotech Academy Pte Ltd*
