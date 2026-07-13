# ForThePeople UK

UK citizen transparency platform. Free council-level dashboards built on open data.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](LICENSE)

**Independence:** ForThePeople UK is not affiliated with any government
body, political party, or campaign. Everything shown is either fetched from
a public open-data API or clearly marked as indicative sample data.

### New in this release

- **Live MPs** — current members, parties and majorities for the
  constituencies matching your council, straight from the UK Parliament
  Members API (Open Parliament Licence v3.0). Static fallback when no
  constituency shares the council's name.
- **Council registry with ONS GSS codes** — every selectable place now
  carries the GSS code of its governing authority (`registry.py`),
  cross-checked against postcodes.io in CI. GSS codes are the join key
  for ONS, Land Registry and most other official datasets, so future
  live integrations start from here. The registry also records who
  actually governs each town — Huddersfield maps to Kirklees, Harrogate
  to North Yorkshire.
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
| MPs | [UK Parliament](https://members.parliament.uk) Members API | Yes, current members; static fallback |
| News | gov.uk + BBC News feeds | Yes, cached 24h |
| Postcode lookup | [postcodes.io](https://postcodes.io) API | Yes |
| Everything else | Held in `data.py` | Indicative sample data for demonstration |

The sample tabs (population, finance, housing, education, health, transport,
environment) carry realistic figures for a handful of Yorkshire councils,
national rollup numbers for the whole-UK view, and sensible defaults elsewhere.
They show the shape of the product; every tab links to the official source
(ONS, gov.uk, NHS, DfE) so any figure can be checked. Wiring those tabs to
their own live APIs is the roadmap — the five live sources above show the
pattern, none of them needs an API key, and the GSS codes in `registry.py`
are the join key the remaining integrations (ONS population, Land Registry
house prices) will use.

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
ruff check .
```

## 14 Dashboards

Overview | Weather | Population | Finance | Housing | Education | Health | Crime | Transport | Environment | Schemes | Elections | Jobs | News

## 50+ Government Schemes

Income Support | Disability | Housing | Family | Pension | Energy | Tax | Transport | Education | Immigration | Business | Legal

## Essential Services

Emergency (999, 101, 111) | HMRC | DVLA | Passport | NHS | Voter Registration | Companies House

No login. No tracking. No paywall. All public data.
