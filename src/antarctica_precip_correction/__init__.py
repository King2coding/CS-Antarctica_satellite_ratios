"""
Antarctica GPCP Precipitation Correction Package

A Python package for computing correction ratios for GPCP precipitation products 
over Antarctica using CloudSat-Antarctica climatology data.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@domain.com"

from .corrector import GPCPCorrector
from .plotting import plot_correction_ratios
from .utils import ds_swaplon, apply_filter, apply_cap

__all__ = [
    "GPCPCorrector",
    "plot_correction_ratios", 
    "ds_swaplon",
    "apply_filter",
    "apply_cap"
]
