# ForThePeople UK

UK citizen transparency platform. Free council-level dashboards built on open data.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](LICENSE)

**Independence:** ForThePeople UK is not affiliated with any government
body, political party, or campaign. Everything shown is either fetched from
a public open-data API or clearly marked as indicative sample data.

### New in this release

- **Live population and house prices** — the totals on Overview, Population
  and Housing now come from the ONS mid-year estimates (via the Nomis API)
  and the HM Land Registry UK House Price Index, joined on the registry's
  GSS codes. The vs-UK price comparison is computed from the same month's
  UK-wide figure. Median age, waiting lists and rents remain labelled
  samples for now.
- **Ask in plain English** — type a question, get an answer from Claude
  grounded in this dashboard's own data, with every figure labelled live
  or indicative. Works three ways: an operator API key (rate-limited),
  a visitor's own key (session-only), or no key at all, where it falls
  back to a keyword search of the schemes tables. It gives general
  information and signposting only, never personal eligibility,
  immigration or legal advice.
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
| Population | ONS mid-year estimates via [Nomis](https://www.nomisweb.co.uk) | Yes, latest estimate; static fallback |
| House prices | [HM Land Registry UKHPI](https://landregistry.data.gov.uk/app/ukhpi) | Yes, latest published month; static fallback |
| News | gov.uk + BBC News feeds | Yes, cached 24h |
| Postcode lookup | [postcodes.io](https://postcodes.io) API | Yes |
| Ask | Anthropic Claude API (optional) | Only when a key is set; grounded in the dashboard's own data |
| Everything else | Held in `data.py` | Indicative sample data for demonstration |

The sample tabs (finance, education, health, transport, environment, plus
the population and housing details the live sources don't cover) carry
realistic figures for a handful of Yorkshire councils,
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

## 15 Dashboards

Overview | Weather | Population | Finance | Housing | Education | Health | Crime | Transport | Environment | Schemes | Elections | Jobs | News | Ask

## The Ask tab

Plain-English questions answered by Claude, grounded in the dashboard's data
for the selected council. The model is told which figures are live and which
are indicative samples, and it labels its answers the same way. It will not
assess anyone's benefit eligibility, immigration status or legal position;
it points to the gov.uk checkers, Citizens Advice or a regulated adviser
instead.

The app never needs a key to run. The Ask tab picks its mode automatically:

1. **Operator key** - set `ANTHROPIC_API_KEY` in the environment (on a
   Hugging Face Space: Settings, then Variables and secrets; on Render: an
   environment variable). Built-in limits apply because the operator pays
   per question: 10 per visitor session, 60 per hour in total, short
   answers, and a low-cost model by default (`claude-haiku-4-5`, override
   with `ANTHROPIC_MODEL`). Set a monthly spend limit in the Anthropic
   console as the hard backstop.
2. **Visitor key** - pasted into the tab, held in that browser session
   only, never stored.
3. **No key** - the tab answers with a keyword search over the schemes and
   services tables instead of AI.

Questions and the selected council's dashboard data are sent to Anthropic's
API only in modes 1 and 2. Nothing is logged by the app.

## 50+ Government Schemes

Income Support | Disability | Housing | Family | Pension | Energy | Tax | Transport | Education | Immigration | Business | Legal

## Essential Services

Emergency (999, 101, 111) | HMRC | DVLA | Passport | NHS | Voter Registration | Companies House

No login. No tracking. No paywall. All public data.
