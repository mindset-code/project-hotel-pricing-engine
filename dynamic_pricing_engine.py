"""
Hotel Dynamic Pricing Engine — Revenue Management
Generates 2 years of historical data + 60-day forecast across 3 room types.
Factors: seasonality, day-of-week, occupancy pressure, lead time, local events.
Run: python dynamic_pricing_engine.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json, os

np.random.seed(42)

# ── Configuration ─────────────────────────────────────────────────────────────

TOTAL_ROOMS   = 120
BASE_PRICES   = {'Standard': 120, 'Deluxe': 185, 'Suite': 320}
ROOM_SHARE    = {'Standard': 0.55, 'Deluxe': 0.32, 'Suite': 0.13}
DAYS_HISTORY  = 730   # 2 years
DAYS_FORECAST = 60
START_DATE    = datetime.now() - timedelta(days=DAYS_HISTORY)

# Monthly seasonality index (1.0 = baseline)
SEASONALITY = {
    1: 0.72, 2: 0.78, 3: 0.88, 4: 0.95,
    5: 1.05, 6: 1.22, 7: 1.35, 8: 1.30,
    9: 1.10, 10: 1.00, 11: 0.82, 12: 1.15,
}

# Day-of-week premium
DOW_FACTOR = {0: 0.92, 1: 0.90, 2: 0.93, 3: 0.97, 4: 1.12, 5: 1.25, 6: 1.18}

# Event calendar (month, day) → multiplier
EVENTS = {
    (1, 1): 1.40, (2, 14): 1.20, (3, 15): 1.15, (4, 20): 1.10,
    (5, 25): 1.18, (6, 21): 1.25, (7, 4): 1.45, (8, 15): 1.30,
    (9, 22): 1.12, (10, 31): 1.20, (11, 28): 1.35, (12, 24): 1.50,
    (12, 31): 1.55,
}


# ── Historical Data ───────────────────────────────────────────────────────────

def build_historical():
    rows = []
    for d in range(DAYS_HISTORY):
        dt        = START_DATE + timedelta(days=d)
        seas      = SEASONALITY[dt.month]
        dow       = DOW_FACTOR[dt.weekday()]
        event     = EVENTS.get((dt.month, dt.day), 1.0)
        noise_occ = np.random.normal(1, 0.05)
        noise_adr = np.random.normal(1, 0.04)

        occupancy = float(np.clip(0.68 * seas * dow * noise_occ, 0.25, 0.98))
        rooms_sold = int(TOTAL_ROOMS * occupancy)

        for rtype, base in BASE_PRICES.items():
            adr    = round(base * seas * dow * event * noise_adr, 2)
            revpar = round(adr * occupancy, 2)
            rev    = round(adr * rooms_sold * ROOM_SHARE[rtype], 2)
            rows.append({
                'date':        dt.strftime('%Y-%m-%d'),
                'month':       dt.strftime('%Y-%m'),
                'day_of_week': dt.strftime('%A'),
                'room_type':   rtype,
                'occupancy':   round(occupancy, 4),
                'rooms_sold':  rooms_sold,
                'adr':         adr,
                'revpar':      revpar,
                'revenue':     rev,
                'event_factor': event,
                'season_index': seas,
            })
    return pd.DataFrame(rows)


# ── Pricing Forecast ──────────────────────────────────────────────────────────

def build_forecast(hist_df):
    # Occupancy pressure: avg last 14 days
    recent_occ = hist_df[hist_df['room_type'] == 'Standard'].tail(14)['occupancy'].mean()

    rows = []
    for i in range(1, DAYS_FORECAST + 1):
        dt       = datetime.now() + timedelta(days=i)
        seas     = SEASONALITY[dt.month]
        dow      = DOW_FACTOR[dt.weekday()]
        event    = EVENTS.get((dt.month, dt.day), 1.0)
        lead     = i  # days in advance
        lead_f   = 1.0 + max(0, (30 - lead) / 100)   # last-minute premium
        occ_f    = 1.10 if recent_occ > 0.85 else (0.92 if recent_occ < 0.60 else 1.0)

        for rtype, base in BASE_PRICES.items():
            price = round(float(np.clip(
                base * seas * dow * event * lead_f * occ_f, base * 0.7, base * 2.2
            )), 2)
            exp_occ = float(np.clip(0.68 * seas * dow * occ_f, 0.20, 0.97))
            rows.append({
                'date':              dt.strftime('%Y-%m-%d'),
                'day_of_week':       dt.strftime('%A'),
                'lead_days':         lead,
                'room_type':         rtype,
                'base_price':        base,
                'suggested_adr':     price,
                'expected_occupancy': round(exp_occ, 4),
                'expected_revpar':   round(price * exp_occ, 2),
                'season_factor':     round(seas, 3),
                'dow_factor':        round(dow, 3),
                'event_factor':      round(event, 3),
                'lead_factor':       round(lead_f, 3),
                'occupancy_factor':  round(occ_f, 3),
                'has_event':         event > 1.0,
            })
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    print('Building historical dataset...')
    hist = build_historical()
    hist.to_csv('data/historical_hotel_data.csv', index=False)

    print('Running pricing forecast...')
    forecast = build_forecast(hist)
    forecast.to_csv('data/pricing_forecast.csv', index=False)

    # ── JSON exports for web ──────────────────────────────────────────────────

    std = hist[hist['room_type'] == 'Standard']

    # KPI summary (latest 30 days)
    last30 = std.tail(30)
    kpis = {
        'avg_adr':       round(last30['adr'].mean(), 2),
        'avg_revpar':    round(last30['revpar'].mean(), 2),
        'avg_occupancy': round(last30['occupancy'].mean(), 4),
        'total_revenue': round(hist.tail(30 * 3)['revenue'].sum(), 2),
        'total_rooms':   TOTAL_ROOMS,
        'forecast_days': DAYS_FORECAST,
    }
    with open('data/kpis.json', 'w') as f: json.dump(kpis, f, indent=2)

    # Monthly trend (last 24 months, all room types aggregated)
    monthly = (
        hist.groupby('month')
        .agg(avg_adr=('adr','mean'), avg_revpar=('revpar','mean'),
             avg_occupancy=('occupancy','mean'), total_revenue=('revenue','sum'))
        .reset_index().tail(24)
        .round(2)
    )
    with open('data/monthly_trend.json', 'w') as f:
        json.dump(monthly.to_dict('records'), f, indent=2)

    # Revenue by room type (last 12 months)
    by_room = (
        hist[hist['date'] >= (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')]
        .groupby('room_type')
        .agg(total_revenue=('revenue','sum'), avg_adr=('adr','mean'),
             avg_occupancy=('occupancy','mean'))
        .reset_index().round(2)
    )
    with open('data/revenue_by_room.json', 'w') as f:
        json.dump(by_room.to_dict('records'), f, indent=2)

    # Occupancy by DOW
    dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    by_dow = (
        std.groupby('day_of_week')
        .agg(avg_occupancy=('occupancy','mean'), avg_adr=('adr','mean'))
        .reset_index().round(4)
    )
    by_dow['order'] = by_dow['day_of_week'].map({d:i for i,d in enumerate(dow_order)})
    by_dow = by_dow.sort_values('order').drop('order',axis=1)
    with open('data/occupancy_by_dow.json', 'w') as f:
        json.dump(by_dow.to_dict('records'), f, indent=2)

    # 60-day forecast (Standard room only for clarity)
    fc_std = forecast[forecast['room_type'] == 'Standard'][[
        'date','day_of_week','lead_days','suggested_adr','expected_occupancy',
        'expected_revpar','season_factor','dow_factor','event_factor','has_event'
    ]]
    with open('data/forecast.json', 'w') as f:
        json.dump(fc_std.to_dict('records'), f, indent=2)

    # Pricing factors (avg contribution of each factor)
    factors = [
        {'factor': 'Base Price',        'avg_value': BASE_PRICES['Standard'], 'description': 'Starting point'},
        {'factor': 'Seasonality',       'avg_value': round(std['season_index'].mean(), 3), 'description': 'Monthly demand index'},
        {'factor': 'Day of Week',       'avg_value': round(std['day_of_week'].map({d: DOW_FACTOR[i] for i,d in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])}).mean(), 3), 'description': 'Weekend premium'},
        {'factor': 'Local Events',      'avg_value': round(std['event_factor'].mean(), 3), 'description': 'Conferences & holidays'},
        {'factor': 'Occupancy Pressure','avg_value': 1.05, 'description': 'Supply/demand balance'},
        {'factor': 'Lead Time',         'avg_value': 1.08, 'description': 'Last-minute premium'},
    ]
    with open('data/pricing_factors.json', 'w') as f:
        json.dump(factors, f, indent=2)

    print(f'Historical: {len(hist):,} rows | Forecast: {len(forecast)} rows')
    print('JSON exports saved to data/')
