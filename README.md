# ForThePeople UK

UK citizen transparency platform. Free council-level dashboards built on open data.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](LICENSE)

**Independence:** ForThePeople UK is not affiliated with any government
body, political party, or campaign. Everything shown is either fetched from
a public open-data API or clearly marked as indicative sample data.

### New in this release

- **Live crime statistics** — the Crime tab now pulls street-level data
  from the Police UK open API for the latest published month, counted
  within about a mile of the council centre. No API key needed.
- **Postcode slicer** — type any UK postcode into the sidebar; the
  dashboard auto-selects the matching region and council via
  postcodes.io. Falls back to the existing dropdowns.
- **"View whole UK" button** — one-click national rollup when you
  want country-wide stats instead of drilling down to a single
  council.
- **News tab** — side-by-side feed of gov.uk announcements (OGL
  v3.0) and BBC News UK headlines with direct links to the source.
  Cached for 24 hours; degrades gracefully when a feed is down.

## What's live and what isn't

Being straight about the data matters more on a transparency tool than
anywhere else, so here is exactly where each tab gets its numbers:

| Tab | Source | Live? |
|-----|--------|-------|
| Weather | [Open-Meteo](https://open-meteo.com) API | Yes, fetched at runtime |
| Crime | [Police UK](https://data.police.uk) API | Yes, latest published month |
| News | gov.uk + BBC News feeds | Yes, cached 24h |
| Postcode lookup | [postcodes.io](https://postcodes.io) API | Yes |
| Everything else | Held in `data.py` | Indicative sample data for demonstration |

The sample tabs (population, finance, housing, education, health, transport,
environment, MPs) carry realistic figures for a handful of Yorkshire councils,
national rollup numbers for the whole-UK view, and sensible defaults elsewhere.
They show the shape of the product; every tab links to the official source
(ONS, gov.uk, NHS, DfE) so any figure can be checked. Wiring those tabs to
their own live APIs is the roadmap — the four live sources above show the
pattern, and none of them needs an API key.

## Links

- [GitHub](https://github.com/Pawansingh3889/forthepeople-uk)
- [Hugging Face Space](https://huggingface.co/spaces/pawankapkoti/forthepeople-uk)
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`GOVERNANCE.md`](GOVERNANCE.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md) · [`NOTICE`](NOTICE)

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

No API keys needed. Tests and lint run the same way CI does:

```bash
python -m pytest tests/ -v --timeout=30
ruff check app.py data.py cache.py validators.py postcode.py news.py
```

## 14 Dashboards

Overview | Weather | Population | Finance | Housing | Education | Health | Crime | Transport | Environment | Schemes | Elections | Jobs | News

## 50+ Government Schemes

Income Support | Disability | Housing | Family | Pension | Energy | Tax | Transport | Education | Immigration | Business | Legal

## Essential Services

Emergency (999, 101, 111) | HMRC | DVLA | Passport | NHS | Voter Registration | Companies House

No login. No tracking. No paywall. All public data.
