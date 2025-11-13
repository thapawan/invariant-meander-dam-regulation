"""
Invariant Meander Migration Under Dam Regulation

This package provides tools to analyze meander migration patterns
and demonstrate that dam regulation suppresses migration rates while
preserving the geometric template of erosion.
"""

from . import meander_analysis
from . import lme_model
from . import visualization
from . import data_generator

__version__ = "1.0.0"
__all__ = [
    "meander_analysis",
    "lme_model",
    "visualization",
    "data_generator"
]
