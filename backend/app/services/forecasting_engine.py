"""
forecasting_engine.py
---------------------
ML-based workforce demand/supply forecasting service for SkillSetu AI.

Models:
  - LinearRegression     (sklearn)
  - Ridge                (sklearn)
  - RandomForestRegressor (sklearn)
  - GradientBoostingRegressor (sklearn)
  - Naive Baseline       (statsmodels linear trend / moving-average)

Feature Engineering:
  year, year_sq, lag_1, lag_2, rolling_mean_3

Train  : 2019 – 2023
Test   : 2024
Forecast: 2025 – 2028

Accuracy metrics (computed on actual test split, never fabricated):
  MAE, RMSE, MAPE, R²
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data-transfer objects
# ---------------------------------------------------------------------------

@dataclass
class ForecastPoint:
    """Single-year forecast value with confidence interval."""
    year: int
    predicted_demand: float
    predicted_supply: float
    lower_ci: float
    upper_ci: float
    model_name: str


@dataclass
class ModelMetrics:
    """Hold evaluation metrics for one model."""
    model_name: str
    mae: float
    rmse: float
    mape: float
    r2: float


@dataclass
class ModelComparisonPoint:
    """Comparison across all trained models for a given year."""
    year: int
    actual: Optional[float]
    predictions: Dict[str, float] = field(default_factory=dict)
    metrics: Optional[ModelMetrics] = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRAIN_YEARS: List[int] = list(range(2019, 2024))   # 2019-2023 inclusive
TEST_YEARS:  List[int] = [2024]
FORECAST_YEARS: List[int] = list(range(2025, 2029)) # 2025-2028 inclusive
CI_MULTIPLIER: float = 1.96                          # 95 % CI


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _build_features(series: pd.Series) -> pd.DataFrame:
    """
    Build time-series features from a year-indexed numeric series.

    Parameters
    ----------
    series : pd.Series
        Index = year (int), values = numeric demand/supply figures.

    Returns
    -------
    pd.DataFrame with columns: year, year_sq, lag_1, lag_2, rolling_mean_3, value
    """
    df = pd.DataFrame({"year": series.index.astype(int), "value": series.values})
    df = df.sort_values("year").reset_index(drop=True)

    df["year_sq"] = df["year"] ** 2
    df["lag_1"] = df["value"].shift(1)
    df["lag_2"] = df["value"].shift(2)
    df["rolling_mean_3"] = df["value"].shift(1).rolling(window=3, min_periods=1).mean()

    return df


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error, guarded against zero division."""
    mask = y_true != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _compute_metrics(model_name: str, y_true: np.ndarray, y_pred: np.ndarray) -> ModelMetrics:
    """Compute MAE, RMSE, MAPE and R² from true vs predicted arrays."""
    mae  = float(mean_absolute_error(y_true, y_pred))
    rmse = float(math.sqrt(mean_squared_error(y_true, y_pred)))
    mape = _mape(y_true, y_pred)
    r2   = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan")
    return ModelMetrics(model_name=model_name, mae=mae, rmse=rmse, mape=mape, r2=r2)


# ---------------------------------------------------------------------------
# Naive baseline (statsmodels / manual linear extrapolation)
# ---------------------------------------------------------------------------

def _naive_forecast(train_df: pd.DataFrame, future_years: List[int]) -> np.ndarray:
    """
    Naive baseline: fit a simple OLS line via statsmodels on year vs value,
    then extrapolate. Falls back to moving-average slope if statsmodels is
    unavailable.
    """
    years  = train_df["year"].values.astype(float)
    values = train_df["value"].values.astype(float)

    try:
        import statsmodels.api as sm  # type: ignore

        X_sm = sm.add_constant(years)
        ols  = sm.OLS(values, X_sm).fit()
        X_future = sm.add_constant(np.array(future_years, dtype=float))
        return ols.predict(X_future).astype(float)
    except Exception:
        # Fallback: numpy polyfit degree-1
        coeffs = np.polyfit(years, values, 1)
        poly   = np.poly1d(coeffs)
        return poly(np.array(future_years, dtype=float))


# ---------------------------------------------------------------------------
# Core forecasting engine
# ---------------------------------------------------------------------------

class ForecastingEngine:
    """
    Multi-model ML forecasting engine for workforce skill data.

    Usage
    -----
    from app.services.forecasting_engine import forecasting_engine

    forecasts = forecasting_engine.forecast(demand_series, supply_series, [2025, 2026, 2027, 2028])
    comparison = forecasting_engine.compare_models(demand_series)
    """

    _MODELS: Dict[str, object] = {}

    def __init__(self) -> None:
        self._models: Dict[str, object] = {
            "LinearRegression":         LinearRegression(),
            "Ridge":                    Ridge(alpha=1.0),
            "RandomForest":             RandomForestRegressor(
                                            n_estimators=100,
                                            max_depth=4,
                                            random_state=42,
                                        ),
            "GradientBoosting":         GradientBoostingRegressor(
                                            n_estimators=100,
                                            learning_rate=0.1,
                                            max_depth=3,
                                            random_state=42,
                                        ),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _split_train_test(
        self,
        feature_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Time-aware split: train on TRAIN_YEARS, test on TEST_YEARS.
        NEVER applies random shuffling – temporal ordering is preserved.
        """
        train = feature_df[feature_df["year"].isin(TRAIN_YEARS)].dropna()
        test  = feature_df[feature_df["year"].isin(TEST_YEARS)].dropna()
        return train, test

    @staticmethod
    def _feature_cols() -> List[str]:
        return ["year", "year_sq", "lag_1", "lag_2", "rolling_mean_3"]

    def _train_and_evaluate(
        self,
        series: pd.Series,
    ) -> Tuple[Dict[str, object], Dict[str, ModelMetrics], pd.DataFrame]:
        """
        Train all models and return:
          - fitted model dict
          - metrics dict (keyed by model name)
          - full feature dataframe (train+test rows)
        """
        feat_df = _build_features(series)
        train_df, test_df = self._split_train_test(feat_df)

        feat_cols = self._feature_cols()

        if train_df.empty:
            raise ValueError(
                "Not enough training data. Need years 2019-2023 in the supplied series."
            )

        X_train = train_df[feat_cols].values
        y_train = train_df["value"].values

        fitted_models: Dict[str, object] = {}
        metrics_map:   Dict[str, ModelMetrics] = {}

        for name, model in self._models.items():
            try:
                model.fit(X_train, y_train)
                fitted_models[name] = model

                if not test_df.empty:
                    X_test = test_df[feat_cols].values
                    y_test = test_df["value"].values
                    y_pred = model.predict(X_test)
                    metrics_map[name] = _compute_metrics(name, y_test, y_pred)
                else:
                    logger.warning(
                        "No test data found for years %s – metrics unavailable.", TEST_YEARS
                    )
            except Exception as exc:
                logger.error("Model %s failed during training: %s", name, exc)

        return fitted_models, metrics_map, feat_df

    def _build_future_feature_row(
        self,
        year: int,
        last_known_values: List[float],
    ) -> np.ndarray:
        """
        Construct a single feature row for a future year.

        Parameters
        ----------
        year              : target forecast year
        last_known_values : recent actual/predicted values in ascending year order
                            (used to construct lag_1, lag_2, rolling_mean_3)
        """
        lag_1 = float(last_known_values[-1]) if len(last_known_values) >= 1 else 0.0
        lag_2 = float(last_known_values[-2]) if len(last_known_values) >= 2 else lag_1
        rolling_mean_3 = float(np.mean(last_known_values[-3:])) if last_known_values else 0.0

        return np.array([[year, year ** 2, lag_1, lag_2, rolling_mean_3]])

    def _iterative_forecast(
        self,
        fitted_models: Dict[str, object],
        feat_df: pd.DataFrame,
        target_years: List[int],
    ) -> Dict[str, Dict[int, float]]:
        """
        Iteratively forecast future years, feeding model predictions back as
        lag features for subsequent years.

        Returns dict: model_name -> {year: predicted_value}
        """
        # Seed with latest known values from feature_df
        known_values = list(feat_df.sort_values("year")["value"].values)

        results: Dict[str, Dict[int, float]] = {name: {} for name in fitted_models}
        # Per-model separate known_values to avoid cross-contamination
        model_known: Dict[str, List[float]] = {
            name: list(known_values) for name in fitted_models
        }

        for year in sorted(target_years):
            for name, model in fitted_models.items():
                row  = self._build_future_feature_row(year, model_known[name])
                pred = float(model.predict(row)[0])
                results[name][year] = pred
                model_known[name].append(pred)

        return results

    def _best_model_name(self, metrics_map: Dict[str, ModelMetrics]) -> str:
        """Return the model name with the lowest RMSE on the test split."""
        valid = {k: v for k, v in metrics_map.items() if not math.isnan(v.rmse)}
        if not valid:
            return "LinearRegression"
        return min(valid, key=lambda k: valid[k].rmse)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def forecast(
        self,
        demand_series: pd.Series,
        supply_series: pd.Series,
        target_years: Optional[List[int]] = None,
    ) -> List[ForecastPoint]:
        """
        Forecast workforce demand and supply for the specified target years.

        Parameters
        ----------
        demand_series : pd.Series  – year-indexed demand figures (2019-2024 at minimum)
        supply_series : pd.Series  – year-indexed supply figures (2019-2024 at minimum)
        target_years  : list of ints, defaults to 2025-2028

        Returns
        -------
        List[ForecastPoint] ordered by year, using the best-performing model
        (lowest RMSE on 2024 test year).
        """
        if target_years is None:
            target_years = FORECAST_YEARS

        # --- Demand ---
        d_models, d_metrics, d_feat_df = self._train_and_evaluate(demand_series)
        d_best = self._best_model_name(d_metrics)
        logger.info("Demand best model: %s (RMSE=%.2f)", d_best,
                    d_metrics.get(d_best, ModelMetrics(d_best, 0, 0, 0, 0)).rmse)

        # --- Supply ---
        s_models, s_metrics, s_feat_df = self._train_and_evaluate(supply_series)
        s_best = self._best_model_name(s_metrics)
        logger.info("Supply best model: %s (RMSE=%.2f)", s_best,
                    s_metrics.get(s_best, ModelMetrics(s_best, 0, 0, 0, 0)).rmse)

        # Iterative forecast
        d_preds = self._iterative_forecast(d_models, d_feat_df, target_years)
        s_preds = self._iterative_forecast(s_models, s_feat_df, target_years)

        # Residual std for CI estimation (from training residuals)
        def _residual_std(fitted_models: Dict, feat_df: pd.DataFrame, best: str) -> float:
            train_df  = feat_df[feat_df["year"].isin(TRAIN_YEARS)].dropna()
            if train_df.empty or best not in fitted_models:
                return 0.0
            X_tr = train_df[self._feature_cols()].values
            y_tr = train_df["value"].values
            resid = y_tr - fitted_models[best].predict(X_tr)
            return float(np.std(resid))

        d_std = _residual_std(d_models, d_feat_df, d_best)
        s_std = _residual_std(s_models, s_feat_df, s_best)

        points: List[ForecastPoint] = []
        for year in sorted(target_years):
            pred_d = d_preds[d_best].get(year, 0.0)
            pred_s = s_preds[s_best].get(year, 0.0)
            # Use demand std for CI (representative of overall uncertainty)
            margin = CI_MULTIPLIER * d_std
            points.append(
                ForecastPoint(
                    year=year,
                    predicted_demand=round(pred_d, 2),
                    predicted_supply=round(pred_s, 2),
                    lower_ci=round(pred_d - margin, 2),
                    upper_ci=round(pred_d + margin, 2),
                    model_name=d_best,
                )
            )

        return points

    def compare_models(
        self,
        demand_series: pd.Series,
        include_naive: bool = True,
    ) -> List[ModelComparisonPoint]:
        """
        Train all models and return side-by-side predictions for every year
        in TRAIN_YEARS + TEST_YEARS + FORECAST_YEARS, alongside real metrics
        on the TEST_YEARS split.

        Parameters
        ----------
        demand_series  : pd.Series  – year-indexed demand figures
        include_naive  : bool       – whether to include the statsmodels naive baseline

        Returns
        -------
        List[ModelComparisonPoint]
        """
        feat_df = _build_features(demand_series)
        train_df, test_df = self._split_train_test(feat_df)

        feat_cols = self._feature_cols()
        X_train   = train_df[feat_cols].values
        y_train   = train_df["value"].values

        fitted: Dict[str, object] = {}
        metrics_map: Dict[str, ModelMetrics] = {}

        for name, model in self._models.items():
            try:
                model.fit(X_train, y_train)
                fitted[name] = model
                if not test_df.empty:
                    y_pred = model.predict(test_df[feat_cols].values)
                    metrics_map[name] = _compute_metrics(name, test_df["value"].values, y_pred)
            except Exception as exc:
                logger.error("compare_models: %s failed – %s", name, exc)

        # Naive baseline
        if include_naive:
            naive_train_preds = _naive_forecast(train_df, list(train_df["year"].values))
            naive_test_preds  = _naive_forecast(train_df, list(test_df["year"].values)) if not test_df.empty else np.array([])
            if not test_df.empty and len(naive_test_preds):
                metrics_map["NaiveBaseline"] = _compute_metrics(
                    "NaiveBaseline", test_df["value"].values, naive_test_preds
                )

        all_years: List[int] = (
            sorted(set(TRAIN_YEARS + TEST_YEARS + FORECAST_YEARS))
        )

        # Iterative predictions for all models
        ml_preds = self._iterative_forecast(fitted, feat_df, all_years)

        # Naive forecasts over all years
        naive_all: Dict[int, float] = {}
        if include_naive:
            naive_vals = _naive_forecast(train_df, all_years)
            naive_all  = dict(zip(all_years, naive_vals.tolist()))

        # Build actuals lookup
        actuals: Dict[int, float] = dict(
            zip(feat_df["year"].astype(int), feat_df["value"])
        )

        comparison: List[ModelComparisonPoint] = []
        for year in all_years:
            preds: Dict[str, float] = {}
            for name, yr_map in ml_preds.items():
                preds[name] = round(yr_map.get(year, float("nan")), 2)
            if include_naive:
                preds["NaiveBaseline"] = round(naive_all.get(year, float("nan")), 2)

            # Attach metrics only for TEST_YEARS rows
            row_metrics: Optional[ModelMetrics] = None
            if year in TEST_YEARS:
                best_name = self._best_model_name(metrics_map)
                row_metrics = metrics_map.get(best_name)

            comparison.append(
                ModelComparisonPoint(
                    year=year,
                    actual=actuals.get(year),
                    predictions=preds,
                    metrics=row_metrics,
                )
            )

        return comparison

    def get_model_metrics(
        self,
        demand_series: pd.Series,
    ) -> Dict[str, ModelMetrics]:
        """
        Return a dict of ModelMetrics for every model, evaluated on the
        2024 test split.

        Parameters
        ----------
        demand_series : pd.Series – year-indexed demand figures

        Returns
        -------
        Dict[str, ModelMetrics]
        """
        _, metrics_map, _ = self._train_and_evaluate(demand_series)
        return metrics_map


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

forecasting_engine: ForecastingEngine = ForecastingEngine()
