"""Pharyngitis: McIsaac/Centor scoring with IDSA 2012-aligned recommendations."""

from .score import (
    PharyngitisFeatures,
    Recommendation,
    mcisaac_recommendation,
    mcisaac_score,
)

__all__ = [
    "PharyngitisFeatures",
    "Recommendation",
    "mcisaac_recommendation",
    "mcisaac_score",
]
