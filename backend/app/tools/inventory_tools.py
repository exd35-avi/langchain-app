from langchain.tools import tool
from ..data_loader import get_inventory, get_sales, get_suppliers
import pandas as pd
@tool
def get_current_stock(sku: str = None, product_name: str = None) -> str:
    df = get_inventory()
    if sku:
        row = df[df['sku'] == sku]
        if row.empty: return f"SKU {sku} not found."
        p = row.iloc[0]
        status = "⚠️ LOW STOCK" if p['current_stock'] <= p['reorder_level'] else "OK"
        return f"{p['product_name']} ({p['sku']}): {p['current_stock']} units. Reorder at {p['reorder_level']}. Status: {status}"
    elif product_name:
        matches = df[df['product_name'].str.contains(product_name, case=False)]
        if matches.empty: return f"No product named '{product_name}'"
        result = f"Products matching '{product_name}':\n"
        for _, r in matches.iterrows():
            result += f"- {r['product_name']} ({r['sku']}): {r['current_stock']} units\n"
        return result
    else:
        low = df[df['current_stock'] <= df['reorder_level']]
        if low.empty: return "All products have sufficient stock."
        result = "⚠️ Low stock items:\n"
        for _, r in low.iterrows():
            result += f"- {r['product_name']} ({r['sku']}): {r['current_stock']} / {r['reorder_level']}\n"
        return result
@tool
def get_sales_trend(sku: str, days: int = 30) -> str:
    sales = get_sales()
    if sku not in sales['sku'].unique(): return f"SKU {sku} not found."
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    filtered = sales[(sales['sku'] == sku) & (sales['sale_date'] >= cutoff)]
    total = filtered['quantity'].sum()
    product = get_inventory()[get_inventory()['sku'] == sku]['product_name'].values[0]
    return f"Sales for {product} in last {days} days: {total} units. Daily avg: {total/days:.1f}"
@tool
def recommend_reorder(sku: str = None) -> str:
    inv = get_inventory()
    sup = get_suppliers()
    if sku:
        prod = inv[inv['sku'] == sku]
        if prod.empty: return f"SKU {sku} not found."
        supplier = sup[sup['sku'] == sku]
        if supplier.empty: return f"No supplier for {sku}"
        row = prod.iloc[0]
        lead = supplier.iloc[0]['lead_time_days']
        reorder_point = row['reorder_level']
        current = row['current_stock']
        if current <= reorder_point:
            needed = max(supplier.iloc[0]['min_order_qty'], (reorder_point - current) + row['safety_stock'])
            urgency = "CRITICAL" if current <= reorder_point * 0.5 else "NORMAL"
            return f"Recommend order for {row['product_name']}: {needed} units.\nCurrent: {current}, Reorder at: {reorder_point}, Lead time: {lead} days. Urgency: {urgency}"
        else:
            return f"{row['product_name']} stock is adequate."
    else:
        low = inv[inv['current_stock'] <= inv['reorder_level']]
        if low.empty: return "No products need reordering."
        result = "Products needing reorder:\n"
        for _, r in low.iterrows():
            result += f"- {r['product_name']} ({r['sku']}): {r['current_stock']} left\n"
        return result
