"""Educational privacy-preserving data-sharing reference implementation.

This package demonstrates concepts and is not a production or end-to-end
security system.
"""

from .anonymity import k_anonymity_report
from .differential import dp_mean
from .transform import transform_records

__all__ = ["dp_mean", "k_anonymity_report", "transform_records"]

__version__ = "0.1.0"
