"""Analytics service passthrough (domain owns the calculations, §38.8)."""
from signalcraft.analytics import (
    insights,
    performance_score,
    record_performance,
    summary,
)

__all__ = ["insights", "performance_score", "record_performance", "summary"]
