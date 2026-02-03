"""
01_generate_synthetic_data.py
----------------------------
Generates a South Africa-style alcohol route-to-market sales dataset (synthetic).

Outputs:
- data/raw/transactions_raw.csv
- docs/data_dictionary.json
"""

import json
import math
import random
import datetime
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 753

def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)

    project_root = Path(__file__).resolve().parents[1]
    out_raw = project_root / "data" / "raw" / "transactions_raw.csv"
    out_dict = project_root / "docs" / "data_dictionary.json"
    out_raw.parent.mkdir(parents=True, exist_ok=True)
    out_dict.parent.mkdir(parents=True, exist_ok=True)

    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    days = (end_date - start_date).days + 1
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]

    provinces = [
        ("Gauteng", ["Johannesburg", "Pretoria", "Soweto", "Tembisa"]),
        ("Western Cape", ["Cape Town", "Bellville", "Khayelitsha"]),
        ("KwaZulu-Natal", ["Durban", "Pietermaritzburg", "Umlazi"]),
        ("Eastern Cape", ["Gqeberha", "Mdantsane"]),
        ("Free State", ["Bloemfontein"]),
        ("Limpopo", ["Polokwane"]),
    ]

    outlet_types = ["Tavern", "Liquor Store", "Supermarket", "Bottle Store"]
    wholesaler_regions = ["North Hub", "South Hub", "Coastal Hub"]
    categories = ["Beer", "Cider", "Spirits", "RTD"]
    brands = {
        "Beer": ["Castle Lager", "Black Label", "Heineken", "Carling", "Amstel"],
        "Cider": ["Savanna", "Hunters", "Strongbow"],
        "Spirits": ["Vodka", "Whisky", "Brandy", "Gin"],
        "RTD": ["Flying Fish", "Smirnoff Storm", "Brutal Fruit", "Corona Sunbrew (NA)"]
    }
    pack_sizes = ["330ml", "500ml", "750ml", "1L"]
    promo_flags = ["None", "Price Promo", "Bundle", "POS Display"]

    # Create outlets
    n_outlets = 420
    outlets = []
    for i in range(n_outlets):
        prov, cities = random.choice(provinces)
        city = random.choice(cities)
        otype = random.choices(outlet_types, weights=[0.45, 0.25, 0.2, 0.10], k=1)[0]
        wholesaler = random.choice(wholesaler_regions)
        outlets.append({
            "outlet_id": f"O{str(i+1).zfill(4)}",
            "outlet_type": otype,
            "province": prov,
            "city": city,
            "wholesaler_region": wholesaler
        })
    outlets_df = pd.DataFrame(outlets)

    def is_weekend(d: datetime.date) -> bool:
        return d.weekday() >= 5

    def season_multiplier(d: datetime.date) -> float:
        if d.month in (11, 12):
            return 1.25
        if d.month in (2, 3):
            return 0.90
        if d.month in (6, 7):
            return 1.05
        return 1.0

    base_price = {
        "Beer": 18.0,
        "Cider": 22.0,
        "Spirits": 120.0,
        "RTD": 28.0
    }
    size_multiplier = {"330ml": 1.0, "500ml": 1.35, "750ml": 1.9, "1L": 2.3}

    rows = []
    txn_id = 1

    for d in dates:
        weekend = is_weekend(d)
        season = season_multiplier(d)
        month_end = d.day >= 25
        promo_chance = 0.18 + (0.10 if weekend else 0.0) + (0.05 if month_end else 0.0)

        active_fraction = 0.38 + (0.10 if weekend else 0.0)
        active_outlets = outlets_df.sample(frac=active_fraction, random_state=hash(d) % (2**32))

        for _, o in active_outlets.iterrows():
            lam = {"Tavern": 6.5, "Liquor Store": 4.0, "Supermarket": 2.8, "Bottle Store": 3.2}[o["outlet_type"]]
            lam *= (1.25 if weekend and o["outlet_type"] == "Tavern" else 1.0)
            lam *= season

            n_tickets = int(max(0, min(np.random.poisson(lam), 25)))

            for _t in range(n_tickets):
                cat = random.choices(categories, weights=[0.55, 0.18, 0.17, 0.10], k=1)[0]
                brand = random.choice(brands[cat])
                size = random.choices(pack_sizes, weights=[0.55, 0.25, 0.13, 0.07], k=1)[0]

                promo = "None"
                discount = 0.0
                if random.random() < promo_chance:
                    promo = random.choices(promo_flags[1:], weights=[0.55, 0.30, 0.15], k=1)[0]
                    discount = random.choice([0.05, 0.08, 0.10, 0.12, 0.15])

                qty_base = {"Beer": 8, "Cider": 6, "Spirits": 1, "RTD": 5}[cat]
                if o["outlet_type"] == "Tavern":
                    qty_base *= 1.4
                elif o["outlet_type"] == "Supermarket":
                    qty_base *= 1.1

                qty = max(1, int(np.random.lognormal(mean=math.log(qty_base), sigma=0.45)))
                qty = min(qty, 120 if cat != "Spirits" else 12)

                unit_price = base_price[cat] * size_multiplier[size]
                unit_price *= np.random.normal(1.0, 0.06)
                unit_price = max(5.0, round(unit_price, 2))

                gross = unit_price * qty
                net = round(gross * (1.0 - discount), 2)

                rows.append({
                    "transaction_id": f"T{str(txn_id).zfill(8)}",
                    "transaction_date": d.isoformat(),
                    "outlet_id": o["outlet_id"],
                    "outlet_type": o["outlet_type"],
                    "province": o["province"],
                    "city": o["city"],
                    "wholesaler_region": o["wholesaler_region"],
                    "product_category": cat,
                    "brand": brand,
                    "pack_size": size,
                    "quantity_units": qty,
                    "unit_price_zar": unit_price,
                    "promotion_type": promo,
                    "discount_pct": round(discount, 2),
                    "net_revenue_zar": net
                })
                txn_id += 1

    txns = pd.DataFrame(rows)
    txns.to_csv(out_raw, index=False)

    data_dict = {
        "transactions_raw.csv": {
            "transaction_id": "Unique transaction line identifier.",
            "transaction_date": "ISO date of the transaction.",
            "outlet_id": "Unique outlet identifier.",
            "outlet_type": "Outlet type: Tavern, Liquor Store, Supermarket, Bottle Store.",
            "province": "South African province (synthetic assignment).",
            "city": "City / township / area (synthetic assignment).",
            "wholesaler_region": "Distribution hub region serving the outlet.",
            "product_category": "Beer, Cider, Spirits, RTD.",
            "brand": "Synthetic mix of global/local style brands within category.",
            "pack_size": "Pack size label for pricing scaling.",
            "quantity_units": "Number of units purchased (line quantity).",
            "unit_price_zar": "Unit price (ZAR).",
            "promotion_type": "None / Price Promo / Bundle / POS Display.",
            "discount_pct": "Discount applied (0–0.15).",
            "net_revenue_zar": "Net revenue after discount."
        }
    }

    out_dict.write_text(json.dumps(data_dict, indent=2), encoding="utf-8")
    print(f"✅ Wrote: {out_raw}")
    print(f"✅ Wrote: {out_dict}")
    print(f"Rows: {len(txns):,}")

if __name__ == "__main__":
    main()
