"""Append Revision 2.1 correction rows to the Visium run log.

No model is run. Existing rows are never rewritten; this only appends the
old -> new values for the re-review corrections.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import log_run  # noqa: E402

ROWS = [
    ("correction_history_files_revision21",
     "Revision 2.1: all three 6-byte header-only history CSVs verified absent "
     "(visium_c2l_mapping_history.csv, visium_c2l_mapping_history_rerun.csv, "
     "c2l_reference_training_history.csv). Revision 2 stated they were deleted "
     "but the first and third still existed. Root cause: visium_c2l_20_train_"
     "reference.py and visium_c2l_21_map_sections.py wrote hist.to_csv "
     "unconditionally; only visium_c2l_21_map_sections_rerun.py was guarded. "
     "All three writers now drop all-NaN history, write only when non-empty, "
     "and remove a stale empty file. Evidence: "
     "visium_c2l_mapping_history_README.md."),
    ("correction_depth_medians_revision21",
     "OLD changelog #4: tumour median-of-medians 7,337/3,676 (2.00x), "
     "adjacent-normal 2,326/1,945 (1.20x). NEW: 7,545.0/3,708.5 (2.03x) and "
     "2,388.0/2,083.75 (1.15x). The old values were the MEAN of the per-section "
     "median columns, not the median; mean-of-means 9,164.2/5,211.2 (1.76x) "
     "already reproduced. All-spot pooled medians 4,215/2,123 and section "
     "median-of-medians 4,471.5/2,234.25 are now stored with explicit "
     "aggregation definitions. Evidence: visium_c2l_depth_balance_summary.csv."),
]

for step, detail in ROWS:
    log_run(step=step, status="correction", detail=detail)

print(f"appended {len(ROWS)} Revision 2.1 correction rows")
