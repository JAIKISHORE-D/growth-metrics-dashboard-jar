"""
Growth Metrics Dashboard - Synthetic Dataset Generator
Simulates 10,000+ users of a Jar-inspired fintech (micro-savings/investment) app
over a 12-month window (Jul 2025 - Jun 2026), with realistic funnel drop-off,
channel quality differences, seasonality, and churn patterns baked in on purpose
so that the resulting dashboard has real, discoverable insights.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 12500  # >10,000 users

# ---------------------------------------------------------------------
# 1. SIGNUP DATE (12-month window with seasonality: Jan (New Year resolutions)
#    and Oct-Nov (festive/bonus season in India) get spikes)
# ---------------------------------------------------------------------
start_date = datetime(2025, 7, 1)
end_date = datetime(2026, 6, 30)
total_days = (end_date - start_date).days

month_weights = {
    7: 0.9, 8: 0.85, 9: 0.9, 10: 1.4, 11: 1.5, 12: 1.1,
    1: 1.6, 2: 1.0, 3: 0.95, 4: 0.85, 5: 0.8, 6: 1.0
}

day_offsets = []
for _ in range(N):
    m = np.random.choice(list(month_weights.keys()), p=np.array(list(month_weights.values()))/sum(month_weights.values()))
    year = 2025 if m >= 7 else 2026
    day = np.random.randint(1, 28)
    d = datetime(year, m, day)
    day_offsets.append(d)
signup_dates = pd.to_datetime(day_offsets)

# ---------------------------------------------------------------------
# 2. ACQUISITION CHANNEL (with different quality -> affects downstream funnel)
# ---------------------------------------------------------------------
channels = ["Organic", "Referral", "Paid Social (Meta/Insta)", "Influencer", "Google Ads", "App Store Search"]
channel_probs = [0.22, 0.18, 0.20, 0.15, 0.15, 0.10]
acquisition_channel = np.random.choice(channels, size=N, p=channel_probs)

# Channel quality multipliers (affects activation/KYC/investment probability)
channel_quality = {
    "Organic": 1.25, "Referral": 1.35, "Paid Social (Meta/Insta)": 0.75,
    "Influencer": 0.85, "Google Ads": 1.05, "App Store Search": 1.10
}

# ---------------------------------------------------------------------
# 3. DEVICE
# ---------------------------------------------------------------------
devices = ["Android", "iOS"]
device = np.random.choice(devices, size=N, p=[0.82, 0.18])  # India-skewed Android base

# ---------------------------------------------------------------------
# 4. CITY (Tier 1/2/3 mix, India fintech-realistic)
# ---------------------------------------------------------------------
cities = {
    "Bengaluru": 0.11, "Mumbai": 0.10, "Delhi NCR": 0.10, "Hyderabad": 0.08,
    "Pune": 0.07, "Chennai": 0.07, "Ahmedabad": 0.05, "Kolkata": 0.05,
    "Jaipur": 0.05, "Lucknow": 0.05, "Surat": 0.04, "Indore": 0.04,
    "Coimbatore": 0.04, "Patna": 0.04, "Bhopal": 0.04, "Nagpur": 0.03,
    "Guwahati": 0.03
}
city = np.random.choice(list(cities.keys()), size=N, p=np.array(list(cities.values()))/sum(cities.values()))

tier1 = {"Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai"}
city_tier = np.array(["Tier 1" if c in tier1 else "Tier 2/3" for c in city])

# ---------------------------------------------------------------------
# 5. AGE GROUP
# ---------------------------------------------------------------------
age_groups = ["18-24", "25-34", "35-44", "45+"]
age_group = np.random.choice(age_groups, size=N, p=[0.38, 0.36, 0.17, 0.09])

# ---------------------------------------------------------------------
# Build base activation propensity score per user (drives KYC, investment, retention)
# ---------------------------------------------------------------------
base_score = np.random.normal(0.5, 0.15, N)
chan_mult = np.array([channel_quality[c] for c in acquisition_channel])
age_mult = np.array([{"18-24": 0.9, "25-34": 1.15, "35-44": 1.05, "45+": 0.85}[a] for a in age_group])
tier_mult = np.where(city_tier == "Tier 1", 1.1, 0.95)
device_mult = np.where(device == "iOS", 1.08, 1.0)

propensity = np.clip(base_score * chan_mult * age_mult * tier_mult * device_mult, 0.02, 0.98)

# ---------------------------------------------------------------------
# 6. KYC STATUS (funnel step 1 - Not Started / In Progress / Verified / Rejected)
# ---------------------------------------------------------------------
kyc_rand = np.random.rand(N)
kyc_status = np.empty(N, dtype=object)
for i in range(N):
    p = propensity[i]
    thresh_verified = 0.35 + 0.4 * p       # higher propensity -> more likely verified
    thresh_progress = thresh_verified + 0.15
    r = kyc_rand[i]
    if r < thresh_verified:
        kyc_status[i] = "Verified"
    elif r < thresh_progress:
        kyc_status[i] = "In Progress"
    elif r < thresh_progress + 0.10:
        kyc_status[i] = "Rejected"
    else:
        kyc_status[i] = "Not Started"

# ---------------------------------------------------------------------
# 7. FIRST INVESTMENT (Yes/No) - only possible if KYC Verified
# ---------------------------------------------------------------------
first_investment = np.array(["No"] * N, dtype=object)
invest_prob = np.clip(propensity * 0.85, 0.03, 0.95)
for i in range(N):
    if kyc_status[i] == "Verified" and np.random.rand() < invest_prob[i]:
        first_investment[i] = "Yes"

# ---------------------------------------------------------------------
# 8. INVESTMENT AMOUNT (INR) - only for those who invested; lognormal (realistic skew)
# ---------------------------------------------------------------------
investment_amount = np.zeros(N)
invested_mask = first_investment == "Yes"
n_invested = invested_mask.sum()
raw_amounts = np.random.lognormal(mean=7.3, sigma=0.9, size=n_invested)  # median ~ INR 1,480
investment_amount[invested_mask] = np.round(np.clip(raw_amounts, 50, 250000), 2)

# ---------------------------------------------------------------------
# 9. REFERRAL STATUS (Referred Others / Was Referred / None)
# ---------------------------------------------------------------------
referral_status = np.empty(N, dtype=object)
for i in range(N):
    if acquisition_channel[i] == "Referral":
        referral_status[i] = "Was Referred"
    else:
        r = np.random.rand()
        # More active/invested users refer more
        refer_prob = 0.10 + (0.25 if invested_mask[i] else 0)
        referral_status[i] = "Referred Others" if r < refer_prob else "None"

# ---------------------------------------------------------------------
# 10. SESSION COUNT (lifetime sessions) - correlated with propensity & tenure
# ---------------------------------------------------------------------
tenure_days = np.array([(end_date - d).days for d in signup_dates])
tenure_days = np.clip(tenure_days, 1, None)
session_rate_per_week = np.clip(propensity * np.random.normal(2.2, 0.6, N), 0.05, 6)
session_count = np.round(session_rate_per_week * (tenure_days / 7) * np.random.uniform(0.4, 1.0, N)).astype(int)
session_count = np.clip(session_count, 1, None)

# ---------------------------------------------------------------------
# 11. CHURN STATUS & LAST ACTIVE DATE
#     Churn defined as no activity in the last 30 days from dataset end_date
# ---------------------------------------------------------------------
# Higher propensity + invested users churn less
churn_prob = np.clip(0.75 - propensity * 0.55 - invested_mask * 0.15, 0.03, 0.95)
churned = np.random.rand(N) < churn_prob

last_active_date = []
for i in range(N):
    if churned[i]:
        # Last active sometime between signup and (end_date - 31 to 200 days)
        max_gap = max((tenure_days[i] - 31), 1)
        gap = np.random.randint(1, max_gap + 1) if max_gap > 1 else 1
        la = signup_dates[i] + timedelta(days=min(gap, tenure_days[i]))
    else:
        # Active recently (within last 30 days)
        recent_gap = np.random.randint(0, 30)
        la = end_date - timedelta(days=recent_gap)
        if la < signup_dates[i]:
            la = signup_dates[i]
    last_active_date.append(la)
last_active_date = pd.to_datetime(last_active_date)

churn_status = np.where(churned, "Churned", "Active")

# ---------------------------------------------------------------------
# 12. RETENTION DAYS (days between signup and last active - i.e. engagement lifespan)
# ---------------------------------------------------------------------
retention_days = (last_active_date - signup_dates).days
retention_days = pd.Series(retention_days).clip(lower=0)

# ---------------------------------------------------------------------
# 13. REVENUE (platform revenue per user - management fee / spread on investments
#     + subscription fees; only meaningful for invested & active-ish users)
# ---------------------------------------------------------------------
revenue = np.zeros(N)
fee_rate = np.random.uniform(0.004, 0.012, N)  # annualized-ish take rate proxy
revenue[invested_mask] = np.round(
    investment_amount[invested_mask] * fee_rate[invested_mask] * (retention_days[invested_mask] / 30).clip(lower=0.5), 2
)
# small flat revenue for engaged non-investors (ads/interest float, referral bonuses etc.)
non_invest_engaged = (~invested_mask) & (session_count > np.percentile(session_count, 70))
revenue[non_invest_engaged] += np.round(np.random.uniform(2, 25, non_invest_engaged.sum()), 2)

# ---------------------------------------------------------------------
# Assemble DataFrame
# ---------------------------------------------------------------------
df = pd.DataFrame({
    "User_ID": [f"JAR{100000+i}" for i in range(N)],
    "Signup_Date": signup_dates.strftime("%Y-%m-%d"),
    "Acquisition_Channel": acquisition_channel,
    "Device": device,
    "City": city,
    "City_Tier": city_tier,
    "Age_Group": age_group,
    "KYC_Status": kyc_status,
    "First_Investment": first_investment,
    "Investment_Amount": investment_amount,
    "Referral_Status": referral_status,
    "Session_Count": session_count,
    "Last_Active_Date": last_active_date.strftime("%Y-%m-%d"),
    "Retention_Days": retention_days,
    "Revenue": revenue,
    "Churn_Status": churn_status,
})

df.to_csv("/home/claude/growth_dashboard/jar_growth_dataset.csv", index=False)

print("Rows:", len(df))
print(df.head(3).to_string())
print("\n--- Quick sanity stats ---")
print("KYC distribution:\n", df.KYC_Status.value_counts(normalize=True).round(3))
print("\nFirst Investment rate:", (df.First_Investment=="Yes").mean().round(3))
print("Churn rate:", (df.Churn_Status=="Churned").mean().round(3))
print("Avg revenue (all users):", df.Revenue.mean().round(2))
print("Avg revenue (invested users):", df[df.First_Investment=="Yes"].Revenue.mean().round(2))
print("File size check:")
