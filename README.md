# Hotel Dynamic Pricing Engine — Revenue Management

> **Revenue Management Portfolio Project** · Python · 6-factor pricing algorithm · 60-day forecast
> **Status:** Finished · Deployed to production (2026-04)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-%E2%86%92%20Open%20Dashboard-60a5fa?style=for-the-badge&logo=firebase&logoColor=white)](https://proyectos-personales.web.app/hotel)
[![Portfolio](https://img.shields.io/badge/Portfolio-proyectos--personales.web.app-8b5cf6?style=for-the-badge&logo=firebase&logoColor=white)](https://proyectos-personales.web.app)

---

## Project Status

| Phase | Status |
|---|---|
| Pricing algorithm design (6 factors) | Done |
| Synthetic historical data (2 years × 3 room types) | Done |
| 60-day forward forecast | Done |
| React dashboard deployment | Done |

**Current phase:** maintenance — engine live on portfolio.

---

## Project Overview

An algorithmic **Revenue Management engine** built in Python that simulates dynamic hotel pricing decisions. Models ADR, RevPAR and occupancy optimization using six real-world pricing factors across 3 room types and generates a 60-day forward price forecast.

**Live dashboard → [proyectos-personales.web.app/hotel](https://proyectos-personales.web.app/hotel)**

---

## Skills Demonstrated

- **Revenue Management:** ADR, RevPAR, occupancy pressure, lead-time pricing
- **Business Modelling:** Rule-based algorithm combining 6 independent pricing factors
- **Data Analysis:** Python (Pandas, NumPy) for synthetic historical data and projections
- **Data Visualisation:** React + Recharts interactive dashboard (deployed on Firebase)

---

## Repository Structure

```
project-hotel-pricing-engine/
├── dynamic_pricing_engine.py   # Main engine: historical data + forecast + JSON export
├── data/
│   ├── historical_hotel_data.csv   # 2 years × 3 room types (2,190 rows)
│   ├── pricing_forecast.csv        # 60-day forecast × 3 room types (180 rows)
│   ├── kpis.json
│   ├── monthly_trend.json
│   ├── revenue_by_room.json
│   ├── occupancy_by_dow.json
│   ├── forecast.json
│   └── pricing_factors.json
└── README.md
```

---

## Pricing Engine Logic

The engine adjusts the room base price by multiplying six independent factors:

| Factor | Description |
|--------|-------------|
| **Base Price** | Starting price per room type (Standard $120, Deluxe $185, Suite $320) |
| **Seasonality** | Monthly demand index (Jan 0.72 → Jul 1.35) |
| **Day of Week** | Weekend premium (Sat ×1.25, Mon ×0.90) |
| **Local Events** | Holidays & conferences (Jul 4th ×1.45, Dec 31st ×1.55) |
| **Occupancy Pressure** | ×1.10 if recent occ > 85%; ×0.92 if < 60% |
| **Lead Time** | Last-minute premium for bookings within 30 days |

Final price is clipped between 70% and 220% of the base price.

---

## Hotel Configuration

- **120 rooms** across 3 types: Standard (55%), Deluxe (32%), Suite (13%)
- **2 years** of synthetic historical data (daily, all room types)
- **60-day** pricing forecast with expected occupancy and RevPAR

---

## How to Run

```bash
pip install pandas numpy
python dynamic_pricing_engine.py
```

Outputs CSVs and 6 JSON files to `data/`.

---

## Dashboard

The JSON outputs power an interactive React dashboard:

**[proyectos-personales.web.app/hotel](https://proyectos-personales.web.app/hotel)**

Charts included:
- 24-month ADR & RevPAR trend
- 60-day price forecast with event markers
- Occupancy by day of week
- Revenue breakdown by room type
- Pricing factor contribution chart

---

## Links

- **Portfolio:** [proyectos-personales.web.app](https://proyectos-personales.web.app)
- **LinkedIn:** [Mindset & Code](https://www.linkedin.com/company/mindset-code)
- **Email:** contacto@mindset-code.com

---

*Built by [Mindset & Code](https://github.com/mindset-code) · Data & BI Analyst · MBA · ISC2 CC*
