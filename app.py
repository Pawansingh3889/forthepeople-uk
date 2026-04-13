"""ForThePeople UK — Citizen Transparency Platform

Free, real-time council-level government data dashboards for the UK.
Independent. No login. No paywall. Open data.

Usage:
    streamlit run app.py
"""
import streamlit as st
import requests
from data import councils, get_weather, get_council_data, get_mp_data, get_schemes, get_housing, get_schools, get_crime_stats, get_health_data, get_transport, get_environment

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

region = st.sidebar.selectbox("Select Region", [
    "Yorkshire and the Humber",
    "North East",
    "North West",
    "East Midlands",
    "West Midlands",
    "East of England",
    "London",
    "South East",
    "South West",
])

council_list = councils.get(region, ["Select a council"])
council = st.sidebar.selectbox("Select Council", council_list)

st.sidebar.divider()
st.sidebar.markdown("**Data Sources**")
st.sidebar.caption("ONS | gov.uk | NHS Digital | DfE | Police UK | Met Office | Open Data")
st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.caption("Independent platform. Not affiliated with government. All data from public open data sources.")

# ── Header ──
st.markdown(f"""
<div class="main-header">
    <h1>ForThePeople UK</h1>
    <p>Free, real-time council-level government data for <strong>{council}</strong></p>
    <p style="font-size: 0.8rem; color: #475569;">Independent. No login. No paywall. Open data.</p>
</div>
""", unsafe_allow_html=True)

# ── Dashboard Tabs ──
tabs = st.tabs([
    "Overview", "Weather", "Population", "Finance", "Housing",
    "Education", "Health", "Crime", "Transport", "Environment",
    "Schemes", "Elections", "Jobs",
])

# ── TAB: Overview ──
with tabs[0]:
    data = get_council_data(council)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="stat-card"><div class="stat-value">{data["population"]:,}</div><div class="stat-label">Population</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-value">GBP {data["avg_house_price"]:,}</div><div class="stat-label">Avg House Price</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-value">{data["employment_rate"]}</div><div class="stat-label">Employment Rate</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-value">GBP {data["median_salary"]:,}</div><div class="stat-label">Median Salary</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="stat-card"><div class="stat-value">{data["council_tax"]}</div><div class="stat-label">Council Tax (Band D)</div></div>', unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Your MP</div>', unsafe_allow_html=True)
        mp = get_mp_data(council)
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
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total Population", f"{data['population']:,}")
    p2.metric("Median Age", data.get("median_age", "39"))
    p3.metric("Life Expectancy (M)", f"{data.get('life_exp_m', 78.7)}")
    p4.metric("Life Expectancy (F)", f"{data.get('life_exp_f', 82.4)}")
    st.caption(f"Source: ONS Mid-Year Population Estimates")

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

    st.markdown(f"[View full accounts on gov.uk](https://www.gov.uk/government/collections/local-authority-revenue-expenditure-and-financing)")

# ── TAB: Housing ──
with tabs[4]:
    st.markdown('<div class="section-header">Housing Market</div>', unsafe_allow_html=True)
    housing = get_housing(council)
    h1, h2, h3 = st.columns(3)
    h1.metric("Average Price", f"GBP {housing['avg_price']:,}")
    h2.metric("vs UK Average", f"{housing['vs_uk']:+,}")
    h3.metric("Waiting List", f"{housing.get('waiting_list', 'N/A'):,}" if isinstance(housing.get('waiting_list'), int) else housing.get('waiting_list', 'N/A'))

    st.markdown(f"""
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
    st.markdown(f"[Find local NHS services](https://www.nhs.uk/service-search)")

# ── TAB: Crime ──
with tabs[7]:
    st.markdown('<div class="section-header">Crime Statistics</div>', unsafe_allow_html=True)
    crime = get_crime_stats(council)
    cr1, cr2, cr3, cr4 = st.columns(4)
    cr1.metric("Total Crimes (12mo)", f"{crime['total']:,}")
    cr2.metric("Anti-Social", f"{crime['antisocial']:,}")
    cr3.metric("Violent Crime", f"{crime['violent']:,}")
    cr4.metric("Burglary", f"{crime['burglary']:,}")
    st.markdown(f"[View full data on Police UK](https://www.police.uk)")

# ── TAB: Transport ──
with tabs[8]:
    st.markdown('<div class="section-header">Transport</div>', unsafe_allow_html=True)
    transport = get_transport(council)
    st.markdown(f"**Nearest Train Station:** {transport['station']}")
    st.markdown(f"**Bus Provider:** {transport['bus']}")
    st.markdown(f"**Average Commute:** {transport['avg_commute']}")
    st.markdown(f"[Plan your journey](https://www.thetrainline.com)")

# ── TAB: Environment ──
with tabs[9]:
    st.markdown('<div class="section-header">Environment</div>', unsafe_allow_html=True)
    env = get_environment(council)
    e1, e2, e3 = st.columns(3)
    e1.metric("Recycling Rate", env['recycling_rate'])
    e2.metric("Air Quality Index", env['aqi'])
    e3.metric("Green Spaces", env['green_spaces'])
    st.markdown(f"[Check air quality](https://uk-air.defra.gov.uk/)")

# ── TAB: Schemes ──
with tabs[10]:
    st.markdown('<div class="section-header">Government Schemes & Benefits</div>', unsafe_allow_html=True)
    schemes = get_schemes()
    for s in schemes:
        st.markdown(f"""
        <div class="scheme-card">
            <a href="{s['link']}" target="_blank" style="font-weight: 700; font-size: 1.05rem;">{s['name']}</a>
            <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0;">{s['who']}</p>
            <p style="color: #22c55e; font-weight: 600;">GBP {s['amount']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("[Check all benefits you're entitled to](https://www.gov.uk/check-benefits-financial-support)")

# ── TAB: Elections ──
with tabs[11]:
    st.markdown('<div class="section-header">Election Results</div>', unsafe_allow_html=True)
    mp = get_mp_data(council)
    for m in mp:
        color = {"Labour": "#e11d48", "Conservative": "#2563eb", "Liberal Democrats": "#f59e0b"}.get(m['party'], "#64748b")
        st.markdown(f"""
        <div class="data-card">
            <h4>{m['constituency']}</h4>
            <p><strong>{m['name']}</strong> — <span style="color: {color};">{m['party']}</span></p>
            <p>Majority: {m.get('majority', 'N/A'):,}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("[Full election results](https://www.electoralcommission.org.uk/)")

# ── TAB: Jobs ──
with tabs[12]:
    st.markdown('<div class="section-header">Jobs & Opportunities</div>', unsafe_allow_html=True)
    st.markdown(f"""
    **Job Sites for {council}:**
    - [Indeed — {council}](https://uk.indeed.com/jobs?l={council.replace(' ', '+')})
    - [Reed — {council}](https://www.reed.co.uk/jobs/{council.lower().replace(' ', '-')})
    - [Civil Service Jobs](https://www.civilservicejobs.service.gov.uk)
    - [NHS Jobs](https://www.jobs.nhs.uk)
    - [Find an Apprenticeship](https://www.findapprenticeship.service.gov.uk)
    - [Universal Jobmatch](https://www.gov.uk/find-a-job)
    """)

# ── Footer ──
st.markdown("""
<div class="footer">
    ForThePeople UK — Independent Citizen Transparency Platform<br>
    Data from ONS, gov.uk, NHS Digital, DfE, Police UK, Met Office, Open-Meteo<br>
    Not affiliated with any government body. All data is publicly available.<br>
    Built with Python + Streamlit
</div>
""", unsafe_allow_html=True)
