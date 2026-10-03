# SkillSetu AI — Data Sources and Attribution

**SIH PS 26246 | Data Honesty Statement**

> ⚠️ **PILOT DATA NOTICE**: The Odisha pilot dataset in this system is a **calibrated synthetic dataset** (`is_synthetic=1`) generated from real-world structural parameters and ratios available from open government sources. All synthetic records are clearly labelled in the database and API responses. No fabricated statistics are presented as official government data.

---

## Official Data Sources Referenced for Structural Calibration

| Source | Category | Coverage | Availability |
|---|---|---|---|
| **NCVT-MIS Portal** (ncvtmis.gov.in) | Training Supply | All India ITI/Diploma seat capacity, enrolments, passouts | Public Open Data |
| **NCS Portal** (ncs.gov.in) | Demand | Job postings by trade, district, sector | Public API |
| **PLFS (Periodic Labour Force Survey)** | Macro Labour | Unemployment, LFPR, wage data by state | NSO / MoSPI Open Data |
| **DPIIT Industrial Investment** (dpiit.gov.in) | Demand Signal | FDI and domestic investment by state-sector | Public Reports |
| **NSDC / SSC QP-NOS Database** | Taxonomy | Trade-to-occupation curriculum mapping | NSDC Open Reports |
| **CMIE Prowess / State Economic Survey** | Sector GVA | State-level GVA growth by sector | Paid / State Govt |
| **Census 2011 / Projected 2024** | Geography | District-level working-age population | Registrar General of India |

---

## Synthetic Dataset Parameters (Odisha Pilot)

| Parameter | Calibration Basis |
|---|---|
| IT demand volume (Khordha) | NASSCOM State of Tech report 2023 — Odisha IT headcount ~45,000 |
| ITI sanctioned seats | NCVT-MIS Odisha data — 1,84,000 seats across 30 districts |
| Passout rates | National NCVT average 72-78% for technology trades |
| Local absorption rate (IT) | NSDC pilot study — 35-55% ITI passouts find local IT jobs |
| Construction demand growth | PMGSY + PMAY scheme expenditure projections |
| Healthcare demand growth | NHM Odisha staffing norms vs actual fill rates |
| Agriculture trade demand | State Agriculture Dept crop-processing expansion targets |

---

## Dataset Coverage Summary

| Dataset | Years | States | Districts | Sectors | Trades | Records |
|---|---|---|---|---|---|---|
| NCVT-MIS Supply Data | 2018-2024 | Odisha (pilot) | 30 | 8 | 24 | ~45,000 |
| NCS Demand Postings | 2019-2024 | Odisha (pilot) | 30 | 8 | 24 | ~28,000 |
| PLFS Macro Data | 2019-2023 | National | N/A | N/A | N/A | ~12,000 |
| DPIIT Investment | 2019-2024 | State Level | N/A | 8 | N/A | ~3,500 |
| SSC Taxonomy Mapping | 2020-2024 | National | N/A | 8 | 24 | ~890 |

**Total records in pilot database: ~89,390**

---

## How to Use Real Data in Production

1. **Replace synthetic data** by importing actual NCVT-MIS CSV exports into the `training_supply` table (set `is_synthetic=0`)
2. **Connect NCS API** for live job posting counts — update `LabourDemand.job_postings_count` nightly
3. **Ingest PLFS microdata** into `LabourIndicator` table
4. **Retrain forecasting models** using `forecasting_engine.py` on real data to get genuine evaluation metrics

---

## Licensing and Fair Use

All source data from official government portals is used under Open Government Data (OGD) Platform India license (data.gov.in) which permits use for research and policymaking purposes with attribution.
