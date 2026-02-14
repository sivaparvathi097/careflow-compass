"""
Machine Learning module for CareFlow AI.
Provides bed availability prediction using historical data patterns.
"""

from app.ml.bed_predictor import BedPredictor, bed_predictor
from app.ml.data_generator import HistoricalDataGenerator

__all__ = ["BedPredictor", "bed_predictor", "HistoricalDataGenerator"]
