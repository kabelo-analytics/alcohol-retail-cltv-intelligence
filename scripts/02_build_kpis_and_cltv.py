"""
02_build_kpis_and_cltv.py
------------------------
Builds outlet KPIs + pragmatic CLTV-style value scoring and segmentation.

Outputs:
- data/processed/outlet_monthly_kpis.csv
- data/processed/outlet_cltv_segments.csv
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 753

def main() -> None:
    np.random.seed(SEED)

    project_root = Path(__file__).resolve().parents[1]
    raw_path = project_root / "data" / "raw" / "transactions_raw.csv"
    out_kpis = project_root / "data" / "processed" / "outlet_monthly_kpis.csv"
    out_seg = project_root / "data" / "processed" / "outlet_cltv_segments.csv"
    out_kpis.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path, parse_dates=["transaction_date"])

    # Basic cleanup / types
    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)
    df["is_weekend"] = df["transaction_date"].dt.dayofweek.isin([5, 6]).astype(int)

    # Ticket-level approximation: treat each line as a ticket (good enough for a portfolio)
    # KPI aggregates per outlet per month
    agg = df.groupby(["outlet_id", "outlet_type", "province", "city", "wholesaler_region", "month"], as_index=False).agg(
        tickets=("transaction_id", "nunique"),
        units=("quantity_units", "sum"),
        revenue=("net_revenue_zar", "sum"),
        weekend_revenue=("net_revenue_zar", lambda s: s[df.loc[s.index, "is_weekend"] == 1].sum()),
        promo_revenue=("net_revenue_zar", lambda s: s[df.loc[s.index, "promotion_type"] != "None"].sum()),
    )

    agg["aov"] = (agg["revenue"] / agg["tickets"]).replace([np.inf, -np.inf], np.nan)
    agg["rev_per_unit"] = (agg["revenue"] / agg["units"]).replace([np.inf, -np.inf], np.nan)
    agg["weekend_share"] = (agg["weekend_revenue"] / agg["revenue"]).fillna(0.0)
    agg["promo_share"] = (agg["promo_revenue"] / agg["revenue"]).fillna(0.0)

    # Outlet-level rollup across the year
    outlet = agg.groupby(["outlet_id", "outlet_type", "province", "city", "wholesaler_region"], as_index=False).agg(
        months_active=("month", "nunique"),
        tickets=("tickets", "sum"),
        units=("units", "sum"),
        revenue=("revenue", "sum"),
        avg_aov=("aov", "mean"),
        avg_weekend_share=("weekend_share", "mean"),
        avg_promo_share=("promo_share", "mean"),
    )

    # Purchase frequency proxy: tickets per active month
    outlet["tickets_per_month"] = outlet["tickets"] / outlet["months_active"].clip(lower=1)

    # Pragmatic CLTV score (portfolio-friendly)
    # CLTV ≈ (AOV * purchase_frequency) * expected_months_active
    # We use observed months_active as proxy for expected duration.
    outlet["cltv_proxy"] = outlet["avg_aov"] * outlet["tickets_per_month"] * outlet["months_active"]

    # Robust scaling for segment thresholds
    q_rev = outlet["revenue"].quantile([0.25, 0.5, 0.75]).to_dict()
    q_freq = outlet["tickets_per_month"].quantile([0.25, 0.5, 0.75]).to_dict()
    q_aov = outlet["avg_aov"].quantile([0.25, 0.5, 0.75]).to_dict()

    def segment(row: pd.Series) -> str:
        high_rev = row["revenue"] >= q_rev[0.75]
        high_freq = row["tickets_per_month"] >= q_freq[0.75]
        high_aov = row["avg_aov"] >= q_aov[0.75]

        if high_rev and high_freq:
            return "Cash Cows"
        if high_freq and row["avg_weekend_share"] >= 0.55:
            return "Weekend Economy"
        if (not high_freq) and high_aov:
            return "Occasional Big Spenders"
        if row["months_active"] <= 6 and row["tickets_per_month"] <= q_freq[0.25]:
            return "At-Risk / Low Activity"
        return "Core / Mid-Tier"

    outlet["segment"] = outlet.apply(segment, axis=1)

    # Export
    agg.to_csv(out_kpis, index=False)
    outlet.to_csv(out_seg, index=False)

    print(f"✅ Wrote: {out_kpis}")
    print(f"✅ Wrote: {out_seg}")
    print(f"Outlets: {len(outlet):,} | Raw rows: {len(df):,}")

if __name__ == "__main__":
    main()
