from langchain.tools import tool
import uuid
from datetime import datetime
orders = []
@tool
def create_purchase_order(sku: str, quantity: int) -> str:
    from ..data_loader import get_inventory, get_suppliers
    inv = get_inventory()
    sup = get_suppliers()
    prod = inv[inv['sku'] == sku]
    if prod.empty: return f"SKU {sku} not found."
    supplier = sup[sup['sku'] == sku]
    if supplier.empty: return f"No supplier for {sku}"
    name = prod.iloc[0]['product_name']
    price = supplier.iloc[0]['price_per_unit']
    oid = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    orders.append({'order_id': oid, 'sku': sku, 'product': name, 'quantity': quantity, 'total': quantity * price, 'status': 'pending'})
    return f"✅ Purchase order created: {oid}\nProduct: {name}, Qty: {quantity}, Total: ${quantity * price:.2f}\nStatus: pending"
