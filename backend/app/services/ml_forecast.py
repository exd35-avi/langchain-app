import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import os
from datetime import datetime, timedelta
from ..data_loader import get_sales, get_inventory

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

class DemandForecastML:
    def __init__(self):
        self.models = {}
        self.train_all_models()
    
    def _create_features(self, df):
        df = df.copy()
        df['day_of_week'] = pd.to_datetime(df['sale_date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['sale_date']).dt.month
        df['day_of_month'] = pd.to_datetime(df['sale_date']).dt.day
        df['week_of_year'] = pd.to_datetime(df['sale_date']).dt.isocalendar().week
        df = df.sort_values('sale_date')
        df['lag_1'] = df['quantity'].shift(1).fillna(0)
        df['lag_7'] = df['quantity'].shift(7).fillna(0)
        df['rolling_mean_7'] = df['quantity'].rolling(7, min_periods=1).mean().fillna(0)
        return df
    
    def train_model_for_sku(self, sku):
        sales = get_sales()
        sku_sales = sales[sales['sku'] == sku].copy()
        if len(sku_sales) < 30:
            return None
        sku_sales = self._create_features(sku_sales)
        features = ['day_of_week', 'month', 'day_of_month', 'week_of_year', 'lag_1', 'lag_7', 'rolling_mean_7']
        X = sku_sales[features].values
        y = sku_sales['quantity'].values
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
        ])
        pipeline.fit(X, y)
        self.models[sku] = pipeline
        return pipeline
    
    def train_all_models(self):
        sales = get_sales()
        skus = sales['sku'].unique()
        for sku in skus:
            try:
                self.train_model_for_sku(sku)
                print(f"Trained model for {sku}")
            except Exception as e:
                print(f"Failed to train for {sku}: {e}")
    
    def forecast(self, sku, days=30):
        if sku not in self.models:
            return self._simple_forecast(sku, days)
        model = self.models[sku]
        sales = get_sales()
        sku_sales = sales[sales['sku'] == sku].copy()
        if len(sku_sales) == 0:
            return self._simple_forecast(sku, days)
        last_date = pd.to_datetime(sku_sales['sale_date'].max())
        future_dates = [last_date + timedelta(days=i) for i in range(1, days+1)]
        last_row = self._create_features(sku_sales).iloc[-1:].copy()
        predictions = []
        for i, future_date in enumerate(future_dates):
            feat = {
                'day_of_week': future_date.weekday(),
                'month': future_date.month,
                'day_of_month': future_date.day,
                'week_of_year': future_date.isocalendar().week,
                'lag_1': last_row['quantity'].values[0] if i == 0 else predictions[-1],
                'lag_7': last_row['lag_7'].values[0] if i < 7 else predictions[-7],
                'rolling_mean_7': np.mean(predictions[-7:]) if len(predictions) >= 7 else last_row['rolling_mean_7'].values[0]
            }
            X_pred = np.array([[feat['day_of_week'], feat['month'], feat['day_of_month'], 
                               feat['week_of_year'], feat['lag_1'], feat['lag_7'], feat['rolling_mean_7']]])
            pred = model.predict(X_pred)[0]
            predictions.append(max(0, int(round(pred))))
        total = sum(predictions)
        avg_daily = total / days
        if hasattr(model.named_steps['regressor'], 'estimators_'):
            tree_preds = np.array([tree.predict(model.named_steps['scaler'].transform(X_pred)) for tree in model.named_steps['regressor'].estimators_])
            std = np.std(tree_preds)
            lower = max(0, int(total - 1.96 * std * days))
            upper = int(total + 1.96 * std * days)
        else:
            lower = max(0, int(total * 0.8))
            upper = int(total * 1.2)
        return {
            'total_forecast': total,
            'avg_daily': round(avg_daily, 1),
            'daily_predictions': predictions,
            'confidence_lower': lower,
            'confidence_upper': upper,
            'method': 'ML (RandomForest)'
        }
    
    def _simple_forecast(self, sku, days):
        sales = get_sales()
        sku_sales = sales[sales['sku'] == sku]
        if len(sku_sales) < 7:
            avg = 5
        else:
            avg = sku_sales['quantity'].tail(30).mean()
        total = avg * days
        return {
            'total_forecast': int(total),
            'avg_daily': round(avg, 1),
            'daily_predictions': [int(avg)] * days,
            'confidence_lower': max(0, int(total * 0.7)),
            'confidence_upper': int(total * 1.3),
            'method': 'Simple Average (fallback)'
        }
    
    def predict_stockout(self, sku, days=7):
        inv = get_inventory()
        prod = inv[inv['sku'] == sku]
        if prod.empty:
            return None
        current_stock = prod.iloc[0]['current_stock']
        forecast = self.forecast(sku, days)
        demand = forecast['total_forecast']
        if current_stock <= 0:
            return 1.0
        if demand >= current_stock:
            prob = min(1.0, demand / current_stock)
        else:
            prob = 0.0
        prob = min(1.0, prob * 1.2)
        return round(prob, 2)

ml_forecast = DemandForecastML()
