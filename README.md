# ForThePeople UK

Citizen transparency platform for the UK. Free, real-time council-level government data dashboards.

Inspired by [forthepeople.in](https://forthepeople.in/en) — bringing the same transparency to UK councils.

## Features

13 dashboards covering every council in England:

| Dashboard | Data Source |
|---|---|
| Overview | Population, house prices, employment, salary, council tax |
| Weather | Live weather + 7-day forecast (Open-Meteo) |
| Population | Demographics, median age, life expectancy |
| Finance | Council budget, spending breakdown, council tax |
| Housing | Average prices, vs UK average, waiting lists, schemes |
| Education | Schools count, Ofsted ratings, university links |
| Health | GP surgeries, hospitals, A&E wait times |
| Crime | Total crimes, anti-social, violent, burglary (Police UK) |
| Transport | Train stations, bus providers, commute times |
| Environment | Recycling rates, air quality, green spaces |
| Schemes | 10 government benefits with eligibility and amounts |
| Elections | MP names, parties, constituencies, majorities |
| Jobs | Job sites, apprenticeships, certifications |

## Regions Covered

Yorkshire, North East, North West, East Midlands, West Midlands, East of England, London, South East, South West — 60+ councils.

## Setup

```bash
pip install streamlit requests
streamlit run app.py
```

## Data Sources

All free, no API keys needed:

| Source | What |
|---|---|
| Open-Meteo | Live weather and forecasts |
| ONS | Population, demographics, house prices |
| gov.uk | Council budgets, schemes, benefits, elections |
| NHS Digital | GP surgeries, hospitals, wait times |
| DfE | Schools, Ofsted ratings |
| Police UK | Crime statistics |
| DEFRA | Air quality, environment |

## Privacy

No login. No tracking. No cookies. No paywall. All data from public open sources.

## Stack

Python, Streamlit, Open-Meteo API, Reddit JSON, ESPN API
