"""Community-acquired pneumonia severity: CRB-65 and CURB-65."""

from .crb_65 import (
    Crb65Features,
    Crb65Result,
    crb_65_assessment,
    crb_65_criteria,
    crb_65_score,
)
from .curb_65 import (
    Curb65Features,
    Curb65Result,
    curb_65_assessment,
    curb_65_criteria,
    curb_65_score,
)

__all__ = [
    "Crb65Features",
    "Crb65Result",
    "Curb65Features",
    "Curb65Result",
    "crb_65_assessment",
    "crb_65_criteria",
    "crb_65_score",
    "curb_65_assessment",
    "curb_65_criteria",
    "curb_65_score",
]
