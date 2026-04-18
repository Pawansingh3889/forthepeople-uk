# ForThePeople UK

UK citizen transparency platform. Free council-level government data dashboards.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](LICENSE)

**Independence:** ForThePeople UK is not affiliated with any government
body, political party, or campaign. Data is from public open-data sources
(ONS, gov.uk, NHS Digital, DfE, Police.UK, Met Office, Open-Meteo,
postcodes.io, BBC News).

### New in this release

- **Postcode slicer** — type any UK postcode into the sidebar; the
  dashboard auto-selects the matching region and council via
  postcodes.io. Falls back to the existing dropdowns.
- **"View whole UK" button** — one-click national rollup when you
  want country-wide stats instead of drilling down to a single
  council. Uses ONS headline numbers (population, house prices,
  life expectancy, employment rate).
- **News tab** — side-by-side feed of gov.uk announcements (OGL
  v3.0) and BBC News UK headlines with direct links to the source.
  Cached for 24 hours; degrades gracefully when a feed is down.

## Links

- [GitHub](https://github.com/Pawansingh3889/forthepeople-uk)
- [Run Locally](#setup)
- [Hugging Face Space](https://huggingface.co/spaces/pawankapkoti/forthepeople-uk)
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`GOVERNANCE.md`](GOVERNANCE.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md) · [`NOTICE`](NOTICE)

## Setup

```bash
pip install streamlit requests
streamlit run app.py
```

## 14 Dashboards

Overview | Weather | Population | Finance | Housing | Education | Health | Crime | Transport | Environment | Schemes | Elections | Jobs | News

## 50+ Government Schemes

Income Support | Disability | Housing | Family | Pension | Energy | Tax | Transport | Education | Immigration | Business | Legal

## Essential Services

Emergency (999, 101, 111) | HMRC | DVLA | Passport | NHS | Voter Registration | Companies House

## Data Sources

ONS | gov.uk | NHS Digital | DfE | Police UK | Open-Meteo | DEFRA

No login. No tracking. No paywall. All public data.
