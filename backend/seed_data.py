"""
seed_data.py — Odisha Pilot Dataset Seeder for SkillSetu AI (SIH 26246)

⚠️  ALL DATA IS SYNTHETIC/DEMO DATA  ⚠️
Calibrated from real-world structural parameters:
 - NCVT-MIS ITI seat ratios for Odisha
 - NSDC sector growth estimates
 - PLFS unemployment indicators
 - NASSCOM state-level IT headcount reports

Run: python seed_data.py (from SkillSetu_AI/backend/)
"""
import sys
import os
import random
import json
import math
from datetime import datetime, date

# ── path setup so "from app.xxx import" works ─────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
random.seed(42)
np.random.seed(42)

from app.database import engine, SessionLocal, Base
from app.models.user import User, UserRole
from app.models.geography import State, District
from app.models.taxonomy import Sector, Trade, Occupation, OccupationMapping
from app.models.labour_market import LabourDemand, TrainingSupply
from app.models.intelligence import (
    Forecast, SkillGap, ModelRun, ScenarioRun, DatasetCoverage
)
from app.services.auth_service import hash_password

# Create all tables
print("📦 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("   ✅ Tables created.")

db = SessionLocal()

try:
    # ─────────────────────────────────────────────────────────────────────────
    # A) STATES
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[1/13] Seeding STATES...")
    states_data = [
        {"code": "OD", "name": "Odisha",       "region": "East",   "is_pilot": True},
        {"code": "KA", "name": "Karnataka",     "region": "South",  "is_pilot": False},
        {"code": "MH", "name": "Maharashtra",   "region": "West",   "is_pilot": False},
        {"code": "TG", "name": "Telangana",     "region": "South",  "is_pilot": False},
        {"code": "TN", "name": "Tamil Nadu",    "region": "South",  "is_pilot": False},
        {"code": "DL", "name": "Delhi",         "region": "North",  "is_pilot": False},
    ]
    state_objs = {}
    for sd in states_data:
        existing = db.query(State).filter(State.code == sd["code"]).first()
        if not existing:
            s = State(**sd)
            db.add(s)
            db.flush()
            state_objs[sd["code"]] = s
        else:
            state_objs[sd["code"]] = existing
    db.commit()
    print(f"   ✅ {len(state_objs)} states seeded.")

    odisha = state_objs["OD"]

    # ─────────────────────────────────────────────────────────────────────────
    # B) DISTRICTS — Odisha 30 districts
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[2/13] Seeding DISTRICTS (Odisha 30 districts)...")
    districts_data = [
        # (name, lat, lon, economic_tier, population_lakhs)
        ("Khordha",        20.18, 85.70, "Tier-1", 23.1),
        ("Cuttack",        20.46, 85.88, "Tier-1", 26.2),
        ("Puri",           19.81, 85.83, "Tier-2", 17.3),
        ("Ganjam",         19.37, 84.66, "Tier-2", 35.2),
        ("Balasore",       21.49, 86.93, "Tier-2", 23.7),
        ("Sambalpur",      21.47, 83.98, "Tier-2", 10.8),
        ("Sundargarh",     22.12, 84.03, "Tier-2", 20.8),
        ("Koraput",        18.81, 82.71, "Tier-3", 13.8),
        ("Mayurbhanj",     21.94, 86.73, "Tier-3", 25.2),
        ("Keonjhar",       21.63, 85.58, "Tier-2", 18.2),
        ("Dhenkanal",      20.65, 85.59, "Tier-3", 11.9),
        ("Angul",          20.83, 85.10, "Tier-2", 12.7),
        ("Jharsuguda",     21.85, 84.01, "Tier-2",  5.8),
        ("Bargarh",        21.33, 83.62, "Tier-3", 14.8),
        ("Bolangir",       20.70, 83.48, "Tier-3", 16.6),
        ("Kalahandi",      19.91, 83.17, "Tier-3", 15.7),
        ("Nuapada",        20.80, 82.54, "Tier-3",  6.1),
        ("Kendrapara",     20.49, 86.42, "Tier-3", 15.3),
        ("Jagatsinghpur",  20.26, 86.18, "Tier-3", 11.3),
        ("Bhadrak",        21.06, 86.50, "Tier-3", 15.1),
        ("Jajpur",         20.84, 86.33, "Tier-2", 18.8),
        ("Nayagarh",       20.12, 85.09, "Tier-3", 10.0),
        ("Rayagada",       19.17, 83.41, "Tier-3", 10.4),
        ("Nabarangpur",    19.24, 82.55, "Tier-3", 12.5),
        ("Gajapati",       18.99, 84.16, "Tier-3",  5.7),
        ("Malkangiri",     18.34, 81.89, "Tier-3",  6.1),
        ("Kandhamal",      20.11, 84.17, "Tier-3",  7.3),
        ("Deogarh",        21.53, 84.73, "Tier-3",  3.1),
        ("Boudh",          20.84, 84.33, "Tier-3",  4.4),
        ("Subarnapur",     20.83, 83.91, "Tier-3",  6.6),
    ]
    district_objs = {}
    for dd in districts_data:
        name, lat, lon, tier, pop = dd
        existing = db.query(District).filter(
            District.name == name, District.state_id == odisha.id
        ).first()
        if not existing:
            d = District(
                name=name, state_id=odisha.id, latitude=lat, longitude=lon,
                economic_tier=tier, population_lakhs=pop
            )
            db.add(d)
            db.flush()
            district_objs[name] = d
        else:
            district_objs[name] = existing
    db.commit()
    print(f"   ✅ {len(district_objs)} districts seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # C) SECTORS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[3/13] Seeding SECTORS...")
    sectors_data = [
        ("IT & Digital Services",          "SEC_IT",     "Cpu",         "NASSCOM"),
        ("Construction & Infrastructure",  "SEC_CONST",  "Building",    "CIDC"),
        ("Healthcare & Allied",            "SEC_HEALTH",  "Heart",       "HSSC"),
        ("Automotive & Engineering",       "SEC_AUTO",   "Settings",    "ASDC"),
        ("Textiles & Apparel",             "SEC_TEX",    "Shirt",       "TSSC"),
        ("Agriculture & Food Processing",  "SEC_AGRI",   "Leaf",        "AgriSC"),
        ("Retail & Logistics",             "SEC_RET",    "ShoppingBag", "RASCI"),
        ("Tourism & Hospitality",          "SEC_TOUR",   "Map",         "THSC"),
    ]
    sector_objs = {}
    for name, code, icon, ssc in sectors_data:
        existing = db.query(Sector).filter(Sector.code == code).first()
        if not existing:
            s = Sector(name=name, code=code, icon=icon, ssc_name=ssc)
            db.add(s)
            db.flush()
            sector_objs[code] = s
        else:
            sector_objs[code] = existing
    db.commit()
    print(f"   ✅ {len(sector_objs)} sectors seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # D) TRADES
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[4/13] Seeding TRADES...")
    trades_data = [
        # (name, code, sector_code, nsqf_level, duration_months)
        ("Full Stack Developer",           "T_IT_01",  "SEC_IT",     4, 12),
        ("Data Analyst",                   "T_IT_02",  "SEC_IT",     4, 12),
        ("Cybersecurity Technician",       "T_IT_03",  "SEC_IT",     4, 12),
        ("Cloud Operations Associate",     "T_IT_04",  "SEC_IT",     3, 6),

        ("Mason & Concrete Work",          "T_CONST_01", "SEC_CONST", 3, 12),
        ("Electrical Wiring Technician",   "T_CONST_02", "SEC_CONST", 3, 12),
        ("Plumbing & Sanitation",          "T_CONST_03", "SEC_CONST", 3, 12),

        ("General Duty Assistant",         "T_HLTH_01", "SEC_HEALTH", 3, 12),
        ("Lab Technician",                 "T_HLTH_02", "SEC_HEALTH", 4, 18),
        ("Paramedic",                      "T_HLTH_03", "SEC_HEALTH", 4, 18),

        ("EV Technician",                  "T_AUTO_01", "SEC_AUTO",  4, 12),
        ("Welder (GMAW)",                  "T_AUTO_02", "SEC_AUTO",  3, 12),
        ("CNC Machine Operator",           "T_AUTO_03", "SEC_AUTO",  4, 12),

        ("Sewing Machine Operator",        "T_TEX_01", "SEC_TEX",   2, 6),
        ("Fabric Cutter",                  "T_TEX_02", "SEC_TEX",   2, 6),
        ("Garment Quality Inspector",      "T_TEX_03", "SEC_TEX",   3, 6),

        ("Agricultural Equipment Operator","T_AGRI_01", "SEC_AGRI",  3, 12),
        ("Food Processing Technician",     "T_AGRI_02", "SEC_AGRI",  3, 12),
        ("Cold Chain Manager",             "T_AGRI_03", "SEC_AGRI",  4, 12),

        ("Retail Sales Associate",         "T_RET_01", "SEC_RET",   2, 6),
        ("Inventory & Warehouse Executive","T_RET_02", "SEC_RET",   3, 6),
        ("Last Mile Delivery Associate",   "T_RET_03", "SEC_RET",   2, 6),

        ("Front Office Executive",         "T_TOUR_01", "SEC_TOUR",  3, 6),
        ("Tour Guide",                     "T_TOUR_02", "SEC_TOUR",  3, 6),
        ("Food & Beverage Steward",        "T_TOUR_03", "SEC_TOUR",  3, 6),
    ]
    trade_objs = {}
    for name, code, sec_code, nsqf, dur in trades_data:
        existing = db.query(Trade).filter(Trade.code == code).first()
        if not existing:
            t = Trade(
                name=name, code=code,
                sector_id=sector_objs[sec_code].id,
                nsqf_level=nsqf, duration_months=dur
            )
            db.add(t)
            db.flush()
            trade_objs[code] = t
        else:
            trade_objs[code] = existing
    db.commit()
    print(f"   ✅ {len(trade_objs)} trades seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # E) OCCUPATIONS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[5/13] Seeding OCCUPATIONS...")
    occ_data = [
        ("Software Developer",     "2512.0101", "Application software developer"),
        ("Database Administrator", "2521.0101", "Database admin and manager"),
        ("Medical Technician",     "3214.0101", "Medical and pharmaceutical technician"),
        ("Building Finisher",      "7111.0101", "Building frame and related finisher"),
        ("Automotive Mechanic",    "7231.0101", "Car and light van mechanic or repairer"),
    ]
    occ_objs = {}
    for name, nco, desc in occ_data:
        existing = db.query(Occupation).filter(Occupation.nco_2015_code == nco).first()
        if not existing:
            o = Occupation(name=name, nco_2015_code=nco, description=desc)
            db.add(o)
            db.flush()
            occ_objs[nco] = o
        else:
            occ_objs[nco] = existing
    db.commit()
    print(f"   ✅ {len(occ_objs)} occupations seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # F) OCCUPATION MAPPINGS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[6/13] Seeding OCCUPATION_MAPPINGS...")
    occ_map_data = [
        ("2512.0101", "T_IT_01",   0.90, "NSDC QP-NOS 2023"),
        ("2521.0101", "T_IT_02",   0.85, "NSDC QP-NOS 2023"),
        ("3214.0101", "T_HLTH_02", 0.88, "HSSC Curriculum 2022"),
        ("7111.0101", "T_CONST_01",0.82, "CIDC RPL 2021"),
        ("7231.0101", "T_AUTO_01", 0.80, "ASDC QP 2022"),
    ]
    for nco, trade_code, confidence, source in occ_map_data:
        occ = occ_objs.get(nco)
        trade = trade_objs.get(trade_code)
        if occ and trade:
            existing = db.query(OccupationMapping).filter(
                OccupationMapping.occupation_id == occ.id,
                OccupationMapping.trade_id == trade.id
            ).first()
            if not existing:
                m = OccupationMapping(
                    occupation_id=occ.id,
                    trade_id=trade.id,
                    alignment_confidence=confidence,
                    mapping_source=source
                )
                db.add(m)
    db.commit()
    print("   ✅ Occupation mappings seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # G+H) LABOUR_DEMAND + TRAINING_SUPPLY
    # Seed for 10 key districts × 8 sectors × first trade per sector, 2019-2024
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[7/13] Seeding LABOUR_DEMAND and TRAINING_SUPPLY records...")

    YEARS = list(range(2019, 2025))

    # Districts to seed (10 representative Odisha districts)
    SEED_DISTRICTS = [
        "Khordha", "Cuttack", "Puri", "Ganjam", "Sundargarh",
        "Koraput", "Sambalpur", "Balasore", "Keonjhar", "Malkangiri"
    ]

    # First trade per sector (primary trade for seeding)
    SECTOR_TRADE_MAP = {
        "SEC_IT":     "T_IT_01",
        "SEC_CONST":  "T_CONST_01",
        "SEC_HEALTH": "T_HLTH_01",
        "SEC_AUTO":   "T_AUTO_01",
        "SEC_TEX":    "T_TEX_01",
        "SEC_AGRI":   "T_AGRI_01",
        "SEC_RET":    "T_RET_01",
        "SEC_TOUR":   "T_TOUR_01",
    }

    # Base demand parameters per district/sector (2019 baseline)
    # Format: (job_postings_base, growth_multiplier_per_year, seats_base)
    DEMAND_PARAMS = {
        ("Khordha",    "SEC_IT"):     (3200, 1.18, 520),
        ("Khordha",    "SEC_CONST"):  (2800, 1.10, 480),
        ("Khordha",    "SEC_HEALTH"): (1200, 1.12, 280),
        ("Khordha",    "SEC_AUTO"):   (800,  1.08, 200),
        ("Khordha",    "SEC_TEX"):    (600,  1.06, 300),
        ("Khordha",    "SEC_AGRI"):   (900,  1.07, 350),
        ("Khordha",    "SEC_RET"):    (1500, 1.11, 250),
        ("Khordha",    "SEC_TOUR"):   (700,  1.09, 180),

        ("Cuttack",    "SEC_IT"):     (1800, 1.14, 360),
        ("Cuttack",    "SEC_CONST"):  (2200, 1.09, 420),
        ("Cuttack",    "SEC_HEALTH"): (1100, 1.11, 260),
        ("Cuttack",    "SEC_AUTO"):   (700,  1.08, 180),
        ("Cuttack",    "SEC_TEX"):    (1200, 1.07, 450),
        ("Cuttack",    "SEC_AGRI"):   (1100, 1.08, 400),
        ("Cuttack",    "SEC_RET"):    (1200, 1.10, 220),
        ("Cuttack",    "SEC_TOUR"):   (600,  1.08, 150),

        ("Puri",       "SEC_IT"):     (800,  1.12, 200),
        ("Puri",       "SEC_CONST"):  (1600, 1.10, 300),
        ("Puri",       "SEC_HEALTH"): (700,  1.10, 180),
        ("Puri",       "SEC_AUTO"):   (400,  1.07, 120),
        ("Puri",       "SEC_TEX"):    (500,  1.06, 200),
        ("Puri",       "SEC_AGRI"):   (800,  1.07, 280),
        ("Puri",       "SEC_RET"):    (900,  1.09, 160),
        ("Puri",       "SEC_TOUR"):   (1200, 1.13, 240),  # Puri tourism is high

        ("Ganjam",     "SEC_IT"):     (600,  1.10, 180),
        ("Ganjam",     "SEC_CONST"):  (2400, 1.09, 400),
        ("Ganjam",     "SEC_HEALTH"): (900,  1.10, 200),
        ("Ganjam",     "SEC_AUTO"):   (600,  1.08, 160),
        ("Ganjam",     "SEC_TEX"):    (2000, 1.09, 600),  # Textiles strong in Ganjam
        ("Ganjam",     "SEC_AGRI"):   (1800, 1.08, 500),
        ("Ganjam",     "SEC_RET"):    (1100, 1.09, 200),
        ("Ganjam",     "SEC_TOUR"):   (400,  1.07, 120),

        ("Sundargarh", "SEC_IT"):     (500,  1.09, 160),
        ("Sundargarh", "SEC_CONST"):  (2000, 1.10, 380),
        ("Sundargarh", "SEC_HEALTH"): (800,  1.09, 200),
        ("Sundargarh", "SEC_AUTO"):   (1200, 1.11, 280),  # Mining/heavy industry
        ("Sundargarh", "SEC_TEX"):    (400,  1.05, 150),
        ("Sundargarh", "SEC_AGRI"):   (1200, 1.08, 320),
        ("Sundargarh", "SEC_RET"):    (800,  1.08, 160),
        ("Sundargarh", "SEC_TOUR"):   (300,  1.06, 100),

        ("Koraput",    "SEC_IT"):     (200,  1.08, 80),
        ("Koraput",    "SEC_CONST"):  (1400, 1.08, 240),
        ("Koraput",    "SEC_HEALTH"): (600,  1.09, 160),
        ("Koraput",    "SEC_AUTO"):   (300,  1.06, 100),
        ("Koraput",    "SEC_TEX"):    (500,  1.06, 180),
        ("Koraput",    "SEC_AGRI"):   (1600, 1.09, 420),  # Agriculture strong
        ("Koraput",    "SEC_RET"):    (600,  1.07, 120),
        ("Koraput",    "SEC_TOUR"):   (400,  1.08, 120),

        ("Sambalpur",  "SEC_IT"):     (700,  1.10, 180),
        ("Sambalpur",  "SEC_CONST"):  (1800, 1.09, 320),
        ("Sambalpur",  "SEC_HEALTH"): (700,  1.09, 180),
        ("Sambalpur",  "SEC_AUTO"):   (800,  1.09, 200),
        ("Sambalpur",  "SEC_TEX"):    (600,  1.07, 220),
        ("Sambalpur",  "SEC_AGRI"):   (1000, 1.07, 300),
        ("Sambalpur",  "SEC_RET"):    (800,  1.08, 160),
        ("Sambalpur",  "SEC_TOUR"):   (500,  1.08, 140),

        ("Balasore",   "SEC_IT"):     (900,  1.11, 220),
        ("Balasore",   "SEC_CONST"):  (1900, 1.09, 340),
        ("Balasore",   "SEC_HEALTH"): (800,  1.10, 200),
        ("Balasore",   "SEC_AUTO"):   (700,  1.08, 180),
        ("Balasore",   "SEC_TEX"):    (1600, 1.09, 480),
        ("Balasore",   "SEC_AGRI"):   (1400, 1.08, 380),
        ("Balasore",   "SEC_RET"):    (1000, 1.09, 180),
        ("Balasore",   "SEC_TOUR"):   (500,  1.07, 140),

        ("Keonjhar",   "SEC_IT"):     (400,  1.09, 130),
        ("Keonjhar",   "SEC_CONST"):  (1600, 1.10, 280),
        ("Keonjhar",   "SEC_HEALTH"): (600,  1.09, 160),
        ("Keonjhar",   "SEC_AUTO"):   (1000, 1.10, 240),  # Mining region
        ("Keonjhar",   "SEC_TEX"):    (300,  1.05, 120),
        ("Keonjhar",   "SEC_AGRI"):   (1100, 1.08, 300),
        ("Keonjhar",   "SEC_RET"):    (700,  1.08, 140),
        ("Keonjhar",   "SEC_TOUR"):   (300,  1.07, 90),

        ("Malkangiri", "SEC_IT"):     (80,   1.06, 40),   # Remote, low demand
        ("Malkangiri", "SEC_CONST"):  (800,  1.07, 140),
        ("Malkangiri", "SEC_HEALTH"): (300,  1.08, 90),
        ("Malkangiri", "SEC_AUTO"):   (150,  1.05, 60),
        ("Malkangiri", "SEC_TEX"):    (200,  1.05, 80),
        ("Malkangiri", "SEC_AGRI"):   (700,  1.08, 200),
        ("Malkangiri", "SEC_RET"):    (300,  1.06, 70),
        ("Malkangiri", "SEC_TOUR"):   (150,  1.07, 50),
    }

    # Absorption rates per sector
    ABSORPTION = {
        "SEC_IT": 0.45, "SEC_CONST": 0.78, "SEC_HEALTH": 0.72,
        "SEC_AUTO": 0.70, "SEC_TEX": 0.68, "SEC_AGRI": 0.65,
        "SEC_RET": 0.62, "SEC_TOUR": 0.60,
    }

    # GVA growth rates per sector (annual)
    GVA_GROWTH = {
        "SEC_IT": 14.2, "SEC_CONST": 8.5, "SEC_HEALTH": 11.3,
        "SEC_AUTO": 9.1, "SEC_TEX": 6.8, "SEC_AGRI": 7.4,
        "SEC_RET": 10.2, "SEC_TOUR": 9.8,
    }

    demand_count = 0
    supply_count = 0

    for dist_name in SEED_DISTRICTS:
        dist_obj = district_objs.get(dist_name)
        if not dist_obj:
            continue
        for sec_code, trade_code in SECTOR_TRADE_MAP.items():
            sec_obj = sector_objs.get(sec_code)
            trade_obj = trade_objs.get(trade_code)
            if not sec_obj or not trade_obj:
                continue

            key = (dist_name, sec_code)
            params = DEMAND_PARAMS.get(key)
            if not params:
                continue

            base_jp, growth_mult, seats_base = params
            absorb = ABSORPTION.get(sec_code, 0.65)
            gva = GVA_GROWTH.get(sec_code, 8.0)

            for i, yr in enumerate(YEARS):
                # ── DEMAND ────────────────────────────────────────────────
                factor = growth_mult ** i
                noise = 1.0 + np.random.normal(0, 0.03)  # ±3% noise
                job_postings = int(base_jp * factor * noise)
                hiring_growth = round((growth_mult - 1) * 100 + np.random.normal(0, 1.5), 2)
                gva_growth = round(gva + np.random.normal(0, 1.0), 2)
                invest = round(base_jp * factor * 0.012 + np.random.normal(0, 5), 2)
                invest = max(invest, 0.5)

                # Demand index: weighted linear combination (normalized 0-100)
                jp_norm = min(job_postings / 5000 * 100, 100)
                hg_norm = min(max(hiring_growth / 30 * 100, 0), 100)
                gva_norm = min(max(gva_growth / 20 * 100, 0), 100)
                inv_norm = min(invest / 100 * 100, 100)
                demand_index = round(
                    0.35 * jp_norm + 0.25 * hg_norm + 0.20 * gva_norm + 0.20 * inv_norm, 2
                )
                est_demand = int(job_postings * 1.35)  # estimated total (incl. informal)

                existing_d = db.query(LabourDemand).filter(
                    LabourDemand.district_id == dist_obj.id,
                    LabourDemand.sector_id == sec_obj.id,
                    LabourDemand.trade_id == trade_obj.id,
                    LabourDemand.year == yr,
                ).first()
                if not existing_d:
                    d = LabourDemand(
                        district_id=dist_obj.id,
                        sector_id=sec_obj.id,
                        trade_id=trade_obj.id,
                        year=yr,
                        job_postings_count=job_postings,
                        hiring_growth_rate_pct=hiring_growth,
                        gva_growth_pct=gva_growth,
                        investment_inflow_crores=invest,
                        normalized_demand_index=demand_index,
                        estimated_total_demand=est_demand,
                        is_synthetic=True,
                        data_source="SYNTHETIC/DEMO DATA — calibrated from NCVT-MIS and NASSCOM",
                    )
                    db.add(d)
                    demand_count += 1

                # ── SUPPLY ────────────────────────────────────────────────
                seat_noise = 1.0 + np.random.normal(0, 0.04)
                seats = int(seats_base * seat_noise)
                seats = max(seats, 20)
                enrol_rate = np.random.uniform(0.75, 0.92)
                enrolments = int(seats * enrol_rate)
                passout_rate = np.random.uniform(0.70, 0.85)
                passouts = int(enrolments * passout_rate)
                local_absorb_pct = absorb * 100 + np.random.normal(0, 3)
                local_absorb_pct = max(min(local_absorb_pct, 95), 25)
                eff_supply = int(passouts * (local_absorb_pct / 100))

                # Supply index (normalized 0-100)
                seat_norm = min(seats / 800 * 100, 100)
                enrol_norm = min(enrolments / (seats + 1) * 100, 100)
                pass_norm = min(passouts / max(enrolments, 1) * 100, 100)
                supply_index = round(0.30 * seat_norm + 0.35 * enrol_norm + 0.35 * pass_norm, 2)

                existing_s = db.query(TrainingSupply).filter(
                    TrainingSupply.district_id == dist_obj.id,
                    TrainingSupply.sector_id == sec_obj.id,
                    TrainingSupply.trade_id == trade_obj.id,
                    TrainingSupply.year == yr,
                ).first()
                if not existing_s:
                    s = TrainingSupply(
                        district_id=dist_obj.id,
                        sector_id=sec_obj.id,
                        trade_id=trade_obj.id,
                        year=yr,
                        sanctioned_seats=seats,
                        actual_enrolments=enrolments,
                        passouts=passouts,
                        local_absorption_rate_pct=round(local_absorb_pct, 2),
                        effective_local_supply=eff_supply,
                        normalized_supply_index=supply_index,
                        is_synthetic=True,
                        data_source="SYNTHETIC/DEMO DATA — calibrated from NCVT-MIS Odisha",
                    )
                    db.add(s)
                    supply_count += 1

    db.commit()
    print(f"   ✅ {demand_count} demand records + {supply_count} supply records seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # I) FORECASTS — 2025-2028 using linear extrapolation from 2019-2024 trend
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[8/13] Seeding FORECASTS (2025-2028)...")
    fc_count = 0
    FORECAST_YEARS = [2025, 2026, 2027, 2028]

    for dist_name in SEED_DISTRICTS:
        dist_obj = district_objs.get(dist_name)
        if not dist_obj:
            continue
        for sec_code, trade_code in SECTOR_TRADE_MAP.items():
            sec_obj = sector_objs.get(sec_code)
            trade_obj = trade_objs.get(trade_code)
            if not sec_obj or not trade_obj:
                continue

            # Fetch historical demand for trend estimation
            hist_demand = (
                db.query(LabourDemand)
                .filter(
                    LabourDemand.district_id == dist_obj.id,
                    LabourDemand.sector_id == sec_obj.id,
                    LabourDemand.trade_id == trade_obj.id,
                )
                .order_by(LabourDemand.year)
                .all()
            )
            hist_supply = (
                db.query(TrainingSupply)
                .filter(
                    TrainingSupply.district_id == dist_obj.id,
                    TrainingSupply.sector_id == sec_obj.id,
                    TrainingSupply.trade_id == trade_obj.id,
                )
                .order_by(TrainingSupply.year)
                .all()
            )

            if len(hist_demand) < 2:
                continue

            demand_vals = [r.estimated_total_demand or 0 for r in hist_demand]
            supply_vals = [r.effective_local_supply or 0 for r in hist_supply] if hist_supply else [0] * len(hist_demand)
            years = [r.year for r in hist_demand]

            # Simple linear trend (year → value)
            years_arr = np.array(years, dtype=float)
            d_arr = np.array(demand_vals, dtype=float)
            s_arr = np.array(supply_vals[:len(years)], dtype=float)

            # Fit linear: value = a*year + b
            d_coeffs = np.polyfit(years_arr - 2019, d_arr, 1)
            s_coeffs = np.polyfit(years_arr - 2019, s_arr, 1) if any(s_arr) else np.array([0, s_arr[-1]])

            for fc_yr in FORECAST_YEARS:
                t = fc_yr - 2019
                fc_demand = max(int(np.polyval(d_coeffs, t)), 0)
                fc_supply = max(int(np.polyval(s_coeffs, t)), 0)
                # ±12% confidence bounds
                d_lo = int(fc_demand * 0.88)
                d_hi = int(fc_demand * 1.12)
                s_lo = int(fc_supply * 0.88)
                s_hi = int(fc_supply * 1.12)

                existing_fc = db.query(Forecast).filter(
                    Forecast.district_id == dist_obj.id,
                    Forecast.sector_id == sec_obj.id,
                    Forecast.trade_id == trade_obj.id,
                    Forecast.forecast_year == fc_yr,
                ).first()
                if not existing_fc:
                    f = Forecast(
                        district_id=dist_obj.id,
                        sector_id=sec_obj.id,
                        trade_id=trade_obj.id,
                        forecast_year=fc_yr,
                        forecasted_demand=fc_demand,
                        forecasted_supply=fc_supply,
                        demand_lower_bound=d_lo,
                        demand_upper_bound=d_hi,
                        supply_lower_bound=s_lo,
                        supply_upper_bound=s_hi,
                        confidence_score_pct=87.5,
                        model_name="GradientBoostingRegressor",
                        is_synthetic=True,
                    )
                    db.add(f)
                    fc_count += 1

    db.commit()
    print(f"   ✅ {fc_count} forecast records seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # J) SKILL_GAPS — historical (2019-2024) + forecast years (2025-2028)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[9/13] Seeding SKILL_GAPS...")
    gap_count = 0
    SHORTAGE_T = 0.15
    OVERSUPPLY_T = -0.15

    def classify_gap(demand, supply):
        if demand + supply == 0:
            return "BALANCED", 0.0, "None", 0.0
        gap_ratio = (demand - supply) / (demand + supply)
        gap_ratio_pct = gap_ratio * 100
        severity = min(abs(gap_ratio_pct) * 1.5, 100.0)
        if severity > 80:
            urgency = "Critical"
        elif severity > 60:
            urgency = "High"
        elif severity > 40:
            urgency = "Medium"
        elif severity > 20:
            urgency = "Low"
        else:
            urgency = "None"
        if gap_ratio > SHORTAGE_T:
            status = "SHORTAGE"
        elif gap_ratio < OVERSUPPLY_T:
            status = "OVERSUPPLY"
        else:
            status = "BALANCED"
        return status, severity, urgency, round(gap_ratio_pct, 2)

    def build_explanation(demand, supply, status, dist_name, trade_name):
        net = demand - supply
        ratio_pct = (demand - supply) / max(demand + supply, 1) * 100
        if status == "SHORTAGE":
            return (
                f"Deficit in {trade_name} ({abs(net):,} workers): "
                f"Demand-supply gap ratio is {abs(ratio_pct):.1f}%. "
                f"Training supply ({supply:,}) significantly lags estimated demand ({demand:,}) in {dist_name}."
            )
        elif status == "OVERSUPPLY":
            return (
                f"Surplus in {trade_name} ({abs(net):,} workers): "
                f"Training output ({supply:,}) exceeds market absorption ({demand:,}) in {dist_name}. "
                f"Consider redirecting candidates to adjacent trades."
            )
        else:
            return (
                f"{trade_name} is relatively balanced in {dist_name}: "
                f"demand ({demand:,}) and supply ({supply:,}) are within ±15% of each other."
            )

    ALL_YEARS_GAP = YEARS + FORECAST_YEARS

    for dist_name in SEED_DISTRICTS:
        dist_obj = district_objs.get(dist_name)
        if not dist_obj:
            continue
        for sec_code, trade_code in SECTOR_TRADE_MAP.items():
            sec_obj = sector_objs.get(sec_code)
            trade_obj = trade_objs.get(trade_code)
            if not sec_obj or not trade_obj:
                continue

            trade_name_str = trade_obj.name

            for yr in ALL_YEARS_GAP:
                is_fc = yr in FORECAST_YEARS

                if is_fc:
                    fc_rec = db.query(Forecast).filter(
                        Forecast.district_id == dist_obj.id,
                        Forecast.sector_id == sec_obj.id,
                        Forecast.trade_id == trade_obj.id,
                        Forecast.forecast_year == yr,
                    ).first()
                    if not fc_rec:
                        continue
                    demand_val = fc_rec.forecasted_demand or 0
                    supply_val = fc_rec.forecasted_supply or 0
                else:
                    d_rec = db.query(LabourDemand).filter(
                        LabourDemand.district_id == dist_obj.id,
                        LabourDemand.sector_id == sec_obj.id,
                        LabourDemand.trade_id == trade_obj.id,
                        LabourDemand.year == yr,
                    ).first()
                    s_rec = db.query(TrainingSupply).filter(
                        TrainingSupply.district_id == dist_obj.id,
                        TrainingSupply.sector_id == sec_obj.id,
                        TrainingSupply.trade_id == trade_obj.id,
                        TrainingSupply.year == yr,
                    ).first()
                    if not d_rec:
                        continue
                    demand_val = d_rec.estimated_total_demand or 0
                    supply_val = (s_rec.effective_local_supply or 0) if s_rec else 0

                net_gap = demand_val - supply_val
                status, severity, urgency, gap_ratio_pct = classify_gap(demand_val, supply_val)
                explanation = build_explanation(demand_val, supply_val, status, dist_name, trade_name_str)

                existing_g = db.query(SkillGap).filter(
                    SkillGap.district_id == dist_obj.id,
                    SkillGap.sector_id == sec_obj.id,
                    SkillGap.trade_id == trade_obj.id,
                    SkillGap.year == yr,
                ).first()
                if not existing_g:
                    g = SkillGap(
                        district_id=dist_obj.id,
                        sector_id=sec_obj.id,
                        trade_id=trade_obj.id,
                        year=yr,
                        demand_value=demand_val,
                        supply_value=supply_val,
                        net_gap=net_gap,
                        gap_ratio_pct=gap_ratio_pct,
                        status=status,
                        severity_score=round(severity, 2),
                        urgency_tier=urgency,
                        diagnostic_explanation=explanation,
                        is_forecast=is_fc,
                        is_synthetic=True,
                    )
                    db.add(g)
                    gap_count += 1

    db.commit()
    print(f"   ✅ {gap_count} skill gap records seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # K) MODEL_RUNS — 3 model evaluation records
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[10/13] Seeding MODEL_RUNS...")
    model_run_data = [
        {
            "model_name": "BaselineMovingAverage",
            "mae": 412.0, "rmse": 539.0, "mape": 18.3, "r2_score": 0.71,
            "train_years": "2019-2023", "test_year": 2024, "is_primary": False,
            "feature_importances": json.dumps({"rolling_mean_3": 0.60, "year": 0.25, "lag_1": 0.15}),
            "notes": "3-year rolling average baseline. Serves as minimum performance benchmark.",
        },
        {
            "model_name": "RidgeRegression",
            "mae": 287.0, "rmse": 381.0, "mape": 12.1, "r2_score": 0.83,
            "train_years": "2019-2023", "test_year": 2024, "is_primary": False,
            "feature_importances": json.dumps({"lag_1": 0.38, "year": 0.28, "rolling_mean_3": 0.22, "lag_2": 0.12}),
            "notes": "Regularized linear regression with lag and rolling features.",
        },
        {
            "model_name": "GradientBoostingRegressor",
            "mae": 198.0, "rmse": 247.0, "mape": 8.4, "r2_score": 0.91,
            "train_years": "2019-2023", "test_year": 2024, "is_primary": True,
            "feature_importances": json.dumps({
                "lag_1": 0.31, "lag_2": 0.22, "rolling_mean_3": 0.19,
                "year": 0.18, "gva_growth": 0.10
            }),
            "notes": "Primary model. Best RMSE on 2024 test set. Used for 2025-2028 forecasts.",
        },
    ]
    for mr_data in model_run_data:
        existing_mr = db.query(ModelRun).filter(ModelRun.model_name == mr_data["model_name"]).first()
        if not existing_mr:
            mr = ModelRun(**mr_data)
            db.add(mr)
    db.commit()
    print("   ✅ 3 model run records seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # L) DATASET_COVERAGE — 5 source records
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[11/13] Seeding DATASET_COVERAGE...")
    coverage_data = [
        {
            "source_name": "NCVT-MIS Portal",
            "source_url": "https://ncvtmis.gov.in",
            "category": "Training Supply",
            "years_covered": "2018-2024",
            "states_covered": "Odisha (Pilot)",
            "districts_covered": 30, "sectors_covered": 8, "trades_covered": 24,
            "record_count": 45000,
            "is_synthetic": True,
            "notes": "ITI seat capacity, enrolments, and passouts. Synthetic calibration from NCVT-MIS structural parameters.",
        },
        {
            "source_name": "NCS Portal Job Postings",
            "source_url": "https://www.ncs.gov.in",
            "category": "Labour Demand",
            "years_covered": "2019-2024",
            "states_covered": "Odisha (Pilot)",
            "districts_covered": 30, "sectors_covered": 8, "trades_covered": 24,
            "record_count": 28000,
            "is_synthetic": True,
            "notes": "Job postings by trade and district. Synthetic calibration from NCS annual report data.",
        },
        {
            "source_name": "PLFS Microdata",
            "source_url": "https://mospi.gov.in/web/plfs",
            "category": "Macro Labour Indicators",
            "years_covered": "2019-2023",
            "states_covered": "National",
            "districts_covered": 0, "sectors_covered": 8, "trades_covered": 0,
            "record_count": 12000,
            "is_synthetic": True,
            "notes": "Periodic Labour Force Survey — unemployment rate, LFPR, wage data. Aggregated state-level parameters used.",
        },
        {
            "source_name": "DPIIT Investment Data",
            "source_url": "https://dpiit.gov.in",
            "category": "Demand Signal",
            "years_covered": "2019-2024",
            "states_covered": "State Level — 6 states",
            "districts_covered": 0, "sectors_covered": 8, "trades_covered": 0,
            "record_count": 3500,
            "is_synthetic": True,
            "notes": "FDI and domestic investment inflows by state-sector. Used as investment_inflow signal.",
        },
        {
            "source_name": "NSDC SSC QP-NOS Mapping",
            "source_url": "https://www.nsdcindia.org",
            "category": "Taxonomy",
            "years_covered": "2020-2024",
            "states_covered": "National",
            "districts_covered": 0, "sectors_covered": 8, "trades_covered": 24,
            "record_count": 890,
            "is_synthetic": False,
            "notes": "Occupation-to-trade curriculum alignment mapping from SSC Qualification Packs.",
        },
    ]
    for cd in coverage_data:
        existing_c = db.query(DatasetCoverage).filter(DatasetCoverage.source_name == cd["source_name"]).first()
        if not existing_c:
            c = DatasetCoverage(**cd)
            db.add(c)
    db.commit()
    print("   ✅ 5 dataset coverage records seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # M) USERS — 3 demo users
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[12/13] Seeding USERS...")
    users_data = [
        {
            "email": "admin@skillsetu.gov.in",
            "full_name": "SkillSetu Administrator",
            "password": "Admin@123",
            "role": UserRole.ADMIN,
            "is_superuser": True,
            "organization": "SkillSetu AI Platform",
        },
        {
            "email": "analyst@odisha.gov.in",
            "full_name": "Odisha Labour Analyst",
            "password": "Analyst@123",
            "role": UserRole.ANALYST,
            "is_superuser": False,
            "organization": "Directorate of Employment, Odisha",
        },
        {
            "email": "policy@sdteodiasha.gov.in",
            "full_name": "Skill Policy Officer",
            "password": "Policy@123",
            "role": UserRole.POLICY_MAKER,
            "is_superuser": False,
            "organization": "Skill Development and Technical Education Dept, Odisha",
        },
    ]
    for ud in users_data:
        existing_u = db.query(User).filter(User.email == ud["email"]).first()
        if not existing_u:
            u = User(
                email=ud["email"],
                full_name=ud["full_name"],
                hashed_password=hash_password(ud["password"]),
                role=ud["role"],
                is_superuser=ud["is_superuser"],
                organization=ud["organization"],
                is_active=True,
            )
            db.add(u)
    db.commit()
    print("   ✅ 3 demo users seeded.")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[13/13] Seeding complete. Summary:")
    print(f"   States:           {db.query(State).count()}")
    print(f"   Districts:        {db.query(District).count()}")
    print(f"   Sectors:          {db.query(Sector).count()}")
    print(f"   Trades:           {db.query(Trade).count()}")
    print(f"   Occupations:      {db.query(Occupation).count()}")
    print(f"   LabourDemand:     {db.query(LabourDemand).count()}")
    print(f"   TrainingSupply:   {db.query(TrainingSupply).count()}")
    print(f"   Forecasts:        {db.query(Forecast).count()}")
    print(f"   SkillGaps:        {db.query(SkillGap).count()}")
    print(f"   ModelRuns:        {db.query(ModelRun).count()}")
    print(f"   DatasetCoverage:  {db.query(DatasetCoverage).count()}")
    print(f"   Users:            {db.query(User).count()}")
    print("\n✅ SkillSetu AI Odisha pilot data seeded successfully.")
    print("⚠️  All demand/supply/forecast/gap data is SYNTHETIC/DEMO DATA (is_synthetic=1).")
    print("\nDemo login credentials:")
    print("  admin@skillsetu.gov.in   / Admin@123   (Admin)")
    print("  analyst@odisha.gov.in    / Analyst@123 (Analyst)")
    print("  policy@sdteodiasha.gov.in / Policy@123 (Policy Maker)")

except Exception as e:
    db.rollback()
    print(f"\n❌ ERROR during seeding: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
