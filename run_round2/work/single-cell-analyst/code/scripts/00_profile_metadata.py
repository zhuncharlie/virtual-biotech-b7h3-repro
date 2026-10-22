"""Profile candidate-dataset metadata parquets pulled from CELLxGENE Census."""
import sys
import pandas as pd
from pathlib import Path

META = Path(__file__).resolve().parents[2] / "data/raw/metadata"


def t(df):
    return df.astype(str)


def profile(name):
    path = META / name
    df = pd.read_parquet(path)
    print("=" * 70)
    print(name, df.shape)
    cols = {c: str(df[c].dtype) for c in df.columns}
    print("dtypes:", cols)
    print("\nDISEASE counts\n", t(df.disease).value_counts().to_string())
    print("\nASSAY counts\n", t(df.assay).value_counts().to_string())
    print("\nDONORS per disease\n", df.groupby(t(df.disease)).donor_id.nunique().to_string())
    ct = t(df.cell_type).value_counts()
    print("\nCELL TYPES (%d)\n" % len(ct), ct.to_string())
    piv = df.groupby([t(df.disease), t(df.cell_type)]).donor_id.nunique().unstack(fill_value=0)
    print("\nDONORS per disease x cell_type\n", piv.to_string())
    fib = df[t(df.cell_type).str.contains("fibro", case=False, na=False)]
    print("\nFibroblast cells:", len(fib), " donors by disease:",
          fib.groupby(t(fib.disease)).donor_id.nunique().to_dict())
    print("Donors total:", df.donor_id.nunique(), "| is_primary_data:",
          df.is_primary_data.astype(str).unique().tolist() if "is_primary_data" in df else "NA")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        profile(f)
