# 📊 Growth Metrics Dashboard — FinTech App (Jar-Inspired)

An end-to-end Growth/Product Analytics project simulating the measurement layer a Growth PM would build in their first 90 days at a consumer fintech startup — from raw user data to a live, filterable Power BI dashboard and a prioritized growth experiment backlog.

**Built with:** Power BI · SQL · Python · DAX

---

## 🖼️ Dashboard Preview

![Zone 1 - Overview](https://github.com/JAIKISHORE-D/growth-metrics-dashboard-jar/blob/main/zone1.png)
![Zone 2 - Acquisition & Funnel](https://github.com/JAIKISHORE-D/growth-metrics-dashboard-jar/blob/main/zone2.png)
![Zone 3 - Engagement & Retention](https://github.com/JAIKISHORE-D/growth-metrics-dashboard-jar/blob/main/zone3.png)
![Zone 4 - Monetization](https://github.com/JAIKISHORE-D/growth-metrics-dashboard-jar/blob/main/zone4.png)

---

## 🎯 The Problem

A fintech app helps users build a savings habit through small recurring investments. Leadership can't currently answer three questions:

1. Are new users actually **activating** (completing KYC) and **converting** (making a first investment) — or just signing up and disappearing?
2. Which **acquisition channels** bring good users, and which just inflate signup numbers?
3. Is the business **retaining and monetizing** users well enough to justify what it's spending to acquire them?

This project builds the dashboard and analysis needed to answer all three.

---

## 📁 What's in This Repo

| File | What it is |
|---|---|
| `data/jar_growth_dataset.csv` | 12,500-row synthetic user dataset (signup date, channel, KYC status, investment, revenue, churn, etc.) |
| `sql/kpi_queries.sql` | All 15 KPIs written and validated as SQL |
| `scripts/generate_dataset.py` | Python script that generated the dataset, with realistic built-in behavior patterns |
| `dashboard/dax_measures.txt` | Power BI DAX formulas for every KPI |
| `dashboard/growth_dashboard.pbix` | The Power BI dashboard file |
| `README.md` | This file |

---

## 📈 The 15 KPIs (Real Numbers From This Dataset)

| KPI | Value |
|---|---|
| Total Users | 12,500 |
| Activation Rate (completed KYC) | **57.3%** |
| Conversion Rate (made first investment) | **28.1%** |
| KYC Completion Rate | 69.6% |
| First Investment Rate (of KYC-verified users) | 49.0% |
| Retention Rate (30-day) | **60.1%** |
| Churn Rate | 39.9% |
| ARPU (avg. revenue per user) | ₹27.97 |
| ARPPU (avg. revenue per *paying* user) | ₹90.68 |
| Estimated LTV | ₹88 |
| CAC (cheapest → most expensive channel) | ₹674 → ₹8,922 |
| Referral Rate | 13.6% |

Full formulas for every KPI (SQL + DAX) are in `sql/kpi_queries.sql` and `dashboard/dax_measures.txt`.

---

## 🔍 Top Insights

1. **Activation, not signup, is the biggest leak.** Only 57.3% of users complete KYC — the single largest drop-off in the funnel.
2. **Referral is the best-performing channel by far**: 38.2% conversion vs. 17.1% for Paid Social — more than 2x — yet it's only 18% of signups.
3. **Paid Social has the worst unit economics**: lowest conversion *and* highest CAC (₹8,922) of any channel — a 13x gap versus Organic (₹674).
4. **Referred users retain better** (69.2% vs. 60.1% platform average), so referral isn't just cheaper acquisition — it's higher-quality too.
5. **Engagement has a "habit threshold"**: users with 40+ sessions retain at 72.3%, vs. ~54% for under 15 sessions — retention jumps sharply once users cross that line.

*(Full list of 15 insights and the 20-item growth experiment backlog are in the project write-up below.)*

---

## 🖥️ Dashboard Structure

The dashboard is built as 4 pages, one per "zone," with 6 synced filters (Date Range, Acquisition Channel, City Tier, Device, Age Group, KYC Status) that filter all pages at once:

- **Zone 1 — Overview:** Top-line KPI cards (Total Users, MAU, Activation, Conversion, Retention, ARPU)
- **Zone 2 — Acquisition & Funnel:** Signup → KYC → Investment funnel, channel breakdown table, KYC status pie chart
- **Zone 3 — Engagement & Retention:** New user trend, churn rate by channel and device
- **Zone 4 — Monetization:** ARPPU, Estimated LTV, and the **LTV vs. CAC by channel** chart — the single most important visual, showing which channels are actually profitable

---

## 🛠️ How to Use This Project

1. **Explore the dataset:** open `data/jar_growth_dataset.csv` in Excel or Google Sheets
2. **Run the SQL:** load the CSV into any SQL database (or SQLite) and run `sql/kpi_queries.sql`
3. **Open the dashboard:** open `dashboard/growth_dashboard.pbix` in Power BI Desktop (free download from Microsoft)
4. **Regenerate the data:** `python scripts/generate_dataset.py` (requires `pandas`, `numpy`)

---

## 💡 Why This Project

This mirrors real early-stage Growth work: start from a business question (not a dataset), define KPIs that require judgment calls (e.g., which denominator to use for which rate), approximate missing data honestly (marketing spend isn't in a product database — CAC is modeled from assumed channel budgets, documented in the SQL file), and turn findings into a prioritized action plan rather than stopping at "here are some charts."

---

## 📌 About This Project

Built as a portfolio project for Growth/Product Management internship applications — designed to demonstrate product thinking, SQL/DAX skills, and the ability to turn data into business decisions, not just visualizations.

**Tech stack:** Power BI · SQL (SQLite-compatible) · Python (pandas, numpy) · DAX

---
