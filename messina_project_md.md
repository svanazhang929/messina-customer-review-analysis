# Gelato Messina — Customer Review Analysis
## Project Documentation

**Author:** Yuxin Zhang  
**Date:** Dec 2023 – Mar 2026 (data period) · May 2026 (published)  
**Status:** Complete

---

## 1. Project Overview

An end-to-end customer review analysis built to identify what drives store-level rating differences across Gelato Messina's 20 Sydney locations. The project combines web scraping, AI-powered NLP classification, and regression modelling to surface actionable operational insights for management.

**Central question:** Why do some Messina stores consistently outperform others — and what would it take to close the gap?

---

## 2. Business Problem

Gelato Messina maintains a strong overall brand reputation with a network average of 4.52★ across 20 Sydney stores. However, store-level performance varies significantly — with a gap of over one full star between top and bottom performers. This gap represents a reputational risk that is not visible from brand-level metrics alone.

**Key finding:** The problem is not brand-wide. It is store-specific and operationally fixable.

---

## 3. Technical Stack

| Tool | Purpose |
|------|---------|
| **Apify** | Web scraping — Google Maps reviews |
| **Claude API** | NLP text classification and sentiment labelling |
| **Power BI** | Data modelling, DAX measures, visualisation |
| **DAX** | Calculated columns, measures, regression metrics |
| **Linear regression** | Projected rating improvement modelling |
| **Pearson correlation** | Identifying rating drivers by category |

---

## 4. Data Pipeline

### Step 1 — Data Collection (Apify)
- Scraped Google Maps reviews across all 20 Sydney Messina locations
- Each store sampled at up to 100 most recent reviews
- Fields captured: review text, star rating, reviewer name, timestamp
- Date range: Dec 2023 – Mar 2026
- Raw sample: ~2,000 records before cleaning

### Step 2 — Data Cleaning
- Filtered out star-only ratings with no text content
- Removed non-substantive responses and irrelevant entries
- Final cleaned dataset: **1,278 reviews** across 20 stores

### Step 3 — NLP Classification (Claude API)
- Each review sent through Claude API with a custom classification prompt
- Tagged against 6 sentiment categories:
  - Service
  - Product Quality
  - Flavour Variety
  - Wait Time
  - Store Environment
  - Price & Value
- Each tag assigned a sentiment label: Positive / Negative / Neutral
- Output: structured dataset with category and sentiment per review

### Step 4 — Modelling (Power BI + DAX)
- Built store-level metrics using DAX:
  - Negative Rate % per category per store
  - Positive Rate % per store
  - Total review volume per store
  - Avg Rating (recalculated from sample)
- Ran Pearson correlation between category negative rates and store avg rating
- Applied linear regression: Avg Rating ~ Negative Rate %
  - R² = 0.86 (model explains 86% of rating variance)
  - Used regression coefficients to project rating improvements

---

## 5. Analytical Framework

Three-layer structure:

| Layer | Question | Dashboard |
|-------|---------|-----------|
| **Descriptive** | What are customers talking about? | Dashboard 1 — Store Overview |
| **Correlational** | What drives store ratings? | Dashboard 2 — What drives rating? |
| **Predictive** | What if we fix the biggest problem? | Dashboard 3 — The scoop on what needs to change |

---

## 6. Key Findings

### Finding 1 — Store performance is highly uneven
- Rating range: 3.59★ (Randwick) to 4.64★ (Circular Quay / Newtown)
- Top performers: Cronulla (11.4% neg), Miranda (9.1% neg), Bondi (9.7% neg)
- Underperformers: Randwick (36.4% neg), Parramatta (34.7% neg), Marrickville (30.0% neg)

### Finding 2 — Service is the single biggest rating driver
- Service: r = −0.82 (strongest negative correlation)
- Wait Time: r = −0.65
- Price & Value: r = −0.48
- Store Environment: r = −0.30
- Product Quality: r = +0.35 (asset)
- Flavour Variety: r = +0.41 (asset)

### Finding 3 — The problem is concentrated in 3 stores
- Parramatta: 13 service complaints (highest in network)
- Randwick: 11 service complaints
- Both 2–3× higher than network average

### Finding 4 — The solution already exists within the network
- Miranda and Cronulla operate at target service levels
- Internal best practice transfer is the recommended path

---

## 7. Scenario Modelling

If Randwick, Parramatta and Marrickville reduce service negative rate to brand average (20%):

| Store | Current Rating | Current Neg Rate | Projected Rating | Gain |
|-------|---------------|-----------------|-----------------|------|
| Randwick | 3.59★ | 36.4% | 4.30★ | +0.71★ |
| Parramatta | 3.84★ | 34.7% | 4.30★ | +0.46★ |
| Marrickville | 3.97★ | 30.0% | 4.30★ | +0.34★ |

**No product changes, no capital investment, no price adjustments required.**

---

## 8. Priority Action Matrix

| Quadrant | Actions |
|----------|---------|
| **Fix First** (high impact, actionable) | Service quality, staff training, problem resolution, consistency |
| **Plan For** (high impact, operational) | Wait time, queue management, peak hour staffing, order flow |
| **Maintain** (brand strength) | Flavour variety, seasonal innovation, limited editions |
| **Monitor** (lower priority) | Price & value perception, loyalty offers |

---

## 9. Limitations & Caveats

- Store ratings are recalculated from sampled reviews, not live Google Maps scores — may differ from published ratings
- Sample size limited to ~100 reviews per store; stores with fewer reviews may show higher variance
- Regression based on 20 data points (store locations) — projections are directional estimates, not precise forecasts
- Longitudinal tracking post-intervention would be needed to validate the model
- Messina's overall brand reputation remains strong; this analysis surfaces operational differences between locations, not brand-level problems

---

## 10. Deliverables

| Deliverable | Format | Status |
|------------|--------|--------|
| Power BI Dashboard (4 pages) | .pbix / .pbit | Complete |
| LinkedIn Article | Published | Complete |
| Project documentation | .md | Complete |

---

## 11. Dashboard Pages

| Page | Title | Content |
|------|-------|---------|
| Cover | What actually drives Messina's ratings? | KPI strip, correlation chart, scatter plot, store snapshot table |
| Page 1 | Are all Messina stores created equal? | Store performance table, ArcGIS map, Key Insight |
| Page 2 | What's actually pulling Messina's ratings down? | Bubble chart, correlation bar chart, negative mentions heatmap |
| Page 3 | The scoop on what needs to change | KPI cards, priority action matrix, scenario table |

---

## 12. Skills Demonstrated

- End-to-end data pipeline (scraping → cleaning → classification → modelling → visualisation)
- API integration (Apify, Claude API)
- NLP / text classification
- Statistical analysis (Pearson correlation, linear regression)
- Power BI dashboard design
- DAX measure development
- Data storytelling and business communication
- Scenario modelling for operational decision-making
EOF