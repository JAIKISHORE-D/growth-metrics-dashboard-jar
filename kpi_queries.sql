/* ============================================================
   GROWTH METRICS DASHBOARD - KPI SQL QUERIES
   Table: users  (12,500 rows, one row per user)
   Dialect: ANSI SQL / SQLite-compatible (minor tweaks needed for
   BigQuery/Postgres date functions are noted inline)
   ============================================================ */

-- ------------------------------------------------------------
-- 1. TOTAL USERS
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_users
FROM users;

-- ------------------------------------------------------------
-- 2. NEW USERS (by month)
-- ------------------------------------------------------------
SELECT strftime('%Y-%m', Signup_Date) AS signup_month,
       COUNT(*) AS new_users
FROM users
GROUP BY signup_month
ORDER BY signup_month;

-- ------------------------------------------------------------
-- 3. DAU / WAU / MAU (proxy, since we only store Last_Active_Date
--    not a full event log). We treat "active on day X" as
--    Last_Active_Date = X. For WAU/MAU we count anyone whose
--    Last_Active_Date falls within the trailing window from a
--    reference date.
-- ------------------------------------------------------------
-- DAU for a specific reference date (e.g. 2026-06-15)
SELECT COUNT(*) AS dau
FROM users
WHERE Last_Active_Date = '2026-06-15';

-- WAU: unique active users in trailing 7 days from reference date
SELECT COUNT(*) AS wau
FROM users
WHERE date(Last_Active_Date) BETWEEN date('2026-06-15', '-6 day') AND date('2026-06-15');

-- MAU: unique active users in trailing 30 days from reference date
SELECT COUNT(*) AS mau
FROM users
WHERE date(Last_Active_Date) BETWEEN date('2026-06-15', '-29 day') AND date('2026-06-15');

-- Stickiness ratio (DAU/MAU) - measures engagement depth
SELECT
  (SELECT COUNT(*) FROM users WHERE Last_Active_Date = '2026-06-15') * 1.0 /
  (SELECT COUNT(*) FROM users WHERE date(Last_Active_Date) BETWEEN date('2026-06-15','-29 day') AND date('2026-06-15'))
  AS dau_mau_stickiness;

-- ------------------------------------------------------------
-- 4. ACTIVATION RATE
--    Definition: % of signed-up users who completed KYC (the
--    action that unlocks the core product value)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN KYC_Status = 'Verified' THEN 1 ELSE 0 END) / COUNT(*), 2) AS activation_rate_pct
FROM users;

-- ------------------------------------------------------------
-- 5. CONVERSION RATE
--    Definition: % of users who made their First_Investment = 'Yes'
--    out of TOTAL signups (full-funnel conversion)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN First_Investment = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS conversion_rate_pct
FROM users;

-- ------------------------------------------------------------
-- 6. KYC COMPLETION RATE
--    Definition: % of users who *started* KYC that reached Verified
--    (funnel-step conversion, different from Activation Rate above
--    which is against total signups)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN KYC_Status = 'Verified' THEN 1 ELSE 0 END) /
        SUM(CASE WHEN KYC_Status IN ('Verified','In Progress','Rejected') THEN 1 ELSE 0 END), 2)
  AS kyc_completion_rate_pct
FROM users;

-- ------------------------------------------------------------
-- 7. FIRST INVESTMENT RATE
--    Definition: % of KYC-Verified users who went on to invest
--    (measures activation -> monetization step specifically)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN First_Investment = 'Yes' THEN 1 ELSE 0 END) /
        SUM(CASE WHEN KYC_Status = 'Verified' THEN 1 ELSE 0 END), 2)
  AS first_investment_rate_pct
FROM users
WHERE KYC_Status = 'Verified';

-- ------------------------------------------------------------
-- 8. AVERAGE REVENUE PER USER (ARPU)
--    Definition: Total revenue / Total users (blended, all users)
-- ------------------------------------------------------------
SELECT ROUND(SUM(Revenue) * 1.0 / COUNT(*), 2) AS arpu
FROM users;

-- ARPU among paying/invested users only (ARPPU)
SELECT ROUND(SUM(Revenue) * 1.0 / COUNT(*), 2) AS arppu
FROM users
WHERE First_Investment = 'Yes';

-- ------------------------------------------------------------
-- 9. CUSTOMER LIFETIME VALUE (LTV) - simplified model
--    LTV = ARPU x Average Retention (in months) x Gross Margin
--    Here we approximate: LTV = ARPU_per_active_month * avg_lifespan_months
--    Using Retention_Days / 30 as lifespan proxy, gross margin assumed 70%
-- ------------------------------------------------------------
SELECT
  ROUND( (SUM(Revenue) * 1.0 / COUNT(*)) *
         (AVG(Retention_Days) / 30.0) * 0.70, 2) AS estimated_ltv
FROM users;

-- ------------------------------------------------------------
-- 10. CUSTOMER ACQUISITION COST (CAC) - by channel
--     Requires a marketing-spend table in a real setting. For this
--     project we model CAC using assumed monthly channel budgets
--     (see cac_assumptions in the write-up) joined against new users
--     acquired per channel.
--     Example (spend hardcoded per channel for illustration):
-- ------------------------------------------------------------
WITH spend AS (
  SELECT 'Organic' AS Acquisition_Channel, 150000 AS monthly_spend UNION ALL
  SELECT 'Referral', 400000 UNION ALL
  SELECT 'Paid Social (Meta/Insta)', 1800000 UNION ALL
  SELECT 'Influencer', 900000 UNION ALL
  SELECT 'Google Ads', 1200000 UNION ALL
  SELECT 'App Store Search', 100000
),
new_users_per_channel AS (
  SELECT Acquisition_Channel, COUNT(*) / 12.0 AS avg_monthly_new_users  -- 12-month dataset window
  FROM users
  GROUP BY Acquisition_Channel
)
SELECT s.Acquisition_Channel,
       ROUND(s.monthly_spend / n.avg_monthly_new_users, 0) AS cac_inr
FROM spend s
JOIN new_users_per_channel n ON s.Acquisition_Channel = n.Acquisition_Channel
ORDER BY cac_inr;

-- ------------------------------------------------------------
-- 11. RETENTION RATE (30-day)
--     Definition: % of users still Active as of dataset snapshot
--     (Churn_Status = 'Active' means active within last 30 days)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN Churn_Status = 'Active' THEN 1 ELSE 0 END) / COUNT(*), 2) AS retention_rate_pct
FROM users;

-- Cohort-based retention: % of each signup month still active
SELECT strftime('%Y-%m', Signup_Date) AS signup_month,
       COUNT(*) AS cohort_size,
       ROUND(100.0 * SUM(CASE WHEN Churn_Status='Active' THEN 1 ELSE 0 END)/COUNT(*), 2) AS retention_rate_pct
FROM users
GROUP BY signup_month
ORDER BY signup_month;

-- ------------------------------------------------------------
-- 12. CHURN RATE
--     Definition: % of users with Churn_Status = 'Churned'
--     (inverse of retention rate)
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN Churn_Status = 'Churned' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM users;

-- Churn rate by acquisition channel (find worst-quality channel)
SELECT Acquisition_Channel,
       COUNT(*) AS users,
       ROUND(100.0 * SUM(CASE WHEN Churn_Status='Churned' THEN 1 ELSE 0 END)/COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY Acquisition_Channel
ORDER BY churn_rate_pct DESC;

-- ------------------------------------------------------------
-- 13. REFERRAL RATE
--     Definition: % of total users who have referred at least
--     one other user (Referral_Status = 'Referred Others')
-- ------------------------------------------------------------
SELECT
  ROUND(100.0 * SUM(CASE WHEN Referral_Status = 'Referred Others' THEN 1 ELSE 0 END) / COUNT(*), 2) AS referral_rate_pct
FROM users;

-- ------------------------------------------------------------
-- BONUS: Full funnel view by acquisition channel
--    Signup -> KYC Verified -> Invested -> Retained (Active)
-- ------------------------------------------------------------
SELECT
  Acquisition_Channel,
  COUNT(*) AS signups,
  SUM(CASE WHEN KYC_Status='Verified' THEN 1 ELSE 0 END) AS kyc_verified,
  SUM(CASE WHEN First_Investment='Yes' THEN 1 ELSE 0 END) AS invested,
  SUM(CASE WHEN Churn_Status='Active' THEN 1 ELSE 0 END) AS retained,
  ROUND(100.0*SUM(CASE WHEN KYC_Status='Verified' THEN 1 ELSE 0 END)/COUNT(*),1) AS activation_pct,
  ROUND(100.0*SUM(CASE WHEN First_Investment='Yes' THEN 1 ELSE 0 END)/COUNT(*),1) AS conversion_pct,
  ROUND(100.0*SUM(CASE WHEN Churn_Status='Active' THEN 1 ELSE 0 END)/COUNT(*),1) AS retention_pct
FROM users
GROUP BY Acquisition_Channel
ORDER BY conversion_pct DESC;
