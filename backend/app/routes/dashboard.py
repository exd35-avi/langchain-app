from fastapi import APIRouter
from ..data_loader import get_inventory
router = APIRouter()
@router.get("/stats")
def stats():
    inv = get_inventory()
    low = len(inv[inv['current_stock'] <= inv['reorder_level']])
    total_value = (inv['current_stock'] * inv['unit_price']).sum()
    return {"total_skus": len(inv), "low_stock_count": low, "total_inventory_value": float(total_value)}
@router.get("/alerts")
def alerts():
    inv = get_inventory()
    low = inv[inv['current_stock'] <= inv['reorder_level']]
    return low[['sku', 'product_name', 'current_stock', 'reorder_level']].to_dict(orient='records')
