"""
03_generate_report.py
--------------------
Creates a recruiter-friendly Markdown report + a few key charts.

Outputs:
- reports/report.md
- reports/figures/*.png
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    raw_path = project_root / "data" / "raw" / "transactions_raw.csv"
    seg_path = project_root / "data" / "processed" / "outlet_cltv_segments.csv"
    fig_dir = project_root / "reports" / "figures"
    report_path = project_root / "reports" / "report.md"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path, parse_dates=["transaction_date"])
    seg = pd.read_csv(seg_path)

    # Feature engineering
    df["dow"] = df["transaction_date"].dt.day_name()
    df["is_weekend"] = df["transaction_date"].dt.dayofweek.isin([5, 6])

    # Chart 1: Revenue by day of week
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    revenue_by_dow = df.groupby("dow")["net_revenue_zar"].sum().reindex(dow_order)
    plt.figure()
    revenue_by_dow.plot(kind="bar")
    plt.title("Revenue by Day of Week")
    plt.xlabel("Day")
    plt.ylabel("Net Revenue (ZAR)")
    plt.tight_layout()
    fig1 = fig_dir / "revenue_by_day_of_week.png"
    plt.savefig(fig1, dpi=160)
    plt.close()

    # Chart 2: Outlet segments count
    seg_counts = seg["segment"].value_counts().sort_values(ascending=False)
    plt.figure()
    seg_counts.plot(kind="bar")
    plt.title("Outlet Segment Distribution")
    plt.xlabel("Segment")
    plt.ylabel("Number of Outlets")
    plt.tight_layout()
    fig2 = fig_dir / "segment_distribution.png"
    plt.savefig(fig2, dpi=160)
    plt.close()

    # Chart 3: CLTV proxy by outlet type (box-like using quantiles -> bar)
    cltv_stats = seg.groupby("outlet_type")["cltv_proxy"].quantile([0.25, 0.5, 0.75]).unstack()
    plt.figure()
    cltv_stats[0.5].sort_values(ascending=False).plot(kind="bar")
    plt.title("Median CLTV Proxy by Outlet Type")
    plt.xlabel("Outlet Type")
    plt.ylabel("Median CLTV Proxy (ZAR)")
    plt.tight_layout()
    fig3 = fig_dir / "median_cltv_by_outlet_type.png"
    plt.savefig(fig3, dpi=160)
    plt.close()

    # Top insights
    total_rev = df["net_revenue_zar"].sum()
    weekend_rev = df.loc[df["is_weekend"], "net_revenue_zar"].sum()
    weekend_share = weekend_rev / total_rev if total_rev else 0

    top10 = seg.sort_values("cltv_proxy", ascending=False).head(10)[
        ["outlet_id", "outlet_type", "province", "city", "wholesaler_region", "revenue", "tickets_per_month", "avg_aov", "cltv_proxy", "segment"]
    ]

    # Build report
    report = []
    report.append("# Alcohol Retail & Tavern Performance Intelligence (Purchase Frequency + CLTV)\n")
    report.append("## Executive summary\n")
    report.append(f"- **Total net revenue (synthetic 2025):** ZAR {total_rev:,.0f}\n")
    report.append(f"- **Weekend share of revenue:** {weekend_share:.1%} (captures the *weekend economy*)\n")
    report.append(f"- **Top-value outlets:** a small subset of outlets dominate CLTV proxy; segmenting them makes account prioritisation easy.\n")

    report.append("## Key charts\n")
    report.append(f"![Revenue by Day of Week](figures/{fig1.name})\n")
    report.append(f"![Outlet Segment Distribution](figures/{fig2.name})\n")
    report.append(f"![Median CLTV by Outlet Type](figures/{fig3.name})\n")

    report.append("## Segmentation logic (simple + defensible)\n")
    report.append("- **Cash Cows:** high revenue and high purchase frequency\n")
    report.append("- **Weekend Economy:** high frequency with strong weekend dependency\n")
    report.append("- **Occasional Big Spenders:** lower frequency but high average order value\n")
    report.append("- **At-Risk / Low Activity:** low activity and shorter observed lifespan\n")
    report.append("- **Core / Mid-Tier:** stable middle\n")

    report.append("## Top 10 outlets by CLTV proxy\n")
    report.append(top10.to_markdown(index=False))
    report.append("\n")

    report_path.write_text("\n".join(report), encoding="utf-8")

    print(f"✅ Wrote: {report_path}")
    print(f"✅ Figures: {fig1.name}, {fig2.name}, {fig3.name}")

if __name__ == "__main__":
    main()
