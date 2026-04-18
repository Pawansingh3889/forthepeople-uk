# ForThePeople UK governance

A citizen-facing dashboard over public UK government data. Governance
matches that scope — short, explicit about independence, hard lines on
attribution and political neutrality.

## Roles

### Maintainer

Currently: **[@Pawansingh3889](https://github.com/Pawansingh3889)**.

Final decision on:

- merges to `main`
- new council / region additions
- data-source additions (every new source is a new licence chain)
- changes to the independence and attribution wording in the UI
- this governance document

Commits to:

- replying to issues and PRs within **7 calendar days**
- merging green, in-scope PRs within **14 calendar days** of the last
  review comment being addressed

### Triage collaborator

Granted to contributors with three merged, in-scope PRs. Can label,
assign, and close duplicate / off-topic issues. Cannot merge or
change repository settings.

### Contributor

Anyone who files an issue or opens a PR.

## Decisions

Small changes (docs, bug fixes, UI polish, new council data for an
already-supported region) — one maintainer approval on the PR.

Larger changes — new regions, new data sources, new metrics — start
as an **issue with a proposal**:

1. what question it helps a citizen answer
2. where the data comes from (URL + licence)
3. how attribution is preserved on the dashboard
4. whether the metric is comparable across councils (apples-to-apples
   is the bar — bespoke per-council definitions dilute the platform)

## Issue assignment (first-PR-wins)

1. Comment "I'd like to work on this" — 7-day soft claim.
2. Expire silently after 7 days; anyone may pick up.
3. If two PRs land, the first to pass CI and request review wins.

## Scope discipline

Hard lines that will not move:

- **Politically neutral.** No endorsements, no editorialising on
  MP voting records or council decisions. The dashboard reports,
  it does not campaign. PRs that tilt the presentation toward a
  party, candidate, or policy position will be closed.
- **Attribution preserved.** Every metric shows its upstream data
  source in the UI and is listed in `NOTICE`. Removing or obscuring
  an attribution is never a merge-able change.
- **Public-data-only.** Every source must be publicly accessible
  under a known open licence (OGL v3.0, CC BY 4.0, or equivalent).
  New sources require a corresponding entry in `NOTICE` before the
  PR lands.
- **No personal data about named individuals beyond elected
  representatives in their public role.** MPs, councillors, and
  mayors are fair game for the information already published on
  gov.uk or parliament.uk. Constituents are not.

## Release cadence

Continuous deployment from `main` to Render / Hugging Face Spaces.
No tagged releases today.

## Security

See `SECURITY.md`. Security issues route via private advisory.

## Changes to this document

Via PR from the maintainer. Community input welcome in issues.
