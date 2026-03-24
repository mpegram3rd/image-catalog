# =============================================================================
# filtering_thresholds.py - Search Result Filtering Threshold Configuration
# =============================================================================

"""
This module defines distance threshold values used to filter search results in the
image catalog system. These thresholds control how strict or lenient the similarity
matching should be when searching for images by text or image.

The thresholds are based on cosine similarity scores (0.0 to 1.0).
The threshold is applied as a distance delta between the top ranked result and all other
results to determine if the result should be filtered.
   >>> relative_distance = abs(distances[index] - initial_distance) / abs(initial_distance)
If the relative distance is greater than the threshold, the result is filtered.
"""
from typing import Final

SMALL_CUTOFF_THRESHOLD: Final = 0.05
MEDIUM_CUTOFF_THRESHOLD: Final = 0.1
HUGE_CUTOFF_THRESHOLD: Final = 0.3

VALID_THRESHOLDS: Final = {
    "small": SMALL_CUTOFF_THRESHOLD,   # Fewer search results. Less room for variability
    "medium": MEDIUM_CUTOFF_THRESHOLD, # More moderate distance variability allowed
    "huge": HUGE_CUTOFF_THRESHOLD,     # Fairly liberal distance variability allowing more results
}
