import pandas as pd
import os
inventory_df = None
sales_df = None
suppliers_df = None
def load_all_data():
    global inventory_df, sales_df, suppliers_df
    base = os.path.join(os.path.dirname(__file__), '../../dataset')
    inventory_df = pd.read_csv(os.path.join(base, 'inventory.csv'))
    sales_df = pd.read_csv(os.path.join(base, 'sales_history.csv'))
    suppliers_df = pd.read_csv(os.path.join(base, 'suppliers.csv'))
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
    print(f"Loaded {len(inventory_df)} products, {len(sales_df)} sales, {len(suppliers_df)} suppliers")
def get_inventory(): return inventory_df
def get_sales(): return sales_df
def get_suppliers(): return suppliers_df
