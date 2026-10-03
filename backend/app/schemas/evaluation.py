from pydantic import BaseModel
from typing import List, Optional


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class ModelEvaluationItem(BaseModel):
    model_name: str
    mae: float
    rmse: float
    mape: Optional[float] = None
    r2_score: float
    train_years: str = "2019-2023"
    test_year: int = 2024
    is_primary_model: bool = False
    feature_importances: List[FeatureImportanceItem] = []
    notes: str = ""


class EvaluationDashboardResponse(BaseModel):
    models: List[ModelEvaluationItem]
    methodology_notes: List[str]
    data_split_strategy: str
    primary_model_name: str
