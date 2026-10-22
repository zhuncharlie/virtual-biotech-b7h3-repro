"""Inspect raw Census AnnData batches before merging."""
from pathlib import Path

import anndata as ad
import numpy as np

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data/raw/h5ad"

for f in sorted(RAW.glob("batch0*.h5ad")):
    a = ad.read_h5ad(f, backed="r")
    print("=" * 70)
    print(f.name, a.shape)
    print("obs cols:", list(a.obs.columns))
    print("var cols:", list(a.var.columns))
    print("var_names head:", list(a.var_names[:5]))
    print("layers:", list(a.layers.keys()))
    x = a.X[:200]
    if hasattr(x, "data"):
        vals = x.data
        print("X sparse dtype:", x.dtype, "min", float(vals.min()), "max", float(vals.max()),
              "integer-valued:", bool(np.all(np.equal(np.mod(vals, 1), 0))))
    print("obs dtypes:\n", a.obs.dtypes.to_string())
    if "feature_name" in a.var.columns:
        print("feature_name example:", a.var["feature_name"].astype(str).head(3).tolist())
        print("MT genes:", int(a.var["feature_name"].astype(str).str.startswith("MT-").sum()))
    a.file.close()
