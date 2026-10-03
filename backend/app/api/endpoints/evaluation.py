"""
evaluation.py — ML model evaluation dashboard endpoint.
GET /api/model-evaluation
"""
import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.intelligence import ModelRun
from app.schemas.evaluation import (
    ModelEvaluationItem, EvaluationDashboardResponse, FeatureImportanceItem
)

router = APIRouter(tags=["Model Evaluation"])


@router.get("/model-evaluation", response_model=EvaluationDashboardResponse)
def get_model_evaluation(db: Session = Depends(get_db)):
    """
    Return model evaluation dashboard:
    - All trained model comparison (MAE, RMSE, MAPE, R²)
    - Feature importance for primary model
    - Methodology notes
    """
    model_runs = db.query(ModelRun).order_by(ModelRun.rmse).all()

    if not model_runs:
        return EvaluationDashboardResponse(
            models=[],
            methodology_notes=["No model runs found. Please run seed_data.py first."],
            data_split_strategy="",
            primary_model_name="",
        )

    # Mark primary model as the one with lowest RMSE (already sorted)
    best_rmse = model_runs[0].rmse if model_runs else 9999

    items: List[ModelEvaluationItem] = []
    for mr in model_runs:
        # Parse feature importances JSON
        feature_importances: List[FeatureImportanceItem] = []
        if mr.feature_importances:
            try:
                fi_dict = json.loads(mr.feature_importances)
                feature_importances = [
                    FeatureImportanceItem(feature=k, importance=v)
                    for k, v in sorted(fi_dict.items(), key=lambda x: -x[1])
                ]
            except (json.JSONDecodeError, AttributeError):
                pass

        items.append(
            ModelEvaluationItem(
                model_name=mr.model_name,
                mae=mr.mae or 0.0,
                rmse=mr.rmse or 0.0,
                mape=mr.mape,
                r2_score=mr.r2_score or 0.0,
                train_years=mr.train_years or "2019-2023",
                test_year=mr.test_year or 2024,
                is_primary_model=(mr.rmse == best_rmse),
                feature_importances=feature_importances,
                notes=mr.notes or "",
            )
        )

    methodology_notes = [
        "Time-aware train/test split: Training on years 2019–2023, testing on held-out year 2024.",
        "Future forecasts (2025–2028) generated iteratively using the primary model (GradientBoostingRegressor).",
        "Features used: year, year² (curvature), lag_1 (previous year value), lag_2, rolling_mean_3.",
        "MAPE excluded when actual values are near zero to avoid division errors.",
        "No random shuffling of time-series data — future observations are never used in training.",
        "All evaluation metrics (MAE, RMSE, MAPE, R²) computed on the 2024 test set.",
        "Baseline model is a 3-year rolling average — serves as minimum performance benchmark.",
        "Demand signals: job postings (35%), hiring growth rate (25%), GVA growth (20%), investment inflows (20%).",
        "Supply signals: sanctioned seats (30%), actual enrolments (35%), passouts / completions (35%).",
        "Weights are configurable in config.py / .env without redeployment.",
    ]

    return EvaluationDashboardResponse(
        models=items,
        methodology_notes=methodology_notes,
        data_split_strategy="Train: 2019–2023 | Test: 2024 | Forecast: 2025–2028",
        primary_model_name="GradientBoostingRegressor",
    )
