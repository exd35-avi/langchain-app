import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

os.makedirs('dataset', exist_ok=True)
np.random.seed(42)
random.seed(42)

products = []
for i in range(1, 51):
    sku = f"SKU{i:03d}"
    cat = random.choice(['Electronics', 'Accessories', 'Cables', 'Audio', 'Wearables'])
    price = round(random.uniform(9.99, 299.99), 2)
    reorder_level = random.randint(10, 50)
    current_stock = random.randint(0, 200)
    products.append({
        'sku': sku,
        'product_name': f"Product_{i}",
        'category': cat,
        'unit_price': price,
        'current_stock': current_stock,
        'reorder_level': reorder_level,
        'safety_stock': random.randint(5, 20),
        'location': random.choice(['WH-A', 'WH-B', 'Store1', 'Store2'])
    })
products_df = pd.DataFrame(products)
products_df.to_csv('dataset/inventory.csv', index=False)
print(f"✅ inventory.csv: {len(products_df)} SKUs")

suppliers = []
for sku in products_df['sku']:
    suppliers.append({
        'sku': sku,
        'supplier_name': f"Supplier_{random.randint(1,20)}",
        'lead_time_days': random.randint(2, 14),
        'min_order_qty': random.randint(10, 100),
        'price_per_unit': round(products_df[products_df['sku']==sku]['unit_price'].values[0] * 0.85, 2),
        'reliability': round(random.uniform(0.7, 0.99), 2)
    })
suppliers_df = pd.DataFrame(suppliers)
suppliers_df.to_csv('dataset/suppliers.csv', index=False)
print(f"✅ suppliers.csv: {len(suppliers_df)} records")

start_date = datetime(2024, 1, 1)
end_date = datetime.now()
date_range = pd.date_range(start_date, end_date, freq='D')
sales_records = []
for sku in products_df['sku']:
    base_daily = random.uniform(0.5, 10)
    for date in date_range:
        month = date.month
        if month == 12:
            multiplier = 2.5
        elif month == 11:
            multiplier = 1.8
        elif date.weekday() >= 5:
            multiplier = 1.3
        else:
            multiplier = 1.0
        qty = int(np.random.poisson(base_daily * multiplier))
        if qty > 0:
            sales_records.append({
                'sale_id': f"{sku}_{date.strftime('%Y%m%d')}_{random.randint(100,999)}",
                'sku': sku,
                'sale_date': date.strftime('%Y-%m-%d'),
                'quantity': qty,
                'unit_price': products_df[products_df['sku']==sku]['unit_price'].values[0],
                'total': qty * products_df[products_df['sku']==sku]['unit_price'].values[0]
            })
sales_df = pd.DataFrame(sales_records)
if len(sales_df) < 10000:
    extra = sales_df.sample(n=10000 - len(sales_df), replace=True)
    sales_df = pd.concat([sales_df, extra], ignore_index=True)
sales_df.to_csv('dataset/sales_history.csv', index=False)
print(f"✅ sales_history.csv: {len(sales_df):,} records")
print("\n🎉 Large dataset generated!")
