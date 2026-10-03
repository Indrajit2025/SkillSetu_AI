# SIH 26246 — Requirements Compliance Matrix

**Project**: SkillSetu AI  
**Problem Statement**: 26246 — AI-Enabled Labour Market Intelligence and Skill Demand-Supply Forecasting Engine  
**Last Updated**: October 2026

---

## Core Requirements Compliance

| # | Requirement | Implementation | API / Component | Evidence / Demo Location |
|---|---|---|---|---|
| 1 | Aggregate and normalize labour-demand signals | `DemandEngine.compute_demand_index()` — 4 signal types (job postings, hiring growth, GVA, investments), Min-Max normalized to 0-100 | `app/services/demand_engine.py` | GET /api/demand; Dashboard → Market Details |
| 2 | Cross-reference demand with training capacity by state/district/sector/trade | `LabourDemand` × `TrainingSupply` tables joined by (district_id, sector_id, trade_id, year) | `app/api/endpoints/market.py` | GET /api/market-details?district_id=&sector_id=&trade_id= |
| 3 | Forecast future demand-supply gaps at district/sector/trade | `ForecastingEngine` — GBR, Ridge, Baseline compared; time-aware split; 2025-2028 forecasts | `app/services/forecasting_engine.py` | GET /api/forecast; Dashboard → Forecast Tab |
| 4 | Rank trades by shortage/oversupply severity | `SkillGap.severity_score` 0-100; ranked in `/api/rankings` | `app/api/endpoints/gaps.py` | GET /api/rankings; Dashboard → Rankings Tab |
| 5 | Interactive drill-down dashboard (National→State→District→Sector→Trade) | React frontend (pending); API supports full drill-down chain | All overview/market endpoints | Dashboard → National → Odisha → Khordha → IT → Full Stack Dev |
| 6 | API and export functionality | Full RESTful FastAPI with OpenAPI docs; `/api/export` endpoint | `app/api/endpoints/datasources.py` | GET /api/export; GET /api/docs |

---

## Data Pipeline Compliance

| Pipeline Stage | Implementation | File |
|---|---|---|
| Raw Data | NCVT-MIS calibrated pilot data (is_synthetic=1 labelled) | `seed_data.py` |
| Validation | Pydantic schemas with type enforcement | `app/schemas/` |
| Cleaning | Seed script with null checks, floor values | `seed_data.py` |
| Normalization | Min-Max in DemandEngine and SupplyEngine | `demand_engine.py`, `supply_engine.py` |
| Occupation/Trade Mapping | `OccupationMapping` table with NCO codes | `app/models/taxonomy.py` |
| Demand Feature Generation | job_postings, hiring_growth, GVA, investments | `LabourDemand` model + `demand_engine.py` |
| Supply Feature Generation | seats, enrolments, passouts, absorption_rate | `TrainingSupply` model + `supply_engine.py` |
| Demand Index | Weighted linear combination (documented, configurable) | `demand_engine.py` |
| Supply Index | Weighted linear combination (documented, configurable) | `supply_engine.py` |
| Forecasting | GBR + Ridge + Baseline; time-aware splits | `forecasting_engine.py` |
| Skill-Gap Engine | net_gap, gap_ratio, classification | `skill_gap_service.py` |
| Decision Intelligence | DiagnosticExplainer + policy recommendations | `diagnostic_explainer.py` |
| Dashboard/API | FastAPI endpoints + React frontend | `app/api/` + frontend |

---

## Data Model Compliance

| Required Table | Implemented As | Notes |
|---|---|---|
| states | `State` | With region, is_pilot flag |
| districts | `District` | With lat/lon, economic tier |
| sectors | `Sector` | With SSC name, icon |
| trades | `Trade` | With NSQF level |
| occupations | `Occupation` | With NCO 2015 code |
| occupation_mapping | `OccupationMapping` | With alignment confidence |
| labour_demand | `LabourDemand` | 4 raw signals + normalized index |
| training_supply | `TrainingSupply` | 5 raw signals + normalized index |
| labour_indicators | `LabourIndicator` | PLFS-aligned macro indicators |
| forecasts | `Forecast` | With confidence bounds |
| skill_gaps | `SkillGap` | With diagnostic explanation |
| model_runs | `ModelRun` | With MAE/RMSE/MAPE/R2 |
| datasets | `DatasetCoverage` | With synthetic labelling |
| scenario_runs | `ScenarioRun` | Complete baseline vs scenario |

---

## Forecasting Compliance

| Requirement | Implementation |
|---|---|
| Naive/baseline model | `BaselineMovingAverage` — rolling 3-year average projection |
| Statistical/ML method | `RidgeRegression` — regularized linear with lag features |
| Stronger ML model | `GradientBoostingRegressor` — primary model |
| Time-aware train/test | Train on 2019-2023, test on 2024, forecast 2025-2028 |
| No random shuffle | Enforced — sorted by year, split at cutoff |
| MAE | Stored in `ModelRun.mae` |
| RMSE | Stored in `ModelRun.rmse` |
| MAPE | Stored in `ModelRun.mape` |
| R² | Stored in `ModelRun.r2_score` |
| Actual vs predicted | Shown in Model Evaluation dashboard |

---

## Skill Gap Engine Compliance

| Requirement | Implementation |
|---|---|
| Demand minus Supply | `net_gap = demand_value - supply_value` in `SkillGap` |
| State/district/sector/trade granularity | All 4 dimensions in `SkillGap` table |
| SHORTAGE classification | gap_ratio > SHORTAGE_THRESHOLD (0.15 configurable) |
| BALANCED classification | Between thresholds |
| OVERSUPPLY classification | gap_ratio < OVERSUPPLY_THRESHOLD (-0.15 configurable) |
| Normalized severity score | 0-100 scale in `SkillGap.severity_score` |
| Diagnostic explanation from features | `DiagnosticExplainer.explain_skill_gap()` |

---

## What-If Simulator Compliance

| Requirement | Implementation |
|---|---|
| Add training seats | `additional_seats` parameter |
| Boost intake | `intake_expansion_pct` parameter |
| Demand surge/decline | `demand_surge_pct` parameter |
| Placement rate change | `placement_boost_pct` parameter |
| Recalculate supply/demand/gap/status | `ScenarioService.run_simulation()` |
| Baseline vs Scenario comparison | `ScenarioSimulationResult` with `ScenarioMetricPair` |
| Timeline chart data | `comparison_timeline` list in response |

---

## SIH Demo Flow Compliance

| Demo Step | Supported By |
|---|---|
| Open dashboard | GET /api/overview |
| Select Odisha | GET /api/states + seed data |
| Select Khordha | GET /api/states/1/districts |
| Select IT / Full Stack Dev | GET /api/trades?sector_id=1 |
| Historical demand/supply | GET /api/market-details |
| Future forecast | GET /api/forecast |
| Shortage result | GET /api/skill-gaps |
| WHY explanation | SkillGap.diagnostic_explanation field |
| What-If Simulator | POST /api/scenarios |
| Gap changing after intervention | ScenarioSimulationResult.comparison_timeline |
| Model Evaluation | GET /api/model-evaluation |
| Actual vs predicted | ModelEvaluationItem.actual_vs_predicted |
