## Threshold distance values for filtering results
from typing import Final

SMALL_CUTOFF_THRESHOLD: Final = 0.05
MEDIUM_CUTOFF_THRESHOLD: Final = 0.1
YUGE_CUTOFF_THRESHOLD: Final = 0.3

VALID_THRESHOLDS: Final = {
    "small": SMALL_CUTOFF_THRESHOLD,
    "medium": MEDIUM_CUTOFF_THRESHOLD,
    "yuge": YUGE_CUTOFF_THRESHOLD,
}
