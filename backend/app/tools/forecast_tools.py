from langchain.tools import tool
from ..services.ml_forecast import ml_forecast
from ..data_loader import get_inventory
@tool
def ml_demand_forecast(sku: str, days: int = 30) -> str:
    """Predict future demand using Random Forest ML model."""
    inv = get_inventory()
    product = inv[inv['sku'] == sku]
    if product.empty:
        return f"SKU {sku} not found."
    product_name = product.iloc[0]['product_name']
    forecast = ml_forecast.forecast(sku, days)
    if not forecast:
        return f"Could not generate forecast for {sku}."
    response = f"""📈 **ML Demand Forecast for {product_name} (SKU: {sku})**

**Next {days} days:**
• Total predicted demand: {forecast['total_forecast']} units
• Daily average: {forecast['avg_daily']} units/day
• Method used: {forecast['method']}

**Confidence Interval (95%):**
• Lower bound: {forecast['confidence_lower']} units
• Upper bound: {forecast['confidence_upper']} units

**Disclaimer:** This prediction is based on historical patterns and may vary due to market changes, promotions, or external factors. Always monitor actual sales.

**Action:** {'⚠️ Consider increasing safety stock or reordering soon.' if forecast['total_forecast'] > product.iloc[0]['current_stock'] else '✓ Current stock may suffice, but keep monitoring.'}
"""
    return response
@tool
def predict_stockout_risk(sku: str, days: int = 7) -> str:
    """Predict probability of stockout within given days."""
    inv = get_inventory()
    product = inv[inv['sku'] == sku]
    if product.empty:
        return f"SKU {sku} not found."
    prob = ml_forecast.predict_stockout(sku, days)
    if prob is None:
        return f"Unable to predict stockout for {sku}."
    risk = "HIGH" if prob > 0.7 else "MEDIUM" if prob > 0.3 else "LOW"
    response = f"""⚠️ **Stockout Risk Analysis for {product.iloc[0]['product_name']}**

• Timeframe: next {days} days
• Probability of stockout: **{prob*100:.1f}%**
• Risk level: {risk}

**Recommendation:** 
{'Immediate reorder recommended.' if prob > 0.7 else 'Consider placing a reorder soon.' if prob > 0.3 else 'Stock levels appear safe for now.'}

*Note: This prediction uses ML and historical demand variability.*
"""
    return response
