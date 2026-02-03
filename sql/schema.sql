-- Example star schema for BI / analytics
-- (Optional: useful for showing thinkin in SQL + dimensional modelling)

CREATE TABLE dim_outlet (
  outlet_id TEXT PRIMARY KEY,
  outlet_type TEXT,
  province TEXT,
  city TEXT,
  wholesaler_region TEXT
);

CREATE TABLE dim_product (
  product_key INTEGER PRIMARY KEY,
  product_category TEXT,
  brand TEXT,
  pack_size TEXT
);

CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY,
  date_value DATE,
  year INTEGER,
  month INTEGER,
  day INTEGER,
  day_name TEXT,
  is_weekend INTEGER
);

CREATE TABLE fact_sales (
  transaction_id TEXT PRIMARY KEY,
  date_key INTEGER,
  outlet_id TEXT,
  product_key INTEGER,
  quantity_units INTEGER,
  unit_price_zar REAL,
  promotion_type TEXT,
  discount_pct REAL,
  net_revenue_zar REAL,
  FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
  FOREIGN KEY (outlet_id) REFERENCES dim_outlet(outlet_id),
  FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);
