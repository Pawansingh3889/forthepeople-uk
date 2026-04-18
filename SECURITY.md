# Security policy

ForThePeople UK is a read-only, citizen-facing dashboard. It does not
handle user accounts or personal data, which narrows the threat
surface considerably — but a dashboard that quietly returns wrong
numbers about public services is itself a civic-harm issue, and this
document treats that seriously.

## Supported versions

Continuous deployment from `main`. The supported version is the
latest commit on `main`.

## Threat model

| Surface | Protection | Where |
| --- | --- | --- |
| Upstream data sources | Each fetch is cached with a bounded TTL; a failing source falls back to the last known-good value rather than silently returning zero | `cache.py`, `data.py` |
| Data validation | Every fetched dataset passes through a validation layer before rendering | `validators.py`, `tests/` |
| Streamlit UI | No user-generated input reaches code paths other than the council / region selectors, which are enumerated values | `app.py` |
| CI / deploy | GitHub Actions with no long-lived secrets for public-data sources; Hugging Face / Render deploy pulls from `main` | `.github/workflows/` |

Civic-harm threats specifically worth reporting:

- **Wrong numbers on a public service** (population off by 10x, wrong MP for a constituency, wrong council tax band, expired dataset presented as current).
- **Misleading attribution** (a dashboard cell showing a metric whose source isn't linked or is linked to the wrong provider).
- **Stale cache hiding an outage** (a dead upstream shown as current data because the cache TTL is too generous).

## Reporting a vulnerability

**Do not open a public GitHub issue for a data-integrity or security
problem.**

Report privately via the GitHub security advisory form:

<https://github.com/Pawansingh3889/forthepeople-uk/security/advisories/new>

Include:

1. **What you found** — one-sentence description.
2. **Reproduction** — which council / region / metric, the observed
   value, and the authoritative upstream value.
3. **Impact** — what a reader relying on this would misunderstand.
4. **Suggested fix** — optional.

## What to expect

| Severity | Initial response | Fix target |
| --- | --- | --- |
| Critical (wrong MP, wrong council tax, service-availability misrepresentation) | within 48 hours | within 7 days |
| High (metric silently stale, attribution broken) | within 5 days | within 14 days |
| Medium | within 7 days | next cycle |
| Low / info | within 14 days | when scoped |

## Coordinated disclosure

90 days by default; sooner if the fix has shipped and you agree.

## Scope

**In scope:**

- `app.py`, `data.py`, `cache.py`, `validators.py`
- `tests/`
- `.github/workflows/`
- Configuration files

**Out of scope:**

- Issues in upstream data (report to the data owner — ONS, gov.uk,
  NHS Digital, etc. — and link the advisory here so we can add a
  freshness warning if useful)
- Streamlit / Render / Hugging Face platform issues
- Feature requests (open a feature issue instead)

## Previous advisories

None.
