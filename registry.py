"""Canonical council registry for ForThePeople UK.

One record per selectable place: display name, region grouping, centre
coordinates, and — the part every official API cares about — the ONS GSS code
of the governing local authority. GSS codes are the join key for ONS
population estimates, Land Registry house prices, IMD deprivation ranks and
most other official datasets, so live-source integrations start here instead
of re-solving "which council is this string?" each time.

Some entries are towns rather than authorities in their own right
(Huddersfield is governed by Kirklees, Halifax by Calderdale; Harrogate and
Scarborough have been part of the North Yorkshire unitary since April 2023).
The ``authority`` field records who actually governs, and ``gss`` always
belongs to that authority. ``mp_search`` overrides the term used to find the
place's constituencies in the UK Parliament Members API where the display
name would mismatch (for example Newcastle, which would otherwise also match
Newcastle-under-Lyme).

Codes are cross-checked against postcodes.io reverse geocoding in
``tests/test_registry.py``.
"""
from __future__ import annotations

from dataclasses import dataclass

# Reserved value meaning "show national / UK-wide data" instead of drilling
# down to a single council. K02000001 is the ONS code for the United Kingdom.
UK_ALL = "United Kingdom"


@dataclass(frozen=True)
class Council:
    name: str            # display name used across the app
    region: str          # sidebar grouping (ONS English region)
    lat: float
    lon: float
    gss: str             # ONS GSS code of the governing local authority
    authority: str       # official name of that authority
    mp_search: str | None = None  # constituency search override; None = use name


_ENTRIES = [
    # Yorkshire and the Humber
    Council("York", "Yorkshire and the Humber", 53.96, -1.08, "E06000014", "City of York"),
    Council("Leeds", "Yorkshire and the Humber", 53.80, -1.55, "E08000035", "Leeds"),
    # Sheffield and Barnsley were re-coded by ONS after boundary changes
    # (formerly E08000019 / E08000016). Older datasets may still use the
    # previous codes; postcodes.io serves the current ones below.
    Council("Sheffield", "Yorkshire and the Humber", 53.38, -1.47, "E08000039", "Sheffield"),
    Council("Bradford", "Yorkshire and the Humber", 53.79, -1.75, "E08000032", "Bradford"),
    Council("Hull", "Yorkshire and the Humber", 53.74, -0.34, "E06000010", "Kingston upon Hull, City of"),
    Council("Wakefield", "Yorkshire and the Humber", 53.68, -1.50, "E08000036", "Wakefield"),
    Council("Doncaster", "Yorkshire and the Humber", 53.52, -1.13, "E08000017", "Doncaster"),
    Council("Barnsley", "Yorkshire and the Humber", 53.55, -1.48, "E08000038", "Barnsley"),
    Council("Rotherham", "Yorkshire and the Humber", 53.43, -1.36, "E08000018", "Rotherham"),
    Council("Harrogate", "Yorkshire and the Humber", 53.99, -1.54, "E06000065", "North Yorkshire"),
    Council("Scarborough", "Yorkshire and the Humber", 54.28, -0.40, "E06000065", "North Yorkshire"),
    Council("Huddersfield", "Yorkshire and the Humber", 53.65, -1.78, "E08000034", "Kirklees"),
    Council("Halifax", "Yorkshire and the Humber", 53.72, -1.86, "E08000033", "Calderdale"),
    Council("Grimsby", "Yorkshire and the Humber", 53.57, -0.08, "E06000012", "North East Lincolnshire"),

    # North East (Middlesbrough moved here from Yorkshire — Tees Valley is
    # part of the North East region in the ONS split)
    Council("Newcastle", "North East", 54.97, -1.61, "E08000021", "Newcastle upon Tyne", mp_search="Newcastle upon Tyne"),
    Council("Sunderland", "North East", 54.91, -1.38, "E08000024", "Sunderland"),
    Council("Durham", "North East", 54.78, -1.58, "E06000047", "County Durham"),
    Council("Darlington", "North East", 54.52, -1.55, "E06000005", "Darlington"),
    Council("Hartlepool", "North East", 54.69, -1.21, "E06000001", "Hartlepool"),
    Council("Middlesbrough", "North East", 54.57, -1.23, "E06000002", "Middlesbrough"),

    # North West
    Council("Manchester", "North West", 53.48, -2.24, "E08000003", "Manchester"),
    Council("Liverpool", "North West", 53.41, -2.99, "E08000012", "Liverpool"),
    Council("Lancaster", "North West", 54.05, -2.80, "E07000121", "Lancaster"),
    Council("Blackpool", "North West", 53.81, -3.05, "E06000009", "Blackpool"),
    Council("Preston", "North West", 53.76, -2.70, "E07000123", "Preston"),
    Council("Chester", "North West", 53.19, -2.89, "E06000050", "Cheshire West and Chester"),

    # East Midlands
    Council("Nottingham", "East Midlands", 52.95, -1.15, "E06000018", "Nottingham"),
    Council("Leicester", "East Midlands", 52.63, -1.13, "E06000016", "Leicester"),
    Council("Derby", "East Midlands", 52.92, -1.47, "E06000015", "Derby"),
    Council("Lincoln", "East Midlands", 53.23, -0.54, "E07000138", "City of Lincoln"),
    Council("Northampton", "East Midlands", 52.24, -0.90, "E06000062", "West Northamptonshire"),

    # West Midlands
    Council("Birmingham", "West Midlands", 52.49, -1.90, "E08000025", "Birmingham"),
    Council("Coventry", "West Midlands", 52.41, -1.51, "E08000026", "Coventry"),
    Council("Wolverhampton", "West Midlands", 52.59, -2.13, "E08000031", "Wolverhampton"),
    Council("Stoke-on-Trent", "West Midlands", 53.00, -2.18, "E06000021", "Stoke-on-Trent"),

    # East of England
    Council("Norwich", "East of England", 52.63, 1.30, "E07000148", "Norwich"),
    Council("Cambridge", "East of England", 52.21, 0.12, "E07000008", "Cambridge"),
    Council("Ipswich", "East of England", 52.06, 1.15, "E07000202", "Ipswich"),
    Council("Peterborough", "East of England", 52.57, -0.24, "E06000031", "Peterborough"),
    Council("Colchester", "East of England", 51.89, 0.90, "E07000071", "Colchester"),

    # London
    Council("Westminster", "London", 51.50, -0.14, "E09000033", "Westminster"),
    Council("Camden", "London", 51.54, -0.14, "E09000007", "Camden"),
    Council("Greenwich", "London", 51.48, 0.01, "E09000011", "Greenwich"),
    Council("Hackney", "London", 51.54, -0.06, "E09000012", "Hackney"),
    Council("Tower Hamlets", "London", 51.52, -0.03, "E09000030", "Tower Hamlets"),
    Council("Croydon", "London", 51.38, -0.10, "E09000008", "Croydon"),

    # South East
    Council("Brighton", "South East", 50.82, -0.14, "E06000043", "Brighton and Hove"),
    Council("Oxford", "South East", 51.75, -1.25, "E07000178", "Oxford"),
    Council("Reading", "South East", 51.45, -0.97, "E06000038", "Reading"),
    Council("Southampton", "South East", 50.90, -1.40, "E06000045", "Southampton"),
    Council("Canterbury", "South East", 51.28, 1.08, "E07000106", "Canterbury"),

    # South West
    Council("Bristol", "South West", 51.45, -2.59, "E06000023", "Bristol, City of"),
    Council("Bath", "South West", 51.38, -2.36, "E06000022", "Bath and North East Somerset"),
    Council("Exeter", "South West", 50.72, -3.53, "E07000041", "Exeter"),
    Council("Plymouth", "South West", 50.37, -4.14, "E06000026", "Plymouth"),
    Council("Bournemouth", "South West", 50.72, -1.88, "E06000058", "Bournemouth, Christchurch and Poole"),

    # Whole-UK pseudo-region last, so a real council (with the most live
    # data) is the landing view; the sidebar button still jumps here.
    Council(UK_ALL, "United Kingdom (national)", 54.0, -2.0, "K02000001", "United Kingdom"),
]

REGISTRY: dict[str, Council] = {c.name: c for c in _ENTRIES}

# Backward-compatible views used across the app.
councils: dict[str, list[str]] = {}
for _c in _ENTRIES:
    councils.setdefault(_c.region, []).append(_c.name)

COORDS: dict[str, tuple[float, float]] = {c.name: (c.lat, c.lon) for c in _ENTRIES}
