# Alcohol Retail & Tavern Performance Intelligence (Purchase Frequency + CLTV)

This portfolio project models **repeat purchasing, customer value, and commercial performance** across a South African-style alcohol route-to-market:

- **Wholesalers → Taverns (on-trade) / Retailers (off-trade)**
- Product mix (beer / cider / spirits / RTDs)
- Weekend spikes, seasonality, promotions, and supply constraints
- A practical **Purchase Frequency + CLTV** workflow recruiters can scan quickly

> **Note:** The dataset is **synthetic** (no real customer data). It is designed to look and behave like real commercial sales data.

---

## Why this project exists

Many portfolios stop at “EDA + a model”. This repo shows **business intelligence that a commercial team can use**:

- Who buys repeatedly?
- Which outlets drive the most value?
- What does “weekend economy” do to volume and revenue?
- Where should reps focus (coverage, frequency, promotions)?

---

## What you’ll find in this repo

**Data**
- `data/raw/transactions_raw.csv` – generated transactional sales (line-level)
- `data/processed/outlet_monthly_kpis.csv` – outlet KPIs (frequency, AOV, revenue, etc.)
- `data/processed/outlet_cltv_segments.csv` – segments and CLTV scores

**Code**
- `scripts/01_generate_synthetic_data.py` – creates raw dataset + data dictionary
- `scripts/02_build_kpis_and_cltv.py` – builds KPIs, segments, and exports processed tables
- `scripts/03_generate_report.py` – generates a clean Markdown report + figures

**SQL (optional)**
- `sql/schema.sql` – example star schema for analytics / BI

**Report**
- `reports/report.md` + `reports/figures/`

---

## Quickstart

### 1) Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run the pipeline
```bash
python scripts/01_generate_synthetic_data.py
python scripts/02_build_kpis_and_cltv.py
python scripts/03_generate_report.py
```

### 4) Open the report
- `reports/report.md`

---

## Outputs (what a recruiter should notice)

- **Purchase Frequency**: weekly repeat patterns by outlet type (taverns vs retailers)
- **CLTV**: a pragmatic CLTV score (not over-engineered) and segments:
  - **Cash Cows** (high frequency, high value)
  - **Weekend Kings/Queens** (weekend heavy, promotion sensitive)
  - **Occasional Big Spenders** (low frequency, high AOV)
  - **At-Risk / Low Value** (low activity)

---

## Data dictionary

The generator writes a dictionary to:
- `docs/data_dictionary.json`

---

## Portfolio framing (copy/paste for your site)

**Project name:** Alcohol Retail & Tavern Performance Intelligence (Purchase Frequency + CLTV)  
**Description:** Built a synthetic route-to-market dataset to analyse purchase frequency, outlet KPIs, and CLTV segments for taverns, retailers, and wholesalers. Produced an automated Markdown insight report with business-ready visuals.  
**Skills:** Python, Pandas, Data Cleaning, EDA, KPI Design, Segmentation, CLTV, Data Storytelling, Matplotlib  
**Links:** GitHub repo + report screenshots

---

## Author
Kabelo (portfolio project)
