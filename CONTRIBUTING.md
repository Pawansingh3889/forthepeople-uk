# Contributing to ForThePeople UK

A public-data civic dashboard. Contributions are welcome; the rules
below keep the project accurate, attribution-preserving, and
politically neutral.

Before you start, skim:

- [**`GOVERNANCE.md`**](GOVERNANCE.md) — roles, first-PR-wins, the
  four hard scope lines.
- [**`CODE_OF_CONDUCT.md`**](CODE_OF_CONDUCT.md) — behavioural bar,
  including the political-neutrality clause.
- [**`SECURITY.md`**](SECURITY.md) — wrong numbers on public services
  go there, not in a public issue.

## The Prime Directive

**Accuracy and attribution, no exceptions.** Every metric on the
dashboard has a named upstream source, attributed in the UI and
listed in `NOTICE`. A PR that adds or changes a metric must also
update the attribution.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/forthepeople-uk.git
cd forthepeople-uk
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## How to Contribute

1. **Find or open an issue.** Watch labels `good first issue`,
   `help wanted`, `data-quality`, `new-council`.
2. **Claim it** by commenting — 7-day soft claim per `GOVERNANCE.md`.
3. **Branch.** `feature/<short-name>` or `bugfix/<short-name>`.
4. **Code + test.**
5. **Before pushing:** `ruff check .`, `pytest -q`.
6. **Open the PR.** Conventional commit style, one logical change per
   commit. Reference the issue number.

## Adding a new council or region

The most common contribution path. Walkthrough:

1. Check the data source. If the metric isn't published at the
   required granularity by the existing sources (ONS / gov.uk / NHS
   Digital / DfE / Police.UK / Met Office / Open-Meteo), open an
   issue before coding.
2. Add the council to `data.py` following the existing pattern.
3. Add a test in `tests/` that asserts the metric fetches and
   validates for the new council.
4. Update `NOTICE` if a new upstream source is introduced.

## Adding a new data source

Bigger change — start as an issue. Required elements:

- Source URL and publisher
- Licence (must be OGL v3.0, CC BY 4.0, or equivalent open licence)
- Attribution wording to appear on the dashboard and in `NOTICE`
- Freshness expectations (how often the source updates, how stale a
  cached value can get before the dashboard should warn)

## Code Standards

- Python 3.11+.
- Type hints on public functions.
- Docstrings for every module.
- New code goes under `tests/` in a matching file.
- Caching lives in `cache.py`; validation in `validators.py`. Do not
  scatter fetches across `app.py`.

## Political neutrality

The dashboard reports facts. Don't editorialise. Acceptable:

- "MP X voted in favour of Bill Y on date Z." (cited to parliament.uk)
- "Council waiting list has 3,500 households." (cited to ONS)

Not acceptable:

- "MP X has a poor voting record."
- "Council Y has failed its residents."

Framing wording that interprets, blames, or praises gets pushed back
in review.

## Reporting bugs

Open an issue with:

- Council / region / metric affected
- Observed value vs authoritative upstream value
- Screenshot or URL
- Python version, OS

## Feature requests

Open an issue describing:

- The civic question the feature answers
- Which data source it needs
- Whether the metric is comparable across councils

## Recognition

Merged PRs land in the commit history permanently. The README credits
substantial contributors when appropriate.
