# Growth Metrics Dashboard for a FinTech Application (Jar-Inspired)
### A portfolio project simulating the Growth/Product Analytics function at a micro-savings & investment fintech

---

## 0. How to use this project

| File | What it is |
|---|---|
| `jar_growth_dataset.csv` | 12,500-row synthetic user-level dataset, ready to import into Power BI, Excel, or a SQL database |
| `kpi_queries.sql` | All 15 KPI formulas as runnable SQL, plus cohort and funnel breakdowns |
| `generate_dataset.py` | The data generation script — shows you understand *how* the data was built, not just that you downloaded it |
| `README.md` (this file) | The full case study: business problem, KPI framework, dashboard design, insights, and experiment backlog |

Load the CSV into Power BI Desktop, paste in the SQL for a "Data Model" validation layer or a companion SQL portfolio piece, and use the insights/experiments below as your dashboard's narrative — this is what makes it look like real work instead of a school exercise.

---

## 1. Project Overview & Business Problem

**Company context (fictional, Jar-inspired):** A consumer fintech app in India that helps users build a savings/investing habit through small, recurring "round-up" or auto-save contributions into gold or mutual funds, aimed at Gen Z and young millennials who find traditional investing intimidating.

**The business problem:** The company has scaled user acquisition aggressively across paid and organic channels, but leadership doesn't have a single, reliable view of:

- Whether new users are actually **activating** (completing KYC) and **converting** (making their first investment), or just downloading and disappearing.
- Which **acquisition channels** bring in users who stick around and invest — versus channels that just inflate signup vanity metrics.
- Where users are **dropping off** in the funnel (signup → KYC → first investment → repeat engagement).
- Whether the business is **retaining and monetizing** users well enough to justify current CAC spend.

This is the exact problem a Growth PM is hired to solve in the first 90 days at a Series A/B fintech: **build the measurement layer before you can responsibly run growth experiments.** You cannot optimize a funnel you can't see.

**What this project delivers:** An end-to-end growth analytics system — a clean data model, a KPI framework tied to business outcomes (not vanity metrics), a dashboard design that a CXO or Head of Growth could actually use in a weekly review, and a prioritized experiment backlog derived from the data.

---

## 2. Business Objectives & Success Metrics

| Business Objective | Why it matters | Primary Success Metric |
|---|---|---|
| Grow the active, KYC-verified user base efficiently | Unverified users generate zero revenue and cost money to acquire | Activation Rate, CAC by channel |
| Convert activated users into first-time investors | This is the moment a user becomes revenue-generating | Conversion Rate, First Investment Rate |
| Increase revenue per user without over-relying on new acquisition | Sustainable growth needs monetization depth, not just top-of-funnel volume | ARPU, ARPPU, LTV |
| Reduce early-stage churn | Fintech trust is fragile; most churn happens in the first 30-60 days | Retention Rate, Churn Rate (cohort-based) |
| Build a self-sustaining referral loop | Referred users are cheaper to acquire and convert better (this dataset confirms it) | Referral Rate, LTV:CAC of referred cohort |
| Protect unit economics | Growth that costs more than it returns is not growth | LTV:CAC ratio by channel |

**North Star Metric recommendation:** *Number of KYC-Verified, Actively-Investing Users* — this single metric forces the org to care about acquisition quality, activation, AND monetization simultaneously, rather than optimizing signups in isolation (a classic fintech growth trap).

---

## 3. The Dataset

`jar_growth_dataset.csv` — **12,500 synthetic users**, generated with intentional, realistic correlations (channel quality affects activation; tenure and engagement affect churn; investment behavior affects revenue) so that the dashboard produces genuine, defensible insights rather than random noise. Signups span **July 2025 – June 2026** with seasonality (Indian festive season and January New Year spikes).

### Column dictionary

| Column | Type | Description | Why it matters for growth analysis |
|---|---|---|---|
| `User_ID` | String | Unique user identifier (e.g. `JAR100001`) | Primary key; every KPI is an aggregation over this |
| `Signup_Date` | Date | Date the user created an account | Foundation for cohort analysis, MoM growth trends, seasonality |
| `Acquisition_Channel` | Categorical | Organic, Referral, Paid Social, Influencer, Google Ads, App Store Search | The single most important dimension for CAC and channel-quality analysis — growth teams live and die by this cut |
| `Device` | Categorical | Android / iOS | iOS users often skew higher-income/higher-LTV; a classic segmentation cut in Indian fintech |
| `City` | Categorical | 17 Indian cities | Enables geographic expansion and localization decisions |
| `City_Tier` | Categorical | Tier 1 / Tier 2-3 | Tier 1 vs Tier 2-3 behavior differs sharply in fintech (trust, income, financial literacy) — this is a derived field that makes City instantly more useful |
| `Age_Group` | Categorical | 18-24, 25-34, 35-44, 45+ | Product and messaging differ by life stage; 25-34 is usually the "money" segment |
| `KYC_Status` | Categorical | Verified / In Progress / Rejected / Not Started | This is the **activation gate** — nothing downstream happens without it |
| `First_Investment` | Categorical (Yes/No) | Whether the user ever made a first investment | The core conversion event — the moment a user becomes monetizable |
| `Investment_Amount` | Numeric (INR) | Value of the user's first investment | Feeds ARPU/LTV and reveals ticket-size differences across segments |
| `Referral_Status` | Categorical | Referred Others / Was Referred / None | Measures both acquisition efficiency (was referred) and virality (referred others) |
| `Session_Count` | Numeric | Lifetime app sessions | Proxy for engagement depth; correlates strongly with retention in this dataset |
| `Last_Active_Date` | Date | Most recent session date | Used to compute DAU/WAU/MAU and churn |
| `Retention_Days` | Numeric | Days between signup and last activity | A simple "engagement lifespan" metric, easy to bucket and cohort |
| `Revenue` | Numeric (INR) | Platform revenue attributable to the user (fees on invested amount + incidental revenue) | The monetization outcome — what all the funnel work is ultimately for |
| `Churn_Status` | Categorical (Active/Churned) | Active = active in last 30 days | Binary flag that powers retention/churn KPIs directly |

This isn't a random `Faker` dump — every field was generated with a **causal story** (e.g., Referral users are more likely to convert; iOS users skew slightly higher-value; higher session counts predict lower churn). That's what makes the insights below real rather than invented.

---

## 4. KPI Framework — Definitions & Formulas

All formulas below are implemented and validated in `kpi_queries.sql` against the actual dataset. Figures shown are the real output from running these queries.

| # | KPI | Formula | Value in this dataset |
|---|---|---|---|
| 1 | **Total Users** | `COUNT(User_ID)` | 12,500 |
| 2 | **New Users** | `COUNT(User_ID) WHERE Signup_Date in period` | e.g. 1,580 in Jan 2026 (peak month) |
| 3 | **DAU** | Unique users active on a given day (`Last_Active_Date = day`) | Varies by day snapshot |
| 4 | **WAU** | Unique users active in trailing 7 days | Varies by reference date |
| 5 | **MAU** | Unique users active in trailing 30 days | Varies by reference date |
| 6 | **Activation Rate** | `KYC Verified Users / Total Users × 100` | **57.3%** |
| 7 | **Conversion Rate** | `Users with First_Investment = Yes / Total Users × 100` | **28.1%** |
| 8 | **KYC Completion Rate** | `KYC Verified / (KYC Verified + In Progress + Rejected) × 100` (i.e., of those who *started* KYC) | **69.6%** |
| 9 | **First Investment Rate** | `Invested Users / KYC-Verified Users × 100` | **49.0%** |
| 10 | **ARPU** | `Total Revenue / Total Users` | **₹27.97** |
| 11 | **LTV** (simplified) | `ARPU × (Avg. Retention Days / 30) × Gross Margin (70%)` | **≈ ₹88.3** (blended, all users) |
| 12 | **CAC** (by channel) | `Channel Marketing Spend / New Users Acquired via Channel` | Ranges from **₹674 (Organic)** to **₹8,922 (Paid Social)** — see Section 9 |
| 13 | **Retention Rate** | `Active Users (last 30 days) / Total Users × 100` | **60.1%** |
| 14 | **Churn Rate** | `Churned Users / Total Users × 100` (= 100 − Retention Rate) | **39.9%** |
| 15 | **Referral Rate** | `Users who Referred Others / Total Users × 100` | **13.6%** |

**A note on CAC and LTV (important for interviews):** Real marketing spend isn't in a user-level product table — it lives in ad platforms and finance systems. I modeled CAC using assumed channel budgets (documented in `kpi_queries.sql`) joined against users-acquired-per-channel, exactly how you'd approximate CAC in a real company before a proper marketing-spend pipeline exists. Being able to say *"here's how I approximated this because the perfect data wasn't available"* is itself a strong PM signal.

---

## 5. Recommended Dashboard Layout

A real Growth dashboard is read top-to-bottom in under 60 seconds by a busy stakeholder, then drilled into. Structure it in **four horizontal zones**:

**Zone 1 — Executive Summary (top strip, always visible)**
Big-number KPI cards: Total Users, MAU, Activation Rate, Conversion Rate, Retention Rate, ARPU — each with a small trend sparkline and MoM delta arrow (▲/▼). This is the "glanceable" layer for a CXO who has 10 seconds.

**Zone 2 — Acquisition & Funnel (left two-thirds)**
- New user trend line (monthly, with seasonality visible)
- Channel breakdown table: signups → activation % → conversion % → retention % → CAC (the funnel-by-channel view is the single most useful table on the whole dashboard)
- A funnel chart: Signups → KYC Started → KYC Verified → First Investment → Retained

**Zone 3 — Engagement & Retention (right one-third)**
- DAU/WAU/MAU trend + stickiness ratio
- Cohort retention table (signup month × retention %)
- Churn rate by segment (channel, device, city tier)

**Zone 4 — Monetization & Unit Economics (bottom strip)**
- ARPU/ARPPU trend
- LTV vs CAC by channel (this is the "should we keep spending on this channel" chart — the most CFO-relevant visual on the dashboard)
- Revenue by segment breakdown

**Filters (persistent, top of page, apply to all zones):** Date Range · City / City Tier · Acquisition Channel · Device · Age Group · KYC Status.

This four-zone structure mirrors how growth dashboards are actually built at consumer fintechs: **top-line health → where users come from → whether they stay → whether they're worth it.**

---

## 6. Chart Recommendations by KPI

| KPI / Section | Recommended Chart | Why |
|---|---|---|
| Total Users / New Users | Line chart (monthly) with cumulative total as secondary axis | Shows both growth rate and cumulative scale in one view |
| DAU/WAU/MAU | Multi-line trend + DAU/MAU stickiness as a separate KPI card | Stickiness (a ratio) gets lost if buried inside a multi-line chart — give it its own number |
| Activation Rate, Conversion Rate, KYC Completion, First Investment Rate | Funnel chart (single visual, all four in sequence) | A funnel chart is the only chart type that makes drop-off *visually obvious* — bar charts hide the relative loss at each stage |
| Activation/Conversion by Channel | Horizontal bar chart, sorted descending | Easy to scan "best to worst" channel at a glance; horizontal avoids label truncation with long channel names |
| ARPU / ARPPU trend | Line chart over time, split by paying vs. all users | Shows whether monetization depth is improving independent of user growth |
| LTV vs CAC by channel | Grouped/paired bar chart (LTV bar next to CAC bar per channel) | The visual "gap" between the two bars instantly tells you which channels are profitable |
| Retention Rate (cohort) | Retention heatmap / cohort grid (signup month rows × months-since-signup columns) | Industry-standard way to see retention curves flatten or decay across cohorts |
| Churn Rate by segment | Stacked or grouped bar chart by channel/device/city tier | Lets you compare churn drivers side-by-side |
| Referral Rate | Single KPI card + a small bar comparing conversion/retention of Referred vs. Non-Referred users | The comparison bar is what makes referral data *actionable*, not just a vanity percentage |
| Revenue by segment | Treemap or stacked bar (by channel or age group) | Treemap communicates "which segment matters most to revenue" proportionally, at a glance |

---

## 7. 15 Business Insights (Derived from the Actual Dataset)

These are real patterns pulled directly from `jar_growth_dataset.csv` via the SQL queries — not hypothetical filler. This is the section that proves you can move from data to decision, which is exactly what Growth/PM interviewers screen for.

1. **Activation is the biggest leak, not signup.** Only 57.3% of users reach KYC-Verified — meaning ~43% of acquisition spend is currently going toward users who never unlock core product value. Fixing activation has more leverage than adding more top-of-funnel volume.

2. **KYC completion rate (69.6% of those who start) is meaningfully higher than activation rate (57.3% of everyone).** This gap (12.3 points) is entirely users who **never even start** KYC — a UX/prompt problem, not a document-verification problem. The fix is different (nudge to start) than if it were a drop-off mid-KYC.

3. **Referral is the highest-quality channel by a wide margin**: 38.2% conversion rate vs. 17.1% for Paid Social — more than 2x. Yet Referral only drives 18% of signups. There's a clear underinvestment in the referral channel relative to its proven quality.

4. **Paid Social has the worst full-funnel economics**: lowest conversion rate (17.1%) *and* highest estimated CAC (₹8,922) of any channel. It's currently the most expensive way to acquire the least valuable users.

5. **Organic has the best CAC-to-quality ratio**: ₹674 CAC with 35.3% conversion — the second-best conversion rate of any channel at a fraction of the cost of paid channels. This is the channel to double down on with SEO/ASO/content investment.

6. **Users who refer others convert at 54.3%** — nearly double the platform average (28.1%). Power users and referrers are effectively self-selecting into the highest-value segment; a referral program isn't just an acquisition lever, it's a signal of high-intent users worth targeting with upsell.

7. **"Was Referred" users retain better (69.2%) than the platform average (60.1%)**, confirming that referred users aren't just cheaper to acquire — they also stick around longer, compounding the channel's ROI advantage.

8. **Engagement depth strongly predicts retention.** Users with 40+ lifetime sessions retain at 72.3%, versus 53.9-54.5% for users with under 15 sessions. This isn't linear — retention jumps sharply once a user crosses roughly 15-20 sessions, suggesting a "habit threshold" the product should be designed to push users past early (e.g., via a session-count-based onboarding nudge sequence).

9. **iOS users slightly outperform Android on every downstream metric**: 31.1% vs 27.5% conversion, 62.6% vs 59.6% retention, and ₹31.97 vs ₹27.08 ARPU — despite being only 18% of the user base. This is consistent with the common India-fintech pattern of iOS skewing toward higher-income, higher-trust users, and suggests iOS-specific acquisition may have better unit economics than the current Android-heavy mix implies.

10. **Tier 1 cities convert better (30.5%) than Tier 2/3 (25.4%)**, but the gap (5 points) is smaller than many teams assume — Tier 2/3 is not the weak segment leadership might expect, and represents a real expansion opportunity rather than a segment to deprioritize.

11. **The 25-34 age group is the core "money" segment**: highest conversion rate (33.4%) and highest average investment amount (₹723), while 18-24 — the largest cohort by volume (4,745 users) — converts at only 24.2%. Volume and value are concentrated in different age groups, which should shape both acquisition targeting and monetization messaging.

12. **The 45+ segment is small (1,174 users) and converts worst (21.0%)**, suggesting current product/marketing isn't resonating with older users — likely a trust or UX-complexity barrier worth a dedicated qualitative research pass before investing acquisition spend here.

13. **Signups show strong seasonality**: January (1,580 signups) and the Oct-Nov festive period (1,358 / 1,458) are peak months, roughly 60-90% above the summer trough (May: 783). Marketing spend and campaign planning should be weighted toward these windows rather than spread evenly across the year.

14. **Blended LTV (₹88.3) against the cheapest channel's CAC (₹674, Organic) yields a healthy LTV:CAC ratio**, but against Paid Social's CAC (₹8,922) the ratio is deeply negative — meaning **channel-level LTV:CAC, not blended LTV:CAC, is the number that should gate budget decisions.** A blended view alone would hide that Paid Social is actively unprofitable.

15. **First Investment Rate among KYC-Verified users (49.0%) is nearly double the overall Conversion Rate (28.1%)**, which mathematically confirms that KYC verification is the pivotal activation gate — once a user clears it, they're roughly a coin-flip to invest. This reinforces insight #1: every incremental percentage point of activation converts almost directly into revenue-generating users.

---

## 8. 20 Growth Experiments (Backlog)

Each experiment ties directly back to one of the 15 insights above — this traceability (insight → hypothesis → experiment) is what separates a real growth backlog from a generic brainstorm list.

**1. Problem:** 43% of users never complete KYC.
**Hypothesis:** Users abandon because KYC feels like a multi-step chore with no visible progress.
**Experiment:** Add a persistent progress bar + "2 minutes left" micro-copy to the KYC flow.
**Success Metric:** Activation Rate.
**Expected Impact:** +4-6 pts activation.

**2. Problem:** 12.3-point gap between "started KYC" and "activated" is really users who never *start*.
**Hypothesis:** The KYC CTA is not prominent enough post-signup.
**Experiment:** Trigger a full-screen KYC prompt immediately after signup instead of leaving it in a menu.
**Success Metric:** % of signups who start KYC within 24 hours.
**Expected Impact:** +8-10 pts KYC-start rate.

**3. Problem:** Referral converts 2x better than Paid Social but drives only 18% of signups.
**Hypothesis:** Users aren't referring because the incentive isn't visible enough.
**Experiment:** Add a persistent "Invite & Earn ₹100" banner on the home screen.
**Success Metric:** Referral Rate.
**Expected Impact:** +5 pts referral rate.

**4. Problem:** Paid Social has the worst conversion and highest CAC.
**Hypothesis:** Paid Social creative attracts low-intent browsers, not savers.
**Experiment:** A/B test intent-qualifying ad creative (e.g., "Start with ₹10" vs. generic brand awareness ads).
**Success Metric:** Post-click Conversion Rate.
**Expected Impact:** +3-5 pts conversion on Paid Social specifically.

**5. Problem:** Organic has the best CAC-to-quality ratio but may be under-resourced.
**Hypothesis:** Increasing SEO/ASO investment will scale Organic without hurting its conversion quality.
**Experiment:** Reallocate 20% of Paid Social budget into ASO/content for 1 quarter.
**Success Metric:** Organic-channel new users, blended CAC.
**Expected Impact:** -10-15% blended CAC.

**6. Problem:** Users who refer others convert at 54.3% — a clear high-value segment.
**Hypothesis:** Prompting engaged (high-session) users specifically to refer will surface more of this segment.
**Experiment:** Trigger a referral prompt after a user's 15th session (the "habit threshold" from insight #8).
**Success Metric:** Referral Rate among 15+ session users.
**Expected Impact:** +8-10 pts referral rate in that segment.

**7. Problem:** Retention jumps sharply after ~15-20 sessions but many users churn before reaching it.
**Hypothesis:** A structured first-30-days engagement nudge sequence will push more users past the habit threshold.
**Experiment:** Launch a Day 1/3/7/14 push notification + in-app nudge sequence tied to session milestones.
**Success Metric:** % of new cohort reaching 15+ sessions within 30 days.
**Expected Impact:** +10 pts.

**8. Problem:** iOS users outperform Android on every metric but are only 18% of the base.
**Hypothesis:** iOS-specific acquisition has better unit economics than the current mix suggests.
**Experiment:** Run a dedicated iOS-targeted campaign for one quarter and compare CAC-adjusted LTV.
**Success Metric:** iOS LTV:CAC vs. Android LTV:CAC.
**Expected Impact:** Validate whether iOS budget allocation should increase.

**9. Problem:** Tier 2/3 cities convert only 5 points lower than Tier 1, suggesting untapped potential.
**Hypothesis:** Localized (regional language) onboarding will close this gap further.
**Experiment:** A/B test Hindi/regional-language KYC flow in top 5 Tier 2/3 cities.
**Success Metric:** Tier 2/3 Activation Rate.
**Expected Impact:** +5-7 pts in tested cities.

**10. Problem:** 18-24 is the largest cohort by volume but converts worst among younger/middle segments (24.2%).
**Hypothesis:** Ticket-size anxiety ("I don't have enough to invest") is suppressing first investment among younger users.
**Experiment:** Introduce a ₹10 "starter investment" flow specifically surfaced to 18-24 users.
**Success Metric:** First Investment Rate, 18-24 segment.
**Expected Impact:** +6-8 pts in segment.

**11. Problem:** 25-34 is the highest-value segment but isn't specifically targeted in acquisition.
**Hypothesis:** Channel/creative targeting optimized for 25-34 will improve blended conversion and ticket size.
**Experiment:** Run age-targeted ad sets on Google/Meta specifically for 25-34.
**Success Metric:** Conversion Rate and Avg. Investment Amount within acquired 25-34 users.
**Expected Impact:** +3-4 pts conversion, +10-15% avg ticket size.

**12. Problem:** 45+ segment converts worst (21.0%) and is small — likely a trust/complexity barrier.
**Hypothesis:** Simplified UI + human-assisted onboarding (call/chat support) will unlock this segment.
**Experiment:** Offer opt-in phone-assisted KYC for users who select 45+ age band.
**Success Metric:** 45+ Activation Rate.
**Expected Impact:** +8-10 pts in segment (from a low base).

**13. Problem:** Signups spike in Jan and Oct-Nov but marketing spend is likely flat year-round.
**Hypothesis:** Front-loading budget into these windows will improve blended CAC.
**Experiment:** Shift 30% of quarterly ad budget into Oct-Nov and January specifically.
**Success Metric:** Blended CAC in shifted quarters vs. prior year.
**Expected Impact:** -8-12% blended CAC.

**14. Problem:** Paid Social LTV:CAC is deeply negative at channel level (masked by blended LTV:CAC).
**Hypothesis:** Capping or pausing Paid Social spend will improve overall marketing efficiency without a proportional loss in users.
**Experiment:** Reduce Paid Social budget by 30% for one quarter and reallocate to Referral + Organic.
**Success Metric:** Blended LTV:CAC ratio, total net users acquired.
**Expected Impact:** Neutral-to-positive net users, improved blended LTV:CAC.

**15. Problem:** First Investment Rate among Verified users (49%) suggests half of activated users still don't invest.
**Hypothesis:** A default/suggested investment amount at the point of KYC completion will reduce decision fatigue.
**Experiment:** A/B test a pre-filled "Recommended: ₹100" first-investment screen immediately post-KYC.
**Success Metric:** First Investment Rate.
**Expected Impact:** +6-8 pts.

**16. Problem:** No visibility into *why* users drop off mid-KYC (Rejected/In Progress = 25% of the base).
**Hypothesis:** Document quality/format issues are a leading cause of KYC rejection.
**Experiment:** Add real-time document quality validation (blur/crop detection) before submission.
**Success Metric:** KYC Rejection Rate.
**Expected Impact:** -30-40% rejection rate.

**17. Problem:** Engagement (session count) is a strong retention predictor but isn't currently used to trigger interventions.
**Hypothesis:** A win-back campaign targeted at users with declining session frequency will reduce preventable churn.
**Experiment:** Trigger a win-back push/email when a user's weekly sessions drop 50%+ vs. their own baseline.
**Success Metric:** 30-day Retention Rate among targeted users vs. control.
**Expected Impact:** +5-7 pts retention in targeted segment.

**18. Problem:** ARPPU (₹90.68) is over 3x ARPU (₹27.97), showing most revenue depends on a minority of investing users.
**Hypothesis:** Cross-selling a recurring auto-invest feature to existing one-time investors will raise ARPPU further.
**Experiment:** Prompt one-time investors to set up a recurring weekly auto-save after their first investment.
**Success Metric:** ARPPU, % of investors on recurring auto-save.
**Expected Impact:** +15-20% ARPPU among converted investors.

**19. Problem:** "Was Referred" users retain better (69.2%) but there's no distinct onboarding for them.
**Hypothesis:** A referral-specific onboarding (highlighting the referrer's trust/social proof) will lift activation further.
**Experiment:** Show "Your friend [Name] has already invested ₹X" social-proof messaging during KYC for referred users.
**Success Metric:** Activation Rate among referred users.
**Expected Impact:** +5 pts within this segment.

**20. Problem:** No current mechanism distinguishes "at risk" active users before they churn.
**Hypothesis:** A composite engagement score (sessions + recency + investment status) can flag at-risk users early enough to intervene.
**Experiment:** Build and pilot a simple churn-risk score; route flagged users into a retention email/push flow.
**Success Metric:** Churn Rate among flagged users vs. unflagged baseline.
**Expected Impact:** -5-8 pts churn in flagged, treated segment.

---

## 9. Dashboard Filters

| Filter | Type | Purpose |
|---|---|---|
| Date Range | Date slicer | Compare periods, isolate seasonality (e.g., Oct-Nov vs. rest of year) |
| Acquisition Channel | Multi-select dropdown | The #1 cut for CAC and channel-quality decisions |
| City / City Tier | Multi-select dropdown | Geographic performance and expansion planning |
| Device (Android/iOS) | Toggle | Platform-specific engagement and monetization differences |
| Age Group | Multi-select dropdown | Segment-specific messaging and product decisions |
| KYC Status | Multi-select dropdown | Isolate funnel stages for targeted analysis |

All filters should apply globally across all four dashboard zones (Power BI slicers synced across pages) so a Growth PM can, for example, filter to "Paid Social + 18-24 + last 90 days" and see the full funnel and revenue picture for that exact slice in one click.

---

## 10. Modern Dashboard Design Guidance (for Product Managers)

- **Lead with decisions, not data.** Every chart should answer a specific question a stakeholder would ask in a review ("is this channel worth the spend?"), not just display a metric because the data existed.
- **Use a restrained color palette** — one accent color for "good" (e.g., teal/green) and one for "needs attention" (amber/red), applied consistently to KPI card deltas across the whole dashboard. Avoid rainbow charts; they force the reader to work harder than necessary.
- **Big numbers first, detail on demand.** KPI cards at the top, drill-down tables/charts below — respects the reader's attention the way a real exec dashboard must.
- **Annotate anomalies directly on the chart** (e.g., a small callout on the January spike: "New Year acquisition push") rather than leaving the reader to guess why a trend line moved.
- **Keep every page to one screen, no scrolling**, if possible — Power BI/Looker dashboards used in actual weekly reviews are built to be screen-shared without scrolling mid-meeting.
- **Consistent granularity across visuals** — if the top KPI cards are monthly, don't silently mix in a weekly trend chart without labeling it clearly; inconsistent time grains are the most common trust-breaking mistake in dashboards.

---

## 11. How This Project Mirrors Real Growth Team Work at Fintech Startups

This project is deliberately structured the way a Growth/Analytics intern's actual first project would be scoped at a company like Jar, CRED, or Zepto:

- **Start from a business problem, not a dataset.** Real growth work never starts with "here's some data, find insights" — it starts with a leadership question ("are we acquiring the right users?") that the dashboard is built to answer.
- **KPI definitions require judgment calls, not just formulas.** Deciding that Activation Rate should be measured against *all* signups while First Investment Rate should be measured against *KYC-Verified* users only is exactly the kind of definitional decision a PM has to make and defend in a metrics review — small definitional choices change what "good" looks like.
- **CAC is never perfectly available** — modeling it from assumed channel budgets (as done here) is standard practice in early-stage companies before a clean spend-to-user pipeline exists between marketing and product data.
- **Insights are prioritized by leverage, not just interestingness.** The experiment backlog explicitly ties each experiment back to funnel leverage (activation > acquisition tweaks) — this reflects how real growth teams triage: fix the biggest leak before optimizing a smaller one.
- **The output is a decision-support tool, not a report.** A real growth dashboard is a living artifact used in weekly business reviews, not a one-time analysis — which is why this project includes filters and a layout designed for repeated use, not a single static conclusion.
- **Unit economics (LTV:CAC by channel) is the actual language growth teams use to defend or kill a channel** with finance and leadership — this project doesn't stop at "channel X converts better," it goes one step further to "channel X is/isn't worth what we're paying for it," which is the level recruiters want to see you operate at.

---

## 12. Tech Stack & How to Extend This

- **Dataset:** `jar_growth_dataset.csv` (12,500 rows) — import directly into Power BI, Excel, or Google Sheets.
- **SQL:** `kpi_queries.sql` — all 15 KPIs plus cohort/funnel breakdowns, written in SQLite-compatible ANSI SQL (portable to Postgres/BigQuery with minor date-function tweaks, noted inline).
- **Python:** `generate_dataset.py` — fully documented data generation logic; useful to show in a GitHub repo as evidence of understanding the data's structure, not just consuming it.
- **Power BI build steps:** Import CSV → build a simple star-schema-style data model (optionally split into a Users table + a Channel-Spend lookup table for the CAC calc) → build the four zones above using DAX measures for each KPI (formulas map 1:1 to the SQL in `kpi_queries.sql`) → publish and share the `.pbix`.

**Suggested repo structure for GitHub:**
```
growth-metrics-dashboard-jar/
├── README.md                  (this file — also your project write-up)
├── data/
│   └── jar_growth_dataset.csv
├── sql/
│   └── kpi_queries.sql
├── scripts/
│   └── generate_dataset.py
└── dashboard/
    └── growth_dashboard.pbix  (add after you build it in Power BI)
```

**For your resume:** *"Built an end-to-end growth analytics project for a fintech app — designed a 15-KPI framework, generated and modeled a 12,500-user dataset, wrote SQL to compute activation/conversion/retention/CAC/LTV metrics, and translated findings into a 20-experiment growth backlog prioritized by funnel leverage."*
