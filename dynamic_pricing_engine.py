import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Configuration ---
TOTAL_ROOMS = 100
BASE_PRICE = 150.00
DAYS_TO_FORECAST = 30

# --- 1. Data Simulation ---

def generate_historical_data():
    """Simulates historical booking data for a hotel."""
    np.random.seed(42)
    dates = [datetime.now() - timedelta(days=i) for i in range(365)]
    
    data = {
        'Date': dates,
        'Occupancy': np.clip(np.random.normal(0.75, 0.15, 365), 0.3, 0.95), # Mean 75%
        'ADR': np.clip(np.random.normal(BASE_PRICE, 25, 365), 100, 250),
        'Local_Event_Factor': np.random.choice([1.0, 1.2, 1.5], 365, p=[0.8, 0.15, 0.05]) # 20% chance of an event
    }
    df = pd.DataFrame(data)
    df['RevPAR'] = df['Occupancy'] * df['ADR']
    return df

# --- 2. Dynamic Pricing Engine Logic ---

def dynamic_pricing_forecast(historical_df):
    """Forecasts optimal price for the next 30 days based on simple rules."""
    
    forecast_data = []
    
    # Simple Model: Price is adjusted based on expected occupancy and event factor
    # Expected Occupancy is based on the average of the last 7 days
    avg_occupancy_last_week = historical_df.tail(7)['Occupancy'].mean()
    
    for i in range(1, DAYS_TO_FORECAST + 1):
        date = datetime.now() + timedelta(days=i)
        
        # Base Price
        suggested_price = BASE_PRICE
        
        # 1. Day of Week Adjustment (Higher on Weekends)
        if date.weekday() >= 4: # Friday, Saturday, Sunday
            suggested_price *= 1.15
        
        # 2. Occupancy Pressure (If expected occupancy is high, raise price)
        if avg_occupancy_last_week > 0.85:
            suggested_price *= 1.10
        elif avg_occupancy_last_week < 0.60:
            suggested_price *= 0.90
            
        # 3. Local Event Simulation (Randomly assign a high-demand event)
        event_factor = 1.0
        if random.random() < 0.1: # 10% chance of a high-demand event
            event_factor = 1.30
            
        suggested_price *= event_factor
        
        # Final calculation and capping
        suggested_price = round(np.clip(suggested_price, 100, 300), 2)
        
        forecast_data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Day_of_Week': date.strftime('%A'),
            'Expected_Occupancy_Base': round(avg_occupancy_last_week, 2),
            'Local_Event_Factor': event_factor,
            'Suggested_ADR': suggested_price
        })
        
    return pd.DataFrame(forecast_data)

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Generate Historical Data
    historical_df = generate_historical_data()
    historical_df.to_csv('historical_hotel_data.csv', index=False)
    
    # 2. Run Dynamic Pricing Engine
    forecast_df = dynamic_pricing_forecast(historical_df)
    forecast_df.to_csv('pricing_forecast.csv', index=False)
    
    # Save a sample of the forecast for the README
    forecast_df.head(10).to_markdown('pricing_forecast_sample.md')
    
    print("Dynamic Pricing Engine executed. Historical data and 30-day forecast saved.")
