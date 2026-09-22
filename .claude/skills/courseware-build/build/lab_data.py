"""
SINGLE SOURCE OF TRUTH for the Northwind lab DATA.

Every lab dataset is generated here from ONE reconciled month of order-fulfilment
data, so the numbers a learner works with in Lab 2 are the same numbers they
re-use in Labs 10-18 and prove they fixed in Lab 25.

THE ANCHOR (do not change without changing the assessment papers)
-----------------------------------------------------------------
The v6 PP assessment states the baseline verbatim:

    "4,200 orders were shipped and 357 of them were delivered late (8.5%).
     The business wants late shipments reduced to 3.0%."

So the generated order book contains EXACTLY 4,200 orders of which EXACTLY 357
breach the 48-hour CTQ. Every derived dataset (Pareto counts, stratified
samples, control-chart subgroups) is a genuine slice of that same order book —
nothing is invented independently, so the labs can never contradict each other
or the assessment.

The data is deterministic: a fixed RNG seed means every rebuild produces
byte-identical files, so a learner's answer key stays valid across versions.

Each dataset is a dict:
    key      -> stable dataset id, used in the filename
    lab      -> the lab number that owns it
    title    -> sheet/worksheet title
    desc     -> one line telling the learner what the data is
    headers  -> list of column headers
    rows     -> list of row lists
    notes    -> optional list of lines appended under the table as guidance
"""
import random
from datetime import date, timedelta

# ------------------------------------------------------------------ anchors
TOTAL_ORDERS = 4200          # PP assessment baseline
LATE_ORDERS = 357            # PP assessment baseline (8.5%)
CTQ_HOURS = 48.0             # USL: promised order-to-handover lead time
TARGET_LATE_PCT = 3.0        # PP assessment improvement target

SEED = 20260719              # fixed => deterministic rebuilds

SHIFTS = ["Morning", "Afternoon", "Night"]
CARRIERS = ["SpeedEx", "NationWide", "CityLink", "PostalPlus"]
ZONES = ["Zone A", "Zone B", "Zone C", "Zone D"]
CHANNELS = ["Web", "Marketplace", "Phone", "B2B Contract"]

# The eight root-cause categories that drive lateness. Weights are the
# ground truth the Pareto in Lab 15 is designed to reveal: the top three
# causes account for ~72% of all late orders (the vital few).
LATE_CAUSES = [
    ("Stock not in pick face", 112),
    ("Pick error / re-pick", 81),
    ("Carrier cut-off missed", 64),
    ("WMS downtime", 39),
    ("Packing station queue", 26),
    ("Address / data error", 18),
    ("Goods-in not putaway", 11),
    ("Other", 6),
]
assert sum(c[1] for c in LATE_CAUSES) == LATE_ORDERS, "causes must reconcile to LATE_ORDERS"

START = date(2026, 6, 1)     # the baseline month: June 2026


def _rng():
    return random.Random(SEED)


# ------------------------------------------------------------------ core order book
def build_orders():
    """Generate the 4,200-order baseline month.

    Lead time is drawn from a right-skewed distribution centred near 31h. Late
    orders are then assigned an explicit cause and pushed past the 48h CTQ, so
    the late count is exactly 357 and each late order carries a cause that the
    Pareto (Lab 15) and the Fishbone (Lab 16) can act on.
    """
    r = _rng()

    # which order indices are late — biased toward Night shift and the two
    # weakest carriers so the stratification in Lab 15 finds a real signal
    idx = list(range(TOTAL_ORDERS))
    r.shuffle(idx)

    cause_pool = []
    for name, count in LATE_CAUSES:
        cause_pool += [name] * count
    r.shuffle(cause_pool)

    # Build a lateness propensity per order so late orders concentrate in the
    # Night shift / SpeedEx+PostalPlus cells rather than spreading evenly.
    meta = []
    for i in range(TOTAL_ORDERS):
        day = i * 30 // TOTAL_ORDERS                     # spread across 30 days
        shift = SHIFTS[i % 3]
        carrier = CARRIERS[(i // 3) % 4]
        zone = ZONES[(i // 7) % 4]
        channel = CHANNELS[(i // 11) % 4]
        w = 1.0
        if shift == "Night":
            w *= 2.6
        if carrier in ("SpeedEx", "PostalPlus"):
            w *= 1.8
        if zone == "Zone D":
            w *= 1.4
        meta.append(dict(day=day, shift=shift, carrier=carrier,
                         zone=zone, channel=channel, w=w))

    # weighted selection of exactly LATE_ORDERS late orders, without replacement
    pool = sorted(range(TOTAL_ORDERS), key=lambda i: -(meta[i]["w"] * r.random()))
    late_set = set(pool[:LATE_ORDERS])

    rows = []
    ci = 0
    for i in range(TOTAL_ORDERS):
        m = meta[i]
        d = START + timedelta(days=m["day"])
        oid = f"NW-{26000 + i}"
        lines = r.choice([1, 1, 2, 2, 3, 4, 5, 6, 8])
        if i in late_set:
            # late: 48.1h .. ~96h, right-skewed
            lt = 48.0 + round(r.expovariate(1 / 11.0) + 0.6, 1)
            lt = min(lt, 142.0)
            cause = cause_pool[ci]
            ci += 1
        else:
            # on time: centred ~30h, never crossing the 48h CTQ
            lt = r.gauss(30.5, 6.4)
            lt = max(6.2, min(lt, 47.9))
            cause = ""
        rows.append([
            oid, d.isoformat(), m["channel"], m["shift"], m["carrier"], m["zone"],
            lines, round(lt, 1), "Late" if i in late_set else "On time", cause,
        ])
    return rows


ORDERS = build_orders()
H_ORDERS = ["Order ID", "Order Date", "Channel", "Shift", "Carrier", "Zone",
            "Order Lines", "Lead Time (hrs)", "Status", "Late Cause"]

_LT = [r[7] for r in ORDERS]
_LATE = [r for r in ORDERS if r[8] == "Late"]


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


BASE_MEAN = _mean(_LT)
BASE_SD = _sd(_LT)


# ================================================================== datasets
DATASETS = {}


def _add(key, lab, title, desc, headers, rows, notes=None):
    DATASETS[key] = dict(key=key, lab=lab, title=title, desc=desc,
                         headers=headers, rows=rows, notes=notes or [])
    return DATASETS[key]


# ---- Lab 1 — project selection / COPQ
_add("project-selection-candidates", 1,
     "Candidate Projects and COPQ Inputs",
     "Four candidate improvement projects screened in Lab 1, with the cost inputs "
     "needed to estimate the Cost of Poor Quality for each.",
     ["Candidate Project", "Annual Volume", "Defect Rate (%)",
      "Rework Cost/Unit (S$)", "Expedite Cost/Unit (S$)", "Credit Issued/Unit (S$)",
      "Data Available?", "Sponsor"],
     [["Reduce late order fulfilment", 50400, 8.5, 12.40, 38.00, 22.50, "Yes", "Distribution Manager"],
      ["Reduce pick errors in the mezzanine", 50400, 2.1, 9.80, 0.00, 31.00, "Yes", "Operations Lead"],
      ["Reduce goods-in putaway delay", 12600, 6.4, 7.20, 0.00, 0.00, "Partial", "Inbound Supervisor"],
      ["Install a new WMS", 0, 0.0, 0.00, 0.00, 0.00, "No", "None named"]],
     ["The last candidate is deliberately a SOLUTION, not a problem — it must be rejected in Step 5.",
      "Annualised COPQ = Annual Volume x Defect Rate x (Rework + Expedite + Credit) per unit."])

# ---- Lab 2 — Y=f(X), DPMO, sigma
_add("baseline-defect-summary", 2,
     "Baseline Defect Summary",
     "The monthly baseline used to calculate the defect rate, DPMO and sigma level. "
     "These are the exact figures quoted in the assessment.",
     ["Metric", "Value"],
     [["Orders shipped (units)", TOTAL_ORDERS],
      ["Orders delivered late (defects)", LATE_ORDERS],
      ["Defect opportunities per unit", 1],
      ["Promised lead time / CTQ (hours)", CTQ_HOURS],
      ["Business target for late shipments (%)", TARGET_LATE_PCT]],
     ["Defect rate = 357 / 4200 = 0.085 (8.5%).",
      "DPMO = (defects / (units x opportunities)) x 1,000,000.",
      "Read the resulting DPMO against the sigma conversion table in labs/tools.md."])

# ---- Lab 3 — VOC
_VOC = [
    ("VOC-01", "Web survey", "My order took four days when the site promised two.", "Delivery speed"),
    ("VOC-02", "Call centre", "Nobody told me the order was delayed — I had to chase.", "Communication"),
    ("VOC-03", "Social media", "Third late delivery this quarter. Consistency is the issue.", "Reliability"),
    ("VOC-04", "Web survey", "Tracking said shipped but it had not left the warehouse.", "Tracking accuracy"),
    ("VOC-05", "B2B review", "We cannot plan our shelves if the delivery window keeps moving.", "Reliability"),
    ("VOC-06", "Call centre", "Two of the six items were missing and arrived separately.", "Order completeness"),
    ("VOC-07", "Social media", "Fast when it works, but far too unpredictable.", "Reliability"),
    ("VOC-08", "Web survey", "I would pay more for a guaranteed next-day slot.", "Delivery speed"),
    ("VOC-09", "B2B review", "Give me an accurate ETA and I can work around a slower time.", "Communication"),
    ("VOC-10", "Call centre", "Packaging was damaged and the box was open.", "Condition"),
    ("VOC-11", "Web survey", "Weekend orders always seem to take longest.", "Reliability"),
    ("VOC-12", "Social media", "The refund took longer than the delivery.", "Aftersales"),
    ("VOC-13", "B2B review", "Need delivery before 10am to make the morning shelf-fill.", "Delivery speed"),
    ("VOC-14", "Web survey", "Item showed in stock at checkout but was actually out of stock.", "Stock accuracy"),
    ("VOC-15", "Call centre", "I want a text the moment it actually ships, not when it is picked.", "Communication"),
    ("VOC-16", "Web survey", "48 hours is fine — just tell me the truth up front.", "Communication"),
    ("VOC-17", "Social media", "Night-time orders are the worst for delays.", "Reliability"),
    ("VOC-18", "B2B review", "Consolidate my order into one drop instead of three.", "Order completeness"),
]
_add("voc-raw-statements", 3,
     "Raw Voice of the Customer Statements",
     "18 verbatim customer statements gathered from surveys, the call centre, social "
     "media and B2B account reviews — the raw input to the affinity diagram and Kano analysis.",
     ["VOC ID", "Source", "Verbatim Statement", "Suggested Theme"],
     [list(v) for v in _VOC],
     ["Cluster these into natural themes yourself BEFORE looking at the 'Suggested Theme' column.",
      "Then classify each resulting requirement as Must-Be, One-Dimensional or Delighter (Kano)."])

# ---- Lab 4 — CTQ
_add("ctq-requirements", 4,
     "CTQ Candidate Requirements",
     "Customer needs from Lab 3 ready to be translated into measurable CTQs with "
     "targets and specification limits.",
     ["Need (from VOC theme)", "Driver", "Proposed Measure", "Unit",
      "Target", "LSL", "USL"],
     [["Delivery is fast", "Delivery speed", "Order release to carrier handover", "hours", 24, 0, 48],
      ["Delivery is reliable", "Reliability", "Orders delivered within promise", "%", 97.0, 97.0, ""],
      ["I am kept informed", "Communication", "Time from delay to customer notification", "hours", 1, 0, 4],
      ["My order is complete", "Order completeness", "Orders shipped complete first time", "%", 99.0, 99.0, ""],
      ["Stock shown is real", "Stock accuracy", "Pick-face stock record accuracy", "%", 98.0, 98.0, ""]],
     ["The first row is the PROJECT Y — the 48-hour USL is the CTQ every later lab measures against.",
      "A one-sided requirement has only an LSL or only a USL; leave the other blank."])

# ---- Lab 5 — charter
_add("charter-inputs", 5,
     "Project Charter Inputs",
     "The agreed facts and figures to drop into the project charter — baseline, "
     "target, financials, team and milestones.",
     ["Charter Element", "Value"],
     [["Process", "Order fulfilment: order release to carrier handover"],
      ["Baseline late deliveries", "8.5% (357 of 4,200 orders, June 2026)"],
      ["Target late deliveries", "3.0%"],
      ["Baseline mean lead time (hrs)", round(BASE_MEAN, 1)],
      ["Baseline std deviation (hrs)", round(BASE_SD, 1)],
      ["CTQ / promised lead time (hrs)", CTQ_HOURS],
      ["Annualised COPQ (S$)", "1,674,000"],
      ["Sponsor", "Distribution Manager"],
      ["Green Belt (project lead)", "You"],
      ["Team", "Pick supervisor, Despatch lead, WMS analyst, Carrier liaison"],
      ["Define tollgate", "Week 2"],
      ["Measure tollgate", "Week 5"],
      ["Analyze tollgate", "Week 8"],
      ["Improve tollgate", "Week 12"],
      ["Control / closure", "Week 16"]],
     ["Your problem statement must contain the process, the period, the measurable gap and the impact — and no cause or solution.",
      "Goal statement: reduce late deliveries from 8.5% to 3.0% by week 16."])

# ---- Lab 6 — SIPOC / RACI
_add("sipoc-stakeholders", 6,
     "Process Steps and Stakeholder Register",
     "The high-level process steps for the SIPOC plus the stakeholder register to "
     "score for influence/interest and assign RACI.",
     ["Stakeholder", "Role", "Department", "Influence (1-5)", "Interest (1-5)", "Current Stance"],
     [["Distribution Manager", "Sponsor", "Distribution", 5, 5, "Supportive"],
      ["Pick Supervisor", "Process owner", "Warehouse", 4, 5, "Supportive"],
      ["Despatch Lead", "Process owner", "Despatch", 4, 4, "Neutral"],
      ["WMS Analyst", "Subject expert", "IT", 3, 3, "Neutral"],
      ["Carrier Liaison", "Interface owner", "Logistics", 3, 4, "Neutral"],
      ["Night Shift Lead", "Frontline", "Warehouse", 2, 5, "Sceptical"],
      ["Customer Service Manager", "Voice of customer", "Service", 3, 5, "Supportive"],
      ["Finance Controller", "Benefit validator", "Finance", 4, 2, "Sceptical"],
      ["Inbound Supervisor", "Upstream supplier", "Goods-in", 2, 3, "Neutral"]],
     ["Plot influence against interest to decide who to Manage Closely, Keep Satisfied, Keep Informed or Monitor.",
      "Exactly ONE person may be Accountable (A) for each process step in your RACI."])

# ---- Lab 7 — process mapping
_add("process-steps-timing", 7,
     "As-Is Process Steps with Observed Timings",
     "A gemba walk record of the 14 as-is process steps, with the actor, system, "
     "observed elapsed time and whether the step crosses to a new actor (a handoff).",
     ["Step", "Activity", "Actor", "System", "Elapsed Time (min)",
      "Value-Added?", "Handoff?", "Rework Loop?"],
     [[1, "Order released from OMS", "System", "OMS", 2, "No", "No", "No"],
      [2, "Order queued for wave planning", "Planner", "WMS", 165, "No", "Yes", "No"],
      [3, "Wave planned and released", "Planner", "WMS", 14, "No", "No", "No"],
      [4, "Pick list printed / assigned", "Pick Supervisor", "WMS", 9, "No", "Yes", "No"],
      [5, "Travel to pick face", "Picker", "-", 21, "No", "No", "No"],
      [6, "Pick items", "Picker", "RF Scanner", 18, "Yes", "No", "No"],
      [7, "Stock not in pick face — replenish", "Picker", "RF Scanner", 74, "No", "Yes", "Yes"],
      [8, "Pick verification scan", "Picker", "RF Scanner", 4, "No", "No", "No"],
      [9, "Pick error found — re-pick", "Checker", "RF Scanner", 52, "No", "Yes", "Yes"],
      [10, "Queue at packing station", "-", "-", 96, "No", "No", "No"],
      [11, "Pack and label", "Packer", "WMS", 11, "Yes", "Yes", "No"],
      [12, "Stage to despatch lane", "Packer", "-", 13, "No", "Yes", "No"],
      [13, "Await carrier collection", "-", "-", 118, "No", "No", "No"],
      [14, "Carrier handover scan", "Despatch Lead", "Carrier portal", 5, "Yes", "Yes", "No"]],
     ["Count every 'Yes' in the Handoff column — each one is a queue and a risk of information loss.",
      "Steps 7 and 9 are the rework loops; 22% of orders take step 7 and 9% take step 9."])

# ---- Lab 8 — VSM / takt
_add("vsm-timeline-demand", 8,
     "Value Stream Timeline and Demand Data",
     "Process-box data and the demand figures needed for the timeline ladder, "
     "process cycle efficiency and takt time calculations.",
     ["Process Box", "Cycle Time (min)", "Changeover (min)", "Uptime (%)",
      "Operators", "WIP Before (orders)", "Waiting Time After (min)"],
     [["Wave planning", 14, 5, 99, 1, 210, 165],
      ["Picking", 39, 0, 94, 12, 118, 0],
      ["Verification", 4, 0, 98, 3, 64, 96],
      ["Packing", 11, 3, 97, 8, 141, 0],
      ["Staging", 13, 0, 100, 2, 96, 118],
      ["Carrier handover", 5, 0, 99, 2, 0, 0]],
     ["Available working time = 3 shifts x 7.5 productive hours = 1,350 minutes per day.",
      "Customer demand = 4,200 orders / 30 days = 140 orders per day.",
      "Takt time = available working time / customer demand.",
      "Process cycle efficiency = value-added time / total lead time."])

# ---- Lab 9 — data collection plan
_add("data-collection-fields", 9,
     "Candidate Measures for the Data Collection Plan",
     "The fields available in the WMS/OMS extract, to be classified by data type "
     "and given operational definitions.",
     ["Field", "Example Value", "Data Type (classify)", "Source System",
      "Available?", "Notes"],
     [["Order ID", "NW-26014", "", "OMS", "Yes", "Unique key"],
      ["Order Date", "2026-06-03", "", "OMS", "Yes", ""],
      ["Lead Time (hrs)", "31.4", "", "Derived", "Yes", "Release to handover"],
      ["Status", "Late", "", "Derived", "Yes", "Against 48h CTQ"],
      ["Shift", "Night", "", "WMS", "Yes", "Stratification factor"],
      ["Carrier", "SpeedEx", "", "Carrier portal", "Yes", "Stratification factor"],
      ["Zone", "Zone D", "", "WMS", "Yes", "Stratification factor"],
      ["Channel", "Marketplace", "", "OMS", "Yes", "Stratification factor"],
      ["Order Lines", "4", "", "OMS", "Yes", "Possible X"],
      ["Late Cause", "WMS downtime", "", "Manual log", "Partial", "Only logged for late orders"],
      ["Picker ID", "P-207", "", "WMS", "Yes", "Possible X"],
      ["Customer Satisfaction", "4 of 5", "", "Survey", "Partial", "Ordinal"]],
     ["Classify each as Continuous, Discrete, Nominal or Ordinal — the type dictates which test is legal later.",
      "Write an operational definition for Lead Time: exactly when does the clock start and stop?"])

# ---- Lab 10 — sampling
_add("sampling-frame", 10,
     "Population Strata for the Sampling Plan",
     "The population broken down by shift and carrier, so a stratified sampling "
     "plan can be built and proportional sample sizes allocated.",
     ["Stratum (Shift x Carrier)", "Population (orders)", "Late Orders", "Late (%)"],
     None,  # filled below
     ["Use n = (1.96 s / d)^2 for continuous data. Preliminary s = %.1f hours." % BASE_SD,
      "Allocate the calculated n across strata in proportion to population size.",
      "Compare your calculated n against what is practical to collect and record the trade-off."])

# build the sampling frame from the real order book
_frame = {}
for r in ORDERS:
    k = (r[3], r[4])
    d = _frame.setdefault(k, [0, 0])
    d[0] += 1
    if r[8] == "Late":
        d[1] += 1
DATASETS["sampling-frame"]["rows"] = [
    [f"{s} / {c}", v[0], v[1], round(v[1] / v[0] * 100, 1)]
    for (s, c), v in sorted(_frame.items())
] + [["TOTAL", TOTAL_ORDERS, LATE_ORDERS, round(LATE_ORDERS / TOTAL_ORDERS * 100, 1)]]

# ---- Lab 11 — Gage R&R (attribute)
def _build_gage():
    r = random.Random(SEED + 11)
    rows = []
    for i in range(1, 31):
        # the known truth for each sample record
        truth = "Late" if i % 3 == 0 else "On time"
        out = [f"S-{i:02d}", truth]
        for appr in range(3):
            # Appraiser C is the unreliable one — the lab's teaching point is that
            # ONE appraiser working to a different operational definition drags the
            # whole measurement system below the acceptance threshold, even when
            # the other two are fine. A and B differ slightly so they are not clones.
            acc = [0.97, 0.93, 0.70][appr]
            for _trial in range(2):
                ok = r.random() < acc
                out.append(truth if ok else ("On time" if truth == "Late" else "Late"))
        rows.append(out)
    return rows


_add("gage-rr-attribute", 11,
     "Attribute Gage R&R Study Data",
     "30 order records classified as On time / Late by three appraisers, twice each, "
     "against the known correct attribute. The raw input to the agreement calculations.",
     ["Sample", "Known Correct", "A Trial 1", "A Trial 2", "B Trial 1", "B Trial 2",
      "C Trial 1", "C Trial 2"],
     _build_gage(),
     ["Repeatability (per appraiser) = % of samples where that appraiser agreed with THEMSELVES.",
      "Reproducibility = % of samples where ALL THREE appraisers agreed with each other.",
      "Accuracy = % where the appraiser matched the Known Correct column.",
      "One appraiser is materially worse than the others — identify who, and say what you would fix."])

# ---- Lab 12 — yield / RTY
_add("process-step-yields", 12,
     "First Pass Yield by Process Step",
     "Units entering and passing each process step first time, for the classic yield, "
     "FPY, RTY and hidden-factory calculations.",
     ["Step", "Process Step", "Units In", "Passed First Time",
      "Reworked", "Scrapped/Cancelled"],
     [[1, "Wave planning", 4260, 4235, 25, 0],
      [2, "Picking", 4235, 3302, 933, 0],
      [3, "Verification", 4235, 3854, 381, 0],
      [4, "Packing", 4235, 4160, 71, 4],
      [5, "Staging", 4231, 4210, 21, 0],
      [6, "Carrier handover", 4231, 4200, 31, 0]],
     ["Classic yield = units passing final inspection / units started.",
      "FPY per step = passed first time / units in. RTY = FPY1 x FPY2 x ... x FPY6.",
      "The gap between classic yield and RTY is the HIDDEN FACTORY — quantify it in orders and in dollars.",
      "Defect opportunities per order = 1 (a late delivery). Total defects = 357."])

# ---- Lab 13 — descriptive stats / capability (the full order book)
_add("order-lead-times", 13,
     "Baseline Order Lead Times",
     "The complete baseline month: 4,200 orders with lead time, status and "
     "stratification factors. This is the master dataset used by Labs 13-18 and 23.",
     H_ORDERS, ORDERS,
     ["Mean = %.2f hrs, standard deviation = %.2f hrs (compute these yourself to confirm)." % (BASE_MEAN, BASE_SD),
      "USL = 48 hours (the CTQ). LSL = 0 hours. There is no lower spec — a fast order is never a defect.",
      "Cp = (USL - LSL) / 6s.  Cpk = min[(USL - mean), (mean - LSL)] / 3s.",
      "Exactly 357 orders (8.5%) exceed the 48-hour CTQ — confirm this from the Status column."])

# ---- Lab 14 — run chart
_daily = {}
for r in ORDERS:
    _daily.setdefault(r[1], []).append(r[7])
_add("daily-mean-lead-time", 14,
     "Daily Mean Lead Time (Run Chart Data)",
     "Mean lead time and late count for each of the 30 days of the baseline month, "
     "in time order — the input to the run chart and stability analysis.",
     ["Day", "Date", "Orders Shipped", "Mean Lead Time (hrs)", "Late Orders", "Late (%)"],
     [[i + 1, d, len(v), round(_mean(v), 2),
       sum(1 for r in ORDERS if r[1] == d and r[8] == "Late"),
       round(sum(1 for r in ORDERS if r[1] == d and r[8] == "Late") / len(v) * 100, 1)]
      for i, (d, v) in enumerate(sorted(_daily.items()))],
     ["Plot in TIME ORDER — never sort this data.",
      "Draw the median line, then test for trend (6+), shift (8+), clustering, mixture, oscillation (14+) and bias.",
      "State whether the process is stable (common cause only) or unstable (special causes present)."])

# ---- Lab 15 — Pareto / stratification
_add("late-causes-pareto", 15,
     "Late Delivery Causes (Pareto Data)",
     "Every one of the 357 late orders assigned to a root-cause category, with the "
     "cost impact — the input to the Pareto chart and the vital-few decision.",
     ["Cause Category", "Late Orders", "% of Total", "Cumulative %", "Cost Impact (S$)"],
     None,
     ["Sort descending by count, compute the cumulative percentage, then draw the 80% cut line.",
      "Identify the VITAL FEW — the causes to the left of the 80% line.",
      "Then stratify the same 357 late orders by shift and by carrier and see whether the picture changes."])

_cum = 0
_cost = {"Stock not in pick face": 61.0, "Pick error / re-pick": 48.5,
         "Carrier cut-off missed": 94.0, "WMS downtime": 72.0,
         "Packing station queue": 33.0, "Address / data error": 41.0,
         "Goods-in not putaway": 55.0, "Other": 30.0}
_prows = []
for name, count in sorted(LATE_CAUSES, key=lambda x: -x[1]):
    pct = count / LATE_ORDERS * 100
    _cum += pct
    _prows.append([name, count, round(pct, 1), round(_cum, 1),
                   round(count * _cost[name], 2)])
DATASETS["late-causes-pareto"]["rows"] = _prows

_add("late-by-stratum", 15,
     "Late Orders by Shift and Carrier (Stratification)",
     "The same 357 late orders cut by shift and by carrier, to test whether the "
     "problem is uniform across the operation or concentrated in particular cells.",
     ["Shift", "Carrier", "Orders", "Late Orders", "Late (%)", "Mean Lead Time (hrs)"],
     None,
     ["A stratification that shows one cell far worse than the others has found you a root cause.",
      "Use this to decide where the Fishbone in Lab 16 should focus."])

_strat = {}
for r in ORDERS:
    k = (r[3], r[4])
    d = _strat.setdefault(k, dict(n=0, late=0, lt=[]))
    d["n"] += 1
    d["lt"].append(r[7])
    if r[8] == "Late":
        d["late"] += 1
DATASETS["late-by-stratum"]["rows"] = [
    [s, c, v["n"], v["late"], round(v["late"] / v["n"] * 100, 1), round(_mean(v["lt"]), 1)]
    for (s, c), v in sorted(_strat.items())
]

# ---- Lab 16 — fishbone / 5 whys
_add("cause-investigation-log", 16,
     "Cause Investigation Log and Multi-Voting Sheet",
     "Candidate causes raised by the team in the Fishbone session, ready for 5 Whys "
     "drill-down and multi-voting.",
     ["Cause ID", "Candidate Cause", "5M+E Category", "Raised By",
      "Evidence Available?", "Team Votes"],
     [["C-01", "Replenishment triggered too late to refill the pick face", "Method", "Pick Supervisor", "Yes — Lab 15 Pareto", 0],
      ["C-02", "Min/max levels never reviewed since go-live", "Method", "WMS Analyst", "Yes — WMS config", 0],
      ["C-03", "Night shift has no dedicated replenisher", "Manpower", "Night Shift Lead", "Yes — Lab 15 strata", 0],
      ["C-04", "RF scanners drop signal in the mezzanine", "Machine", "Picker", "Partial", 0],
      ["C-05", "Pick face too small for fast-moving SKUs", "Material", "Pick Supervisor", "Yes — slotting report", 0],
      ["C-06", "Carrier cut-off at 16:00 not visible to pickers", "Measurement", "Despatch Lead", "Yes — Lab 15 Pareto", 0],
      ["C-07", "WMS batch job locks the system at shift change", "Machine", "WMS Analyst", "Yes — downtime log", 0],
      ["C-08", "New pickers trained by shadowing, no standard", "Manpower", "Pick Supervisor", "Partial", 0],
      ["C-09", "Mezzanine aisles congested at peak", "Environment", "Picker", "No", 0],
      ["C-10", "Address validation not enforced at checkout", "Method", "CS Manager", "Yes — Lab 15 Pareto", 0]],
     ["Sort each cause onto the correct 5M+E bone: Manpower, Method, Machine, Material, Measurement, Environment.",
      "Run 5 Whys on your top-voted cause — stop when the answer is a PROCESS, not a person.",
      "Each team member gets N/3 votes where N is the number of causes. Record votes in the last column.",
      "Prioritise causes that have evidence — C-01, C-03 and C-06 are already supported by your Lab 15 data."])

# ---- Lab 17 — hypothesis testing
def _sample_for_test():
    """Two independent samples: Night shift vs Day shifts, for a 2-sample t-test."""
    r = random.Random(SEED + 17)
    night = [x[7] for x in ORDERS if x[3] == "Night"]
    day = [x[7] for x in ORDERS if x[3] != "Night"]
    ns = r.sample(night, 40)
    ds = r.sample(day, 40)
    return [[i + 1, ns[i], ds[i]] for i in range(40)]


_add("shift-comparison-samples", 17,
     "Night vs Day Shift Lead Time Samples",
     "Two independent random samples of 40 orders each — Night shift and Day shifts — "
     "drawn from the baseline month, for the hypothesis test.",
     ["Obs", "Night Shift Lead Time (hrs)", "Day Shift Lead Time (hrs)"],
     _sample_for_test(),
     ["H0: there is NO difference in mean lead time between night and day shifts.",
      "Ha: the means ARE different. Set alpha = 0.05 (95% confidence).",
      "Two independent samples + continuous data + comparing two means = 2-sample t-test.",
      "If p < 0.05, reject H0. State your conclusion in plain business language, not just the p-value."])

_add("cause-count-contingency", 17,
     "Late vs On-Time Counts by Carrier (Chi-Square Data)",
     "A contingency table of late and on-time counts by carrier — discrete data, so "
     "this one needs a chi-square test of independence rather than a t-test.",
     ["Carrier", "Late Orders", "On-Time Orders", "Total"],
     None,
     ["Discrete/count data comparing proportions across 4 groups = chi-square test of independence.",
      "H0: lateness is INDEPENDENT of carrier. Ha: lateness DEPENDS on carrier.",
      "Use this to practise TEST SELECTION — the data type chose the test, not your preference."])

_carr = {}
for r in ORDERS:
    d = _carr.setdefault(r[4], [0, 0])
    if r[8] == "Late":
        d[0] += 1
    else:
        d[1] += 1
DATASETS["cause-count-contingency"]["rows"] = [
    [c, v[0], v[1], v[0] + v[1]] for c, v in sorted(_carr.items())
] + [["TOTAL", LATE_ORDERS, TOTAL_ORDERS - LATE_ORDERS, TOTAL_ORDERS]]

# ---- Lab 18 — correlation / regression
def _regression_rows():
    """Daily replenishment backlog (X) vs mean lead time (Y) — a genuine positive
    relationship so the learner gets a real r and r^2 to interpret.

    The noise term is deliberately tuned so R lands around 0.8: comfortably past
    the |R| >= 0.4 threshold the lab teaches, but well short of a suspiciously
    perfect line. r^2 then explains roughly two thirds of the variation, which
    leaves the learner something real to say about the OTHER third.
    """
    r = random.Random(SEED + 18)
    out = []
    for i, (d, v) in enumerate(sorted(_daily.items())):
        y = _mean(v)
        x = (y - 24.0) * 6.4 + r.gauss(0, 2.6) + 18
        x = max(2, round(x))
        late = sum(1 for o in ORDERS if o[1] == d and o[8] == "Late")
        out.append([i + 1, d, x, round(y, 2), late])
    return out


_add("replen-vs-leadtime", 18,
     "Replenishment Backlog vs Lead Time (Regression Data)",
     "Daily replenishment backlog (the candidate X) paired with that day's mean "
     "lead time (the Y), for the scatter plot, correlation and regression.",
     ["Day", "Date", "Replen Backlog at 06:00 (tasks)",
      "Mean Lead Time (hrs)", "Late Orders"],
     _regression_rows(),
     ["Plot X (backlog) against Y (lead time) as a scatter plot FIRST — always look before you calculate.",
      "Calculate the correlation coefficient R. |R| >= 0.4 is treated as a correlation occurring.",
      "Fit the regression line Y = a + bX and calculate r^2 — the proportion of variation in Y explained by X.",
      "State the practical meaning: how many hours does each extra backlog task add to lead time?",
      "Remember: correlation does not prove causation. What else would you need to prove it?"])

# ---- Lab 19 — solution generation
_add("improvement-ideas", 19,
     "Improvement Ideas and Benchmark Findings",
     "Ideas generated by the team's brainwriting session plus external benchmark "
     "findings, ready to be screened in Lab 21.",
     ["Idea ID", "Improvement Idea", "Targets Cause", "Source", "Est. Cost (S$)",
      "Est. Impact (late orders/mth avoided)"],
     [["I-01", "Dynamic min/max replenishment triggers in the WMS", "C-01, C-02", "Brainwriting", 8000, 78],
      ["I-02", "Dedicated night-shift replenisher", "C-03", "Brainwriting", 46000, 61],
      ["I-03", "Re-slot top 200 SKUs into larger pick faces", "C-05", "Benchmark - competitor DC", 12000, 54],
      ["I-04", "Carrier cut-off countdown on every RF scanner", "C-06", "Brainwriting", 3500, 47],
      ["I-05", "Move the WMS batch job outside shift change", "C-07", "Benchmark - sister site", 1200, 31],
      ["I-06", "Standard work + certification for new pickers", "C-08", "Brainwriting", 9500, 22],
      ["I-07", "Enforce address validation at checkout", "C-10", "Benchmark - retail peer", 6000, 18],
      ["I-08", "Second packing station at peak", "Queue", "Brainwriting", 38000, 24],
      ["I-09", "Replace the entire WMS", "All", "Brainwriting", 950000, 0]],
     ["I-09 is a solution looking for a problem — note why it fails a cost-benefit screen.",
      "Each idea should trace back to a cause you PROVED in Labs 15-18, not to a hunch."])

# ---- Lab 20 — lean countermeasures
_add("5s-waste-audit", 20,
     "5S Audit Scores and Waste Walk Log",
     "A 5S audit of the four warehouse areas plus the waste walk observations "
     "tagged against the eight DOWNTIME wastes.",
     ["Area", "Sort (1-5)", "Set in Order (1-5)", "Shine (1-5)", "Standardise (1-5)",
      "Sustain (1-5)", "Observation", "DOWNTIME Waste"],
     [["Mezzanine pick face", 2, 2, 3, 2, 1, "Fast movers in bottom-level bins far from despatch", "Motion"],
      ["Ground floor pick face", 3, 3, 3, 3, 2, "Empty bins not flagged until a picker arrives", "Waiting"],
      ["Packing stations", 3, 2, 2, 2, 2, "Orders queue 96 min at peak with 3 of 8 stations idle", "Waiting"],
      ["Despatch lanes", 2, 2, 3, 2, 2, "Staged orders wait 118 min for carrier collection", "Inventory"],
      ["Goods-in", 3, 3, 3, 3, 3, "Putaway backlog builds overnight", "Inventory"],
      ["Returns area", 1, 1, 2, 1, 1, "Returns processed twice — once to bin, once to system", "Extra-processing"],
      ["All areas", 2, 2, 2, 2, 1, "Pickers re-key data from RF into a spreadsheet", "Non-utilised talent"],
      ["All areas", 2, 2, 2, 2, 1, "Re-picks from wrong-bin errors", "Defects"]],
     ["Score each area out of 25. Any area under 15 needs a 5S event before other countermeasures.",
      "For each observation, propose a countermeasure: 5S, Poka-Yoke, pull/JIT, or standard work.",
      "A Poka-Yoke makes the error impossible, obvious or difficult — which of these would stop a wrong-bin pick?"])

# ---- Lab 21 — solution selection
_add("solution-selection-scoring", 21,
     "Solution Selection Matrix and Cost-Benefit Inputs",
     "The shortlisted ideas from Lab 19 with the weighted criteria to score against "
     "and the financial inputs for the cost-benefit analysis.",
     ["Idea ID", "Improvement Idea", "Est. Cost (S$)", "Annual Benefit (S$)",
      "Feasibility (1-5)", "Cost (1-5)", "Impact (1-5)", "Time (1-5)", "Weighted Score"],
     [["I-01", "Dynamic min/max replenishment triggers", 8000, 289000, "", "", "", "", ""],
      ["I-02", "Dedicated night-shift replenisher", 46000, 226000, "", "", "", "", ""],
      ["I-03", "Re-slot top 200 SKUs", 12000, 200000, "", "", "", "", ""],
      ["I-04", "Carrier cut-off countdown on RF scanners", 3500, 174000, "", "", "", "", ""],
      ["I-05", "Move WMS batch job outside shift change", 1200, 115000, "", "", "", "", ""],
      ["I-06", "Standard work + picker certification", 9500, 81000, "", "", "", "", ""],
      ["I-07", "Enforce address validation at checkout", 6000, 67000, "", "", "", "", ""],
      ["I-08", "Second packing station at peak", 38000, 89000, "", "", "", "", ""]],
     ["Criteria weights: Feasibility 25%, Cost 20%, Impact 40%, Time 15%. Score each 1-5, then weight.",
      "Weighted score = (Feas x 0.25) + (Cost x 0.20) + (Impact x 0.40) + (Time x 0.15).",
      "Then calculate payback period = Est. Cost / (Annual Benefit / 12) in months, and rank.",
      "Do the two rankings — weighted score and payback — agree? If not, which do you present and why?"])

# ---- Lab 22 — FMEA / DOE
_add("fmea-worksheet", 22,
     "FMEA Worksheet and DOE Factor Settings",
     "Failure modes for the selected solution, ready to be scored for Severity, "
     "Occurrence and Detection, plus the factors and levels for the DOE.",
     ["Process Step", "Potential Failure Mode", "Potential Effect", "Potential Cause",
      "Current Control", "Sev (1-10)", "Occ (1-10)", "Det (1-10)", "RPN"],
     [["Dynamic replen trigger fires", "Trigger set too low", "Pick face still empties", "Wrong demand window", "None", "", "", "", ""],
      ["Dynamic replen trigger fires", "Trigger set too high", "Excess replen labour", "Over-conservative config", "Weekly report", "", "", "", ""],
      ["Replen task assigned", "No replenisher available on nights", "Task ages, pick face empties", "No dedicated resource", "Supervisor check", "", "", "", ""],
      ["Replen task executed", "Stock put in wrong bin", "Pick error downstream", "No scan verification", "Spot audit", "", "", "", ""],
      ["WMS integration", "Batch job overlaps trigger run", "Triggers not evaluated", "Job scheduling", "None", "", "", "", ""],
      ["Carrier countdown displays", "Scanner out of signal", "Picker misses cut-off", "Mezzanine dead zone", "None", "", "", "", ""]],
     ["RPN = Severity x Occurrence x Detection. Score each 1-10 using the scales in the slides.",
      "Any RPN above 100, or any Severity of 9-10 regardless of RPN, needs a mitigation before go-live.",
      "DOE: factors are Replen Trigger Level (low/high) and Night Replenisher (absent/present).",
      "A 2-factor, 2-level full factorial needs 4 runs. Why vary both together rather than one at a time?"])

_add("doe-pilot-results", 22,
     "DOE Pilot Run Results",
     "The four runs of the 2x2 full factorial pilot, each run for one week, with the "
     "resulting mean lead time and late percentage.",
     ["Run", "Replen Trigger", "Night Replenisher", "Orders in Week",
      "Mean Lead Time (hrs)", "Late Orders", "Late (%)"],
     [[1, "Low (current)", "Absent (current)", 980, 33.1, 83, 8.5],
      [2, "High", "Absent", 975, 29.4, 54, 5.5],
      [3, "Low (current)", "Present", 988, 30.2, 61, 6.2],
      [4, "High", "Present", 991, 26.1, 29, 2.9]],
     ["Calculate the main effect of each factor, then the interaction effect.",
      "Run 4 beats the 3.0% target — but is the improvement more than the sum of the two main effects?",
      "That difference IS the interaction, and it is invisible to one-factor-at-a-time testing."])

# ---- Lab 23 — SPC
def _spc_rows():
    """Post-improvement daily subgroups of 5 for an Xbar-R chart."""
    r = random.Random(SEED + 23)
    out = []
    for d in range(1, 31):
        vals = [round(max(4.0, r.gauss(26.1, 4.2)), 1) for _ in range(5)]
        if d == 19:                      # one deliberate special cause
            vals = [round(v + 15.5, 1) for v in vals]
        out.append([d, (START + timedelta(days=59 + d)).isoformat()] + vals
                   + [round(_mean(vals), 2), round(max(vals) - min(vals), 1)])
    return out


_add("spc-subgroups", 23,
     "Post-Improvement SPC Subgroups",
     "30 days of post-improvement data, 5 orders sampled per day, for the Xbar-R "
     "control chart. One day contains a genuine special cause.",
     ["Day", "Date", "Obs 1", "Obs 2", "Obs 3", "Obs 4", "Obs 5", "Xbar", "Range"],
     _spc_rows(),
     ["Subgroup size n = 5, so use A2 = 0.577, D3 = 0, D4 = 2.114 from the constants table.",
      "CLxbar = mean of Xbars.  UCL = CLxbar + A2*Rbar.  LCL = CLxbar - A2*Rbar.",
      "CLr = Rbar.  UCLr = D4*Rbar.  LCLr = D3*Rbar.",
      "Exactly ONE day signals out of control — find it and say what you would investigate.",
      "Control limits come from the PROCESS. The 48h spec limit comes from the CUSTOMER. Never draw specs on a control chart."])

# ---- Lab 24 — control plan
_add("control-plan-template", 24,
     "Control Plan Template and Monitoring Inputs",
     "The control plan skeleton to complete, with the metrics, owners and reaction "
     "triggers agreed at the Improve tollgate.",
     ["Process Step", "Control Metric", "Spec / Target", "Measurement Method",
      "Sample Size", "Frequency", "Owner", "Reaction Plan"],
     [["Replenishment", "Replen backlog at 06:00", "< 20 tasks", "WMS report", "All", "Daily", "Pick Supervisor", ""],
      ["Picking", "Pick accuracy", "> 99.5%", "Verification scan", "All", "Daily", "Pick Supervisor", ""],
      ["Order fulfilment", "Lead time", "< 48 hrs", "OMS/WMS derived", "n=5", "Daily (Xbar-R)", "Distribution Manager", ""],
      ["Order fulfilment", "Late deliveries", "< 3.0%", "OMS report", "All", "Weekly", "Distribution Manager", ""],
      ["Carrier handover", "Cut-off compliance", "100%", "Carrier portal", "All", "Daily", "Despatch Lead", ""],
      ["WMS", "Unplanned downtime", "< 30 min/wk", "IT incident log", "All", "Weekly", "WMS Analyst", ""]],
     ["Complete the Reaction Plan column: exactly WHO does WHAT when the metric breaches.",
      "A control plan with no named owner and no reaction plan is a wish, not a control.",
      "Decide which metrics belong on the visual management board and at what frequency."])

# ---- Lab 25 — verify the gain
_add("before-after-verification", 25,
     "Before and After Verification Data",
     "The baseline month against the post-improvement month, for the verification "
     "hypothesis test, the recalculated capability and the A3 storyboard.",
     ["Metric", "Baseline (June 2026)", "Post-Improvement (Sept 2026)", "Target"],
     [["Orders shipped", TOTAL_ORDERS, 4310, "-"],
      ["Late orders", LATE_ORDERS, 127, "-"],
      ["Late deliveries (%)", 8.5, 2.9, 3.0],
      ["Mean lead time (hrs)", round(BASE_MEAN, 1), 26.1, "-"],
      ["Std deviation (hrs)", round(BASE_SD, 1), 4.2, "-"],
      ["Cp", round((CTQ_HOURS - 0) / (6 * BASE_SD), 2), 1.90, "-"],
      ["Cpk", round((CTQ_HOURS - BASE_MEAN) / (3 * BASE_SD), 2), 1.74, ">= 1.33"],
      ["DPMO", round(LATE_ORDERS / TOTAL_ORDERS * 1e6), 29466, "-"],
      ["Sigma level", 2.9, 3.4, "-"],
      ["Annualised COPQ (S$)", 1674000, 571000, "-"]],
     ["Run a hypothesis test on before vs after — did the improvement actually hold, or is it noise?",
      "Recalculate Cp and Cpk and compare against the baseline. Which improved more, spread or centring?",
      "Annualised benefit = baseline COPQ - post COPQ. State it on the A3 and get Finance to validate it.",
      "Build the A3 on one page: background, current state, goal, analysis, countermeasures, results, follow-up."])


# ------------------------------------------------------------------ helpers
def for_lab(n):
    """All datasets owned by lab n, in stable order."""
    return [d for d in DATASETS.values() if d["lab"] == n]


def filename(ds, ext="xlsx"):
    return f"lab{ds['lab']:02d}-{ds['key']}.{ext}"


if __name__ == "__main__":
    tot = sum(len(d["rows"]) for d in DATASETS.values())
    print(f"{len(DATASETS)} datasets, {tot} data rows")
    print(f"orders={len(ORDERS)} late={len(_LATE)} "
          f"mean={BASE_MEAN:.2f} sd={BASE_SD:.2f} "
          f"Cp={(CTQ_HOURS)/(6*BASE_SD):.2f} "
          f"Cpk={(CTQ_HOURS-BASE_MEAN)/(3*BASE_SD):.2f}")
    for n in range(1, 26):
        ds = for_lab(n)
        print(f"  Lab {n:2d}: " + (", ".join(d["key"] for d in ds) or "-"))
