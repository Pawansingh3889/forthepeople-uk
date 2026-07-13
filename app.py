"""ForThePeople UK — Citizen Transparency Platform

Free UK council dashboards. Weather, crime, news and postcode lookup are live
open-data sources (Open-Meteo, Police UK, gov.uk/BBC feeds, postcodes.io);
other figures are indicative sample data for demonstration.
Independent. No login. No paywall.

Usage:
    streamlit run app.py
"""
import os

import streamlit as st

import ask
import foi
from data import (UK_ALL, councils, get_weather, get_council_data, get_mp_data, get_population,
                   get_petitions,
                   get_schemes, get_housing, get_schools, get_crime_stats, get_health_data,
                   get_transport, get_environment, get_essential_services, get_jobs_data,
                   get_air_quality, get_floods)
from news import get_combined as get_news
from postcode import find_council, lookup_postcode
from registry import REGISTRY

st.set_page_config(
    page_title="ForThePeople UK",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ──
st.markdown("""
<style>
    .stApp { background-color: #0a0f1a; }
    .main-header { text-align: center; padding: 20px 0; }
    .main-header h1 { color: #ffffff; font-size: 2.5rem; font-weight: 800; }
    .main-header p { color: #64748b; font-size: 1rem; }
    .stat-card { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #1e3a5f; border-radius: 16px; padding: 24px; text-align: center; }
    .stat-value { font-size: 2rem; font-weight: 800; color: #3b82f6; }
    .stat-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
    .data-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 12px; }
    .data-card h4 { color: #60a5fa; margin: 0 0 8px 0; }
    .data-card p { color: #cbd5e1; margin: 0; font-size: 0.9rem; }
    .scheme-card { background: #1e293b; border-left: 4px solid #22c55e; border-radius: 0 12px 12px 0; padding: 16px; margin-bottom: 10px; }
    .alert-card { background: #1e293b; border-left: 4px solid #ef4444; border-radius: 0 12px 12px 0; padding: 16px; margin-bottom: 10px; }
    .section-header { color: #f8fafc; font-size: 1.3rem; font-weight: 700; border-bottom: 2px solid #1e3a5f; padding-bottom: 8px; margin: 24px 0 16px 0; }
    a { color: #60a5fa !important; text-decoration: none !important; }
    a:hover { color: #93c5fd !important; }
    .footer { text-align: center; color: #475569; font-size: 0.75rem; padding: 40px 0 20px 0; border-top: 1px solid #1e293b; margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
st.sidebar.markdown("## ForThePeople UK")
st.sidebar.caption("Citizen Transparency Platform")

# Location slicer — three ways to choose. The postcode input takes
# precedence: if a valid postcode resolves to a council in our dataset,
# it updates the Region / Council selectboxes via session state.
# Falling back to the two dropdowns remains fully functional.

_region_options = list(councils.keys())


def _set_selection(region: str, council: str) -> None:
    """Sync the two selectbox widgets to a given (region, council) pair."""
    st.session_state["region_select"] = region
    st.session_state["council_select"] = council


postcode_input = st.sidebar.text_input(
    "Quick lookup — enter a UK postcode",
    key="postcode_input",
    placeholder="e.g. YO1 1AA",
    help="Auto-selects the region and council for that postcode. "
         "Falls back to the dropdowns below if the postcode is not in our dataset.",
).strip()

_last_resolved = st.session_state.get("_last_resolved_postcode")
if postcode_input and postcode_input.upper() != (_last_resolved or "").upper():
    result = lookup_postcode(postcode_input)
    if result is None:
        st.sidebar.error("Postcode not recognised. Try the dropdowns below.")
    else:
        match = find_council(result, councils)
        if match is None:
            admin = result.get("admin_district") or result.get("parliamentary_constituency") or "?"
            st.sidebar.warning(
                f"Valid postcode, but {admin} isn't in the dataset yet. "
                "Using your previous selection."
            )
        else:
            matched_region, matched_council = match
            _set_selection(matched_region, matched_council)
            st.session_state["_last_resolved_postcode"] = postcode_input
            st.sidebar.success(f"Matched: {matched_council} ({matched_region})")

# "All UK" shortcut button — one-click to the national rollup without
# searching in the dropdowns.
if st.sidebar.button("View whole UK", use_container_width=True):
    _set_selection("United Kingdom (national)", UK_ALL)

region = st.sidebar.selectbox(
    "Select Region",
    _region_options,
    key="region_select",
)

council_list = councils.get(region, ["Select a council"])
# Reset the council selection if it doesn't belong to the current region
# (e.g. the user changed region manually after a postcode lookup).
if st.session_state.get("council_select") not in council_list:
    st.session_state["council_select"] = council_list[0]

council = st.sidebar.selectbox(
    "Select Council",
    council_list,
    key="council_select",
)

st.sidebar.divider()
with st.sidebar.expander("Data provenance"):
    st.markdown(
        "**Live, fetched at runtime:**\n"
        "- Weather — [Open-Meteo](https://open-meteo.com)\n"
        "- Crime — [Police UK](https://data.police.uk)\n"
        "- MPs — [UK Parliament](https://members.parliament.uk) Members API\n"
        "- Population — ONS mid-year estimate via [Nomis](https://www.nomisweb.co.uk)\n"
        "- House prices — [HM Land Registry UKHPI](https://landregistry.data.gov.uk/app/ukhpi)\n"
        "- Air quality — [Open-Meteo](https://open-meteo.com) Air Quality API\n"
        "- Flood warnings — [Environment Agency](https://check-for-flooding.service.gov.uk)\n"
        "- Petitions — [UK Parliament petitions](https://petition.parliament.uk)\n"
        "- News — gov.uk + BBC feeds\n"
        "- Postcode lookup — [postcodes.io](https://postcodes.io)\n\n"
        "**Indicative sample data** (pending live integration): finance, "
        "education, health, transport, environment, plus the remaining "
        "population and housing details (median age, waiting lists, rents). "
        "Cross-check against the official source linked in each tab.\n\n"
        "The FOI tab is signposting, not data: it builds a Freedom of "
        "Information request route to the selected council via WhatDoTheyKnow.\n\n"
        "The Ask tab sends your question plus the selected council's dashboard "
        "data to Anthropic's Claude API, but only when an API key is configured; "
        "with no key it searches the schemes tables locally instead."
    )
st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.caption("Independent platform. Not affiliated with government.")

# ── Header ──
st.markdown(f"""
<div class="main-header">
    <h1>ForThePeople UK</h1>
    <p>Free, open UK council data for <strong>{council}</strong></p>
    <p style="font-size: 0.8rem; color: #475569;">Independent. No login. No paywall. Open data.</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Live data: Weather, Crime, MPs, Population, House prices, Air quality, Flood "
    "warnings, Petitions, News and postcode lookup. Remaining figures are indicative "
    "samples — see Data provenance in the sidebar and the source linked in each tab."
)

# ── Dashboard Tabs ──
# New tabs go on the end so indices of existing ones (Overview=0,
# Weather=1, ..., Jobs=12) stay stable; News=13, Ask=14, Petitions=15, FOI=16.
tabs = st.tabs([
    "Overview", "Weather", "Population", "Finance", "Housing",
    "Education", "Health", "Crime", "Transport", "Environment",
    "Schemes", "Elections", "Jobs", "News", "Ask", "Petitions", "FOI",
])

# ── TAB: Overview ──
with tabs[0]:
    data = get_council_data(council)

    _info = REGISTRY.get(council)
    if _info and council != UK_ALL:
        st.caption(f"Local authority: {_info.authority} · ONS code {_info.gss}")

    _pop = get_population(council)
    _housing = get_housing(council)
    _pop_label = f"Population ({_pop['year']}, live)" if _pop["live"] else "Population"
    _price_label = f"Avg House Price ({_housing['month']}, live)" if _housing.get("live") else "Avg House Price"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="stat-card"><div class="stat-value">{_pop["population"]:,}</div><div class="stat-label">{_pop_label}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-value">GBP {_housing["avg_price"]:,}</div><div class="stat-label">{_price_label}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-value">{data["employment_rate"]}</div><div class="stat-label">Employment Rate</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-value">GBP {data["median_salary"]:,}</div><div class="stat-label">Median Salary</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="stat-card"><div class="stat-value">{data["council_tax"]}</div><div class="stat-label">Council Tax (Band D)</div></div>', unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Your MPs</div>', unsafe_allow_html=True)
        mp = get_mp_data(council)
        if mp and mp[0].get("live"):
            st.caption("Live from the UK Parliament Members API")
        else:
            st.caption("Indicative — verify on parliament.uk")
        for m in mp:
            color = {"Labour": "#e11d48", "Conservative": "#2563eb", "Liberal Democrats": "#f59e0b", "Green": "#22c55e", "Independent": "#8b5cf6"}.get(m['party'], "#64748b")
            st.markdown(f"""
            <div class="data-card">
                <h4>{m['name']}</h4>
                <span style="background: {color}22; color: {color}; border: 1px solid {color}44; border-radius: 20px; padding: 3px 12px; font-size: 12px;">{m['party']}</span>
                <p style="margin-top: 8px;">{m['constituency']}</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Key Issues</div>', unsafe_allow_html=True)
        for issue in data.get("key_issues", []):
            st.markdown(f"""
            <div class="alert-card">
                <p style="color: #f87171; font-weight: 600; margin-bottom: 4px;">{issue['title']}</p>
                <p>{issue['description']}</p>
            </div>
            """, unsafe_allow_html=True)

# ── TAB: Weather ──
with tabs[1]:
    st.markdown('<div class="section-header">Live Weather</div>', unsafe_allow_html=True)
    w = get_weather(council)
    if "error" not in w:
        wc1, wc2, wc3, wc4 = st.columns(4)
        wc1.metric("Temperature", f"{w['temp']}C")
        wc2.metric("Condition", w['condition'])
        wc3.metric("Humidity", f"{w['humidity']}%")
        wc4.metric("Wind", f"{w['wind']} km/h")

        st.markdown("**7-Day Forecast**")
        fcols = st.columns(7)
        for i, f in enumerate(w.get("forecast", [])):
            with fcols[i]:
                st.metric(f["date"][5:], f"{f['max']}C / {f['min']}C", f"{f['rain']}mm")
    else:
        st.error(w['error'])

# ── TAB: Population ──
with tabs[2]:
    st.markdown('<div class="section-header">Population & Demographics</div>', unsafe_allow_html=True)
    data = get_council_data(council)
    pop = get_population(council)
    if pop["live"]:
        st.caption(f"Total population: live ONS mid-{pop['year']} estimate via Nomis. Other figures are indicative samples.")
    else:
        st.caption("Indicative sample figures — the live ONS estimate could not be fetched.")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric(f"Total Population{' (' + pop['year'] + ')' if pop['live'] else ''}", f"{pop['population']:,}")
    p2.metric("Median Age", data.get("median_age", "39"))
    p3.metric("Life Expectancy (M)", f"{data.get('life_exp_m', 78.7)}")
    p4.metric("Life Expectancy (F)", f"{data.get('life_exp_f', 82.4)}")
    st.caption("Source: [ONS Mid-Year Population Estimates](https://www.nomisweb.co.uk)")

# ── TAB: Finance ──
with tabs[3]:
    st.markdown('<div class="section-header">Council Finance & Budget</div>', unsafe_allow_html=True)
    data = get_council_data(council)
    st.metric("Total Budget", f"GBP {data.get('budget', 'N/A')}")
    st.metric("Council Tax Band D", f"GBP {data.get('council_tax', 'N/A')}")

    if data.get("spending"):
        st.markdown("**Spending Breakdown**")
        for area, pct in data["spending"].items():
            st.progress(int(pct.replace('%', '')) / 100, text=f"{area.replace('_', ' ').title()}: {pct}")

    st.markdown("[View full accounts on gov.uk](https://www.gov.uk/government/collections/local-authority-revenue-expenditure-and-financing)")

# ── TAB: Housing ──
with tabs[4]:
    st.markdown('<div class="section-header">Housing Market</div>', unsafe_allow_html=True)
    housing = get_housing(council)
    if housing.get("live"):
        st.caption(f"Average price: live from HM Land Registry UKHPI, {housing['month']}. Waiting list and rents are indicative samples.")
    else:
        st.caption("Indicative sample figures — live UKHPI data could not be fetched for this selection.")
    vs_uk = housing.get("vs_uk")
    h1, h2, h3 = st.columns(3)
    h1.metric("Average Price", f"GBP {housing['avg_price']:,}")
    h2.metric("vs UK Average", f"{vs_uk:+,}" if isinstance(vs_uk, int) else "N/A")
    h3.metric("Waiting List", f"{housing.get('waiting_list', 'N/A'):,}" if isinstance(housing.get('waiting_list'), int) else housing.get('waiting_list', 'N/A'))

    st.markdown("""
    **Schemes Available:**
    - [Right to Buy](https://www.gov.uk/right-to-buy-buying-your-council-home) — up to GBP 102,400 discount for council tenants
    - [Shared Ownership](https://www.gov.uk/shared-ownership-scheme) — buy 25-75% of a home
    - [Help to Buy](https://www.gov.uk/affordable-home-ownership-schemes) — 25% government bonus
    """)

# ── TAB: Education ──
with tabs[5]:
    st.markdown('<div class="section-header">Schools & Education</div>', unsafe_allow_html=True)
    schools = get_schools(council)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Schools", schools['total'])
    s2.metric("Ofsted Outstanding", schools['outstanding'])
    s3.metric("Ofsted Good", schools['good'])
    s4.metric("Requires Improvement", schools['requires_improvement'])
    st.markdown(f"[Find schools in {council}](https://www.gov.uk/school-performance-tables)")

# ── TAB: Health ──
with tabs[6]:
    st.markdown('<div class="section-header">Health & NHS</div>', unsafe_allow_html=True)
    health = get_health_data(council)
    h1, h2, h3 = st.columns(3)
    h1.metric("GP Surgeries", health['gp_surgeries'])
    h2.metric("Hospitals", health['hospitals'])
    h3.metric("A&E Wait (avg)", health['ae_wait'])
    st.markdown("[Find local NHS services](https://www.nhs.uk/service-search)")

# ── TAB: Crime ──
with tabs[7]:
    st.markdown('<div class="section-header">Crime Statistics</div>', unsafe_allow_html=True)
    crime = get_crime_stats(council)
    if crime.get("live"):
        st.caption(f"Live from Police UK · {crime['month']} · street-level crime within about a mile of the council centre")
        total_label = "Crimes (latest month)"
    else:
        st.caption("Indicative sample figures — live Police UK data is not available for this selection")
        total_label = "Total Crimes (indicative)"
    cr1, cr2, cr3, cr4 = st.columns(4)
    cr1.metric(total_label, f"{crime['total']:,}")
    cr2.metric("Anti-Social", f"{crime['antisocial']:,}")
    cr3.metric("Violent Crime", f"{crime['violent']:,}")
    cr4.metric("Burglary", f"{crime['burglary']:,}")
    st.markdown("[View full data on Police UK](https://www.police.uk)")

# ── TAB: Transport ──
with tabs[8]:
    st.markdown('<div class="section-header">Transport</div>', unsafe_allow_html=True)
    transport = get_transport(council)
    st.markdown(f"**Nearest Train Station:** {transport['station']}")
    st.markdown(f"**Bus Provider:** {transport['bus']}")
    st.markdown(f"**Average Commute:** {transport['avg_commute']}")
    st.markdown("[Plan your journey](https://www.thetrainline.com)")

# ── TAB: Environment ──
with tabs[9]:
    st.markdown('<div class="section-header">Environment</div>', unsafe_allow_html=True)
    env = get_environment(council)
    aq = get_air_quality(council)
    e1, e2, e3 = st.columns(3)
    if aq["live"]:
        e1.metric("Air Quality (EAQI)", f"{aq['aqi']:.0f}", aq["band"], delta_color="off")
    else:
        e1.metric("Air Quality Index", env['aqi'])
    e2.metric("Recycling Rate", env['recycling_rate'])
    e3.metric("Green Spaces", env['green_spaces'])
    if aq["live"]:
        st.caption(
            f"Live European Air Quality Index from Open-Meteo · PM2.5 {aq['pm2_5']} · "
            f"PM10 {aq['pm10']} · NO2 {aq['no2']} µg/m³. Recycling rate and green spaces "
            "are indicative samples."
        )
    else:
        st.caption("Air quality could not be fetched live; the figures shown are indicative samples.")
    st.markdown("[Check air quality (DEFRA)](https://uk-air.defra.gov.uk/)")

    # Flood warnings — live from the Environment Agency
    st.markdown('<div class="section-header">Flood warnings</div>', unsafe_allow_html=True)
    floods = get_floods(council)
    if not floods["live"]:
        st.caption("Could not reach the Environment Agency flood service. Check gov.uk directly.")
    else:
        active = [w for w in (floods["warnings"] or []) if isinstance(w["level"], int) and w["level"] <= 3]
        if not active:
            st.success(f"No active flood warnings near {council}.")
        else:
            for w in active:
                color = {1: "#ef4444", 2: "#f97316", 3: "#3b82f6"}.get(w["level"], "#64748b")
                river = f" — {w['river_or_sea']}" if w["river_or_sea"] else ""
                st.markdown(f"""
                <div class="alert-card" style="border-left-color: {color};">
                    <p style="color: {color}; font-weight: 700; margin: 0;">{w['severity']}</p>
                    <p style="margin: 4px 0 0 0;">{w['description']}{river}</p>
                </div>
                """, unsafe_allow_html=True)
        st.caption("Live from the Environment Agency, within about 30km of the council centre.")
    st.markdown("[Check for flooding (gov.uk)](https://check-for-flooding.service.gov.uk)")

# ── TAB: Schemes ──
with tabs[10]:
    st.markdown('<div class="section-header">Government Schemes & Benefits</div>', unsafe_allow_html=True)
    st.markdown("[Check all benefits you're entitled to](https://www.gov.uk/check-benefits-financial-support)")

    schemes = get_schemes()
    category_colors = {"Income": "#3b82f6", "Disability": "#8b5cf6", "Housing": "#f59e0b",
                      "Family": "#ec4899", "Pension": "#64748b", "Energy": "#22c55e",
                      "Tax": "#06b6d4", "Transport": "#f97316", "Education": "#14b8a6",
                      "Immigration": "#6366f1", "Business": "#ef4444", "Legal": "#a855f7"}

    category_filter = st.selectbox("Filter by category", ["All"] + list(schemes.keys()))

    categories = [category_filter] if category_filter != "All" else list(schemes.keys())
    for cat in categories:
        cat_display = cat.replace("_", " ").title()
        st.markdown(f"#### {cat_display}")
        for s in schemes[cat]:
            color = category_colors.get(s.get("category", ""), "#64748b")
            st.markdown(f"""
            <div class="scheme-card">
                <a href="{s['link']}" target="_blank" style="font-weight: 700; font-size: 1.05rem;">{s['name']}</a>
                <span style="background: {color}22; color: {color}; border: 1px solid {color}44; border-radius: 20px; padding: 2px 10px; font-size: 11px; margin-left: 8px;">{s.get('category', '')}</span>
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0;">{s['who']}</p>
                <p style="color: #22c55e; font-weight: 600;">GBP {s['amount']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Essential Services
    st.markdown('<div class="section-header">Essential Services & Helplines</div>', unsafe_allow_html=True)
    services = get_essential_services()

    st.markdown("##### Emergency Numbers")
    for s in services["emergency"]:
        st.markdown(f"""
        <div class="alert-card">
            <span style="color: #f87171; font-weight: 700; font-size: 1.1rem;">{s['number']}</span>
            <span style="color: white; margin-left: 12px; font-weight: 600;">{s['name']}</span>
            <p style="color: #94a3b8; margin: 4px 0 0 0;">{s['for']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### Government Services")
    for s in services["government"]:
        st.markdown(f"""
        <div class="data-card">
            <a href="{s['url']}" target="_blank"><h4>{s['name']}</h4></a>
            <p>{s['for']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### NHS Services")
    for s in services["nhs"]:
        st.markdown(f"""
        <div class="data-card">
            <a href="{s['url']}" target="_blank"><h4>{s['name']}</h4></a>
            <p>{s['for']}</p>
        </div>
        """, unsafe_allow_html=True)

# ── TAB: Elections ──
with tabs[11]:
    st.markdown('<div class="section-header">Election Results</div>', unsafe_allow_html=True)
    mp = get_mp_data(council)
    if mp and mp[0].get("live"):
        st.caption("Current members live from the UK Parliament Members API; majorities from each seat's latest election result")
    else:
        st.caption("Indicative — verify on parliament.uk")
    for m in mp:
        color = {"Labour": "#e11d48", "Conservative": "#2563eb", "Liberal Democrats": "#f59e0b"}.get(m['party'], "#64748b")
        majority = m.get('majority')
        majority_text = f"{majority:,}" if isinstance(majority, int) and majority > 0 else "N/A"
        st.markdown(f"""
        <div class="data-card">
            <h4>{m['constituency']}</h4>
            <p><strong>{m['name']}</strong> — <span style="color: {color};">{m['party']}</span></p>
            <p>Majority: {majority_text}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("[Full election results](https://www.electoralcommission.org.uk/)")

# ── TAB: Jobs ──
with tabs[12]:
    st.markdown('<div class="section-header">Jobs & Opportunities</div>', unsafe_allow_html=True)
    jobs = get_jobs_data()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Job Sites")
        for j in jobs["job_sites"]:
            st.markdown(f"""
            <div class="data-card">
                <a href="{j['url']}" target="_blank"><h4>{j['name']}</h4></a>
                <p>{j['for']}</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("##### Career Support")
        for j in jobs["career_support"]:
            st.markdown(f"""
            <div class="scheme-card">
                <a href="{j['url']}" target="_blank" style="font-weight: 700;">{j['name']}</a>
                <p style="color: #94a3b8; margin: 4px 0 0 0;">{j['for']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"[Search Indeed for {council} jobs](https://uk.indeed.com/jobs?l={council.replace(' ', '+')})")

# ── TAB: News ──
with tabs[13]:
    st.markdown('<div class="section-header">UK News & Government Announcements</div>', unsafe_allow_html=True)
    st.caption(
        "Headlines from BBC News UK (RSS) and gov.uk announcements (Atom). "
        "Cached for 24 hours; click a headline to read the full article at the source."
    )

    news_items = get_news(limit_per_source=10)
    if not news_items:
        st.info(
            "News feeds are unavailable right now — likely a temporary upstream "
            "issue at BBC News or gov.uk. Try again in a few minutes."
        )
    else:
        gov_items = [n for n in news_items if n["source"] == "gov.uk"]
        bbc_items = [n for n in news_items if n["source"] == "BBC News"]

        col_gov, col_bbc = st.columns(2)

        with col_gov:
            st.markdown("##### gov.uk announcements")
            if not gov_items:
                st.caption("No gov.uk items available.")
            for item in gov_items:
                published = item.get("published") or ""
                st.markdown(f"""
                <div class="data-card">
                    <a href="{item['link']}" target="_blank"><h4>{item['title']}</h4></a>
                    <p style="color: #94a3b8; font-size: 0.78rem;">{published}</p>
                </div>
                """, unsafe_allow_html=True)

        with col_bbc:
            st.markdown("##### BBC News UK")
            if not bbc_items:
                st.caption("No BBC items available.")
            for item in bbc_items:
                published = item.get("published") or ""
                st.markdown(f"""
                <div class="data-card">
                    <a href="{item['link']}" target="_blank"><h4>{item['title']}</h4></a>
                    <p style="color: #94a3b8; font-size: 0.78rem;">{published}</p>
                </div>
                """, unsafe_allow_html=True)

        st.caption(
            "Attribution: BBC News content © BBC, linked back to bbc.co.uk. "
            "gov.uk announcements published under Open Government Licence v3.0."
        )

# ── TAB: Ask ──
with tabs[14]:
    st.markdown('<div class="section-header">Ask in plain English</div>', unsafe_allow_html=True)
    st.caption(
        f"Answers come from Claude, grounded in this dashboard's data for {council}, "
        "and are general information, not advice. Figures are labelled live or "
        "indicative. Don't include personal details in your question."
    )

    operator_key = os.getenv("ANTHROPIC_API_KEY", "")
    api_key = operator_key or st.session_state.get("visitor_api_key", "")
    if not operator_key:
        with st.expander("Use your own Anthropic API key (optional)"):
            st.caption(
                "Held in this browser session only, never stored. Without any key "
                "the tab falls back to a keyword search of schemes and services."
            )
            entered = st.text_input("Anthropic API key", type="password", key="visitor_api_key_input")
            if entered:
                st.session_state["visitor_api_key"] = entered
                api_key = entered

    question = st.text_input(
        "Your question about UK public services",
        max_chars=ask.MAX_QUESTION_CHARS,
        placeholder="e.g. What help is there with energy bills?",
    )

    if st.button("Ask") and question.strip():
        if api_key:
            session_used = st.session_state.get("ask_count", 0)
            if operator_key and session_used >= ask.SESSION_LIMIT:
                st.warning("Question limit reached for this session. Come back later, or use your own API key.")
            elif operator_key and ask.hourly_used() >= ask.HOURLY_LIMIT:
                st.warning("The shared question budget for this hour is used up. Try again later, or use your own API key.")
            else:
                with st.spinner("Asking Claude..."):
                    result = ask.ask_claude(question, council, api_key)
                if "answer" in result:
                    if operator_key:
                        st.session_state["ask_count"] = session_used + 1
                        ask.record_use()
                    st.markdown(result["answer"])
                    st.caption("Generated by Claude. Verify anything important at the official links in each tab.")
                else:
                    st.error(result["error"])
        else:
            matches = ask.keyword_fallback(question)
            st.caption("No API key configured, so this is a keyword match over the schemes and services tables, not an AI answer.")
            if matches:
                for m in matches:
                    link_html = f'<a href="{m["link"]}" target="_blank" style="font-weight: 700;">{m["name"]}</a>' if m.get("link") else f'<span style="font-weight: 700; color: #f8fafc;">{m["name"]}</span>'
                    st.markdown(f"""
                    <div class="scheme-card">
                        {link_html}
                        <p style="color: #94a3b8; margin: 4px 0 0 0;">{m["detail"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nothing matched. Try different words, browse the Schemes tab, or start from [gov.uk](https://www.gov.uk/check-benefits-financial-support).")

# ── TAB: Petitions ──
with tabs[15]:
    st.markdown('<div class="section-header">UK Parliament Petitions</div>', unsafe_allow_html=True)
    pet = get_petitions()
    if pet["live"] and pet["petitions"]:
        st.caption(
            "Live from the UK Parliament petitions API — top open petitions by "
            "signatures, nationwide (not council-specific). 10,000 signatures earns "
            "a government response; 100,000 makes a petition eligible for debate."
        )
        for p in pet["petitions"]:
            if p["debated"]:
                status = '<span style="color:#a855f7;">Debated in Parliament</span>'
            elif p["government_responded"]:
                status = '<span style="color:#f59e0b;">Government responded</span>'
            elif p["signatures"] >= 100_000:
                status = '<span style="color:#a855f7;">Past debate threshold</span>'
            elif p["signatures"] >= 10_000:
                status = '<span style="color:#f59e0b;">Past response threshold</span>'
            else:
                status = '<span style="color:#94a3b8;">Gathering signatures</span>'
            st.markdown(f"""
            <div class="data-card">
                <a href="{p['url']}" target="_blank" style="font-weight:700; font-size:1.02rem;">{p['action']}</a>
                <p style="margin:6px 0 0 0;"><span style="color:#22c55e; font-weight:700;">{p['signatures']:,}</span> signatures &nbsp;·&nbsp; {status}</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(p["signatures"] / 100_000, 1.0))
        st.markdown("[Start or search petitions on petition.parliament.uk](https://petition.parliament.uk)")
    else:
        st.info("The petitions service is unavailable right now. You can browse petitions directly at [petition.parliament.uk](https://petition.parliament.uk).")

# ── TAB: FOI ──
with tabs[16]:
    st.markdown('<div class="section-header">Freedom of Information</div>', unsafe_allow_html=True)
    links = foi.foi_links(council)
    if links["authority"]:
        st.markdown(
            f"Anyone can ask **{links['authority']}** for recorded information under the "
            f"Freedom of Information Act 2000. By law they must respond within "
            f"**{links['response_days']} working days**, and it is free to ask."
        )
        st.markdown(f"- **[Start a request to {links['authority']} on WhatDoTheyKnow]({links['whatdotheyknow']})** — free, and it publishes the answer for everyone")
    else:
        st.markdown(
            "Anyone can ask a public authority for recorded information under the "
            f"Freedom of Information Act 2000, and they must respond within "
            f"**{links['response_days']} working days**. Pick a council in the sidebar for a direct request link."
        )
        st.markdown(f"- **[Find your authority on WhatDoTheyKnow]({links['whatdotheyknow']})**")
    st.markdown(f"- [How to make an FOI request (gov.uk)]({links['gov_guide']})")
    st.markdown(f"- [Your right to official information (ICO)]({links['ico_guide']})")

    st.markdown("**Request template** — copy, edit the details, and send")
    st.code(foi.request_template(links["authority"]), language=None)
    st.caption(
        "FOI covers recorded information held by the authority (spending, policies, "
        "correspondence). For your own personal data, use a Subject Access Request instead."
    )

# ── Footer ──
st.markdown("""
<div class="footer">
    ForThePeople UK — Independent Citizen Transparency Platform<br>
    Data from ONS, gov.uk, NHS Digital, DfE, Police UK, Met Office, Open-Meteo, BBC News<br>
    Not affiliated with any government body. All data is publicly available.<br>
    Built with Python + Streamlit
</div>
""", unsafe_allow_html=True)
