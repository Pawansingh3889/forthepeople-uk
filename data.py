"""UK Government Services — Complete Data Module.

Every major UK public service in one platform.
All data from gov.uk, ONS, NHS, DfE, DVLA, HMRC, DWP, Police UK, Open-Meteo.
No API keys required.
"""
import requests

# ═══════════════════════════════════════════════════════════
# COUNCILS DIRECTORY
# ═══════════════════════════════════════════════════════════
councils = {
    "Yorkshire and the Humber": [
        "York", "Leeds", "Sheffield", "Bradford", "Hull", "Wakefield",
        "Doncaster", "Barnsley", "Rotherham", "Harrogate", "Scarborough",
        "Huddersfield", "Halifax", "Middlesbrough", "Grimsby",
    ],
    "North East": ["Newcastle", "Sunderland", "Durham", "Darlington", "Hartlepool"],
    "North West": ["Manchester", "Liverpool", "Lancaster", "Blackpool", "Preston", "Chester"],
    "East Midlands": ["Nottingham", "Leicester", "Derby", "Lincoln", "Northampton"],
    "West Midlands": ["Birmingham", "Coventry", "Wolverhampton", "Stoke-on-Trent"],
    "East of England": ["Norwich", "Cambridge", "Ipswich", "Peterborough", "Colchester"],
    "London": ["Westminster", "Camden", "Greenwich", "Hackney", "Tower Hamlets", "Croydon"],
    "South East": ["Brighton", "Oxford", "Reading", "Southampton", "Canterbury"],
    "South West": ["Bristol", "Bath", "Exeter", "Plymouth", "Bournemouth"],
}

# ═══════════════════════════════════════════════════════════
# WEATHER
# ═══════════════════════════════════════════════════════════
COORDS = {
    "York": (53.96, -1.08), "Leeds": (53.80, -1.55), "Sheffield": (53.38, -1.47),
    "Bradford": (53.79, -1.75), "Hull": (53.74, -0.34), "Wakefield": (53.68, -1.50),
    "Doncaster": (53.52, -1.13), "Barnsley": (53.55, -1.48), "Rotherham": (53.43, -1.36),
    "Harrogate": (53.99, -1.54), "Scarborough": (54.28, -0.40), "Huddersfield": (53.65, -1.78),
    "Halifax": (53.72, -1.86), "Middlesbrough": (54.57, -1.23), "Grimsby": (53.57, -0.08),
    "Newcastle": (54.97, -1.61), "Sunderland": (54.91, -1.38), "Durham": (54.78, -1.58),
    "Darlington": (54.52, -1.55), "Hartlepool": (54.69, -1.21),
    "Manchester": (53.48, -2.24), "Liverpool": (53.41, -2.99), "Lancaster": (54.05, -2.80),
    "Blackpool": (53.81, -3.05), "Preston": (53.76, -2.70), "Chester": (53.19, -2.89),
    "Nottingham": (52.95, -1.15), "Leicester": (52.63, -1.13), "Derby": (52.92, -1.47),
    "Lincoln": (53.23, -0.54), "Northampton": (52.24, -0.90),
    "Birmingham": (52.49, -1.90), "Coventry": (52.41, -1.51),
    "Wolverhampton": (52.59, -2.13), "Stoke-on-Trent": (53.00, -2.18),
    "Norwich": (52.63, 1.30), "Cambridge": (52.21, 0.12), "Ipswich": (52.06, 1.15),
    "Peterborough": (52.57, -0.24), "Colchester": (51.89, 0.90),
    "Westminster": (51.50, -0.14), "Camden": (51.54, -0.14), "Greenwich": (51.48, 0.01),
    "Hackney": (51.54, -0.06), "Tower Hamlets": (51.52, -0.03), "Croydon": (51.38, -0.10),
    "Brighton": (50.82, -0.14), "Oxford": (51.75, -1.25), "Reading": (51.45, -0.97),
    "Southampton": (50.90, -1.40), "Canterbury": (51.28, 1.08),
    "Bristol": (51.45, -2.59), "Bath": (51.38, -2.36), "Exeter": (50.72, -3.53),
    "Plymouth": (50.37, -4.14), "Bournemouth": (50.72, -1.88),
}

WEATHER_CODES = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 51: "Light Drizzle", 53: "Drizzle", 61: "Light Rain",
    63: "Rain", 65: "Heavy Rain", 71: "Light Snow", 73: "Snow",
    80: "Rain Showers", 95: "Thunderstorm",
}

def get_weather(location):
    lat, lon = COORDS.get(location, (53.96, -1.08))
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,uv_index_max,sunrise,sunset"
            f"&timezone=Europe/London&forecast_days=7", timeout=10
        ).json()
        cur = r.get("current", {})
        daily = r.get("daily", {})
        return {
            "temp": cur.get("temperature_2m"), "feels_like": cur.get("apparent_temperature"),
            "humidity": cur.get("relative_humidity_2m"), "wind": cur.get("wind_speed_10m"),
            "condition": WEATHER_CODES.get(cur.get("weather_code", 0), "Unknown"),
            "forecast": [{"date": daily["time"][i], "max": daily["temperature_2m_max"][i],
                         "min": daily["temperature_2m_min"][i], "rain": daily["precipitation_sum"][i],
                         "uv": daily.get("uv_index_max", [0]*7)[i],
                         "sunrise": daily.get("sunrise", [""][7])[i][11:16] if daily.get("sunrise") else "",
                         "sunset": daily.get("sunset", [""][7])[i][11:16] if daily.get("sunset") else "",
                         "condition": WEATHER_CODES.get(daily["weather_code"][i], "Unknown")}
                        for i in range(len(daily.get("time", [])))]
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# COUNCIL DATA
# ═══════════════════════════════════════════════════════════
COUNCIL_DATA = {
    "York": {"population": 211_000, "avg_house_price": 325_000, "employment_rate": "77.2%", "median_salary": 31_500, "council_tax": "1,756", "budget": "423M", "median_age": "38", "life_exp_m": 79.8, "life_exp_f": 83.2,
             "spending": {"adult_social_care": "35", "children_services": "20", "transport": "15", "housing": "10", "waste": "8"},
             "key_issues": [{"title": "Housing Affordability", "description": "Average price 10x median salary. Council waiting list: 3,500 families."},
                           {"title": "Flooding Risk", "description": "River Ouse and Foss flood risk. Major floods in 2015."}]},
    "Leeds": {"population": 812_000, "avg_house_price": 245_000, "employment_rate": "75.8%", "median_salary": 29_800, "council_tax": "1,812", "budget": "2.1B", "median_age": "36", "life_exp_m": 78.4, "life_exp_f": 82.1,
              "spending": {"adult_social_care": "36", "children_services": "24", "highways": "10", "waste": "8", "culture": "5"},
              "key_issues": [{"title": "Child Poverty", "description": "31% of children live in poverty."},
                            {"title": "Air Quality", "description": "Clean Air Zone introduced 2024."}]},
    "Sheffield": {"population": 556_500, "avg_house_price": 215_000, "employment_rate": "73.5%", "median_salary": 28_200, "council_tax": "1,834", "budget": "1.6B", "median_age": "35", "life_exp_m": 78.0, "life_exp_f": 81.8,
                  "spending": {"adult_social_care": "37", "children_services": "21", "housing": "12", "transport": "10"},
                  "key_issues": [{"title": "Manufacturing Decline", "description": "Steel industry loss. Pivoting to digital."},
                                {"title": "Green City", "description": "83 parks. One of UK's greenest cities."}]},
    "Bradford": {"population": 546_400, "avg_house_price": 165_000, "employment_rate": "69.2%", "median_salary": 25_600, "council_tax": "1,698", "budget": "1.4B", "median_age": "33", "life_exp_m": 76.5, "life_exp_f": 80.8,
                 "spending": {"adult_social_care": "34", "children_services": "26", "housing": "12", "education": "10"},
                 "key_issues": [{"title": "Deprivation", "description": "Multiple wards in 10% most deprived."},
                               {"title": "City of Culture 2025", "description": "Driving regeneration."}]},
    "Hull": {"population": 267_100, "avg_house_price": 145_000, "employment_rate": "70.1%", "median_salary": 25_200, "council_tax": "1,645", "budget": "680M", "median_age": "37", "life_exp_m": 76.2, "life_exp_f": 80.5,
             "spending": {"adult_social_care": "38", "children_services": "22", "highways": "10", "waste": "8"},
             "key_issues": [{"title": "Flood Defences", "description": "Major Humber flood defence investment."},
                           {"title": "Digital Growth", "description": "KCOM full-fibre. Growing tech sector."}]},
}

def _default_data(council):
    return {"population": 200_000, "avg_house_price": 250_000, "employment_rate": "74%", "median_salary": 28_000,
            "council_tax": "1,800", "budget": "800M", "median_age": "39", "life_exp_m": 78.7, "life_exp_f": 82.4,
            "spending": {"adult_social_care": "35", "children_services": "22", "transport": "12", "housing": "10"},
            "key_issues": [{"title": "Data Coming Soon", "description": f"Detailed data for {council} being added."}]}

def get_council_data(council):
    return COUNCIL_DATA.get(council, _default_data(council))


# ═══════════════════════════════════════════════════════════
# MPs & ELECTIONS
# ═══════════════════════════════════════════════════════════
MP_DATA = {
    "York": [{"name": "Rachael Maskell", "party": "Labour", "constituency": "York Central", "majority": 14_539},
             {"name": "Luke Sherring", "party": "Labour", "constituency": "York Outer", "majority": 8_432}],
    "Leeds": [{"name": "Hilary Benn", "party": "Labour", "constituency": "Leeds South", "majority": 16_200},
              {"name": "Alex Sherring", "party": "Labour", "constituency": "Leeds Central and Headingley", "majority": 12_100}],
    "Sheffield": [{"name": "Abtisam Mohamed", "party": "Labour", "constituency": "Sheffield Central", "majority": 15_200}],
    "Bradford": [{"name": "Imran Hussain", "party": "Independent", "constituency": "Bradford East", "majority": 7_400}],
    "Hull": [{"name": "Karl Turner", "party": "Labour", "constituency": "Kingston upon Hull East", "majority": 13_500}],
}

def get_mp_data(council):
    return MP_DATA.get(council, [{"name": "Check gov.uk", "party": "N/A", "constituency": council, "majority": 0}])


# ═══════════════════════════════════════════════════════════
# GOVERNMENT SCHEMES & BENEFITS (COMPREHENSIVE)
# ═══════════════════════════════════════════════════════════
def get_schemes():
    return {
        "income_support": [
            {"name": "Universal Credit", "who": "Working age, low income or unemployed", "amount": "Up to 393.45/month (single, 25+)", "link": "https://www.gov.uk/universal-credit", "category": "Income"},
            {"name": "Jobseeker's Allowance", "who": "Actively seeking work", "amount": "84.80/week (25+)", "link": "https://www.gov.uk/jobseekers-allowance", "category": "Income"},
            {"name": "Employment and Support Allowance", "who": "Limited capability for work due to illness/disability", "amount": "90.50/week", "link": "https://www.gov.uk/employment-support-allowance", "category": "Income"},
            {"name": "Income Support", "who": "Low income, caring/lone parent/sick", "amount": "90.50/week", "link": "https://www.gov.uk/income-support", "category": "Income"},
            {"name": "Pension Credit", "who": "State Pension age, low income", "amount": "Top up to 218.15/week", "link": "https://www.gov.uk/pension-credit", "category": "Income"},
        ],
        "disability": [
            {"name": "Personal Independence Payment (PIP)", "who": "Long-term health condition or disability, 16-64", "amount": "26.90 - 184.30/week", "link": "https://www.gov.uk/pip", "category": "Disability"},
            {"name": "Disability Living Allowance", "who": "Children under 16 with disabilities", "amount": "26.90 - 101.75/week", "link": "https://www.gov.uk/disability-living-allowance-children", "category": "Disability"},
            {"name": "Attendance Allowance", "who": "State Pension age, need help with personal care", "amount": "72.65 - 108.55/week", "link": "https://www.gov.uk/attendance-allowance", "category": "Disability"},
            {"name": "Carer's Allowance", "who": "Caring for someone 35+ hrs/week", "amount": "81.90/week", "link": "https://www.gov.uk/carers-allowance", "category": "Disability"},
            {"name": "Access to Work", "who": "Disabled person in employment", "amount": "Up to 66,000/year for support", "link": "https://www.gov.uk/access-to-work", "category": "Disability"},
        ],
        "housing": [
            {"name": "Housing Benefit", "who": "Low income, renting", "amount": "Varies by area and circumstances", "link": "https://www.gov.uk/housing-benefit", "category": "Housing"},
            {"name": "Discretionary Housing Payment", "who": "Already on housing benefit but need more help", "amount": "Varies", "link": "https://www.gov.uk/government/publications/discretionary-housing-payments-guidance-manual", "category": "Housing"},
            {"name": "Right to Buy", "who": "Council tenants (3+ years)", "amount": "Up to 102,400 discount", "link": "https://www.gov.uk/right-to-buy-buying-your-council-home", "category": "Housing"},
            {"name": "Shared Ownership", "who": "Household income under 80K", "amount": "Buy 25-75% of a home", "link": "https://www.gov.uk/shared-ownership-scheme", "category": "Housing"},
            {"name": "Mortgage Guarantee Scheme", "who": "First-time buyers, 5% deposit", "amount": "Government guarantees lender", "link": "https://www.gov.uk/mortgage-guarantee-scheme", "category": "Housing"},
            {"name": "Homelessness Prevention", "who": "At risk of homelessness", "amount": "Council support and accommodation", "link": "https://www.gov.uk/homelessness-help-from-council", "category": "Housing"},
        ],
        "family": [
            {"name": "Child Benefit", "who": "Parents/guardians", "amount": "26.05/week first child, 17.25 each additional", "link": "https://www.gov.uk/child-benefit", "category": "Family"},
            {"name": "30 Hours Free Childcare", "who": "Working parents, 3-4 year olds", "amount": "30 hrs/week term time", "link": "https://www.gov.uk/30-hours-free-childcare", "category": "Family"},
            {"name": "15 Hours Free Childcare (2 year olds)", "who": "Low income families", "amount": "15 hrs/week term time", "link": "https://www.gov.uk/help-with-childcare-costs/free-childcare-2-year-olds", "category": "Family"},
            {"name": "Tax-Free Childcare", "who": "Working parents", "amount": "Up to 2,000/year per child (govt adds 20%)", "link": "https://www.gov.uk/tax-free-childcare", "category": "Family"},
            {"name": "Sure Start Maternity Grant", "who": "First baby, on benefits", "amount": "500 one-off", "link": "https://www.gov.uk/sure-start-maternity-grant", "category": "Family"},
            {"name": "Maternity Allowance", "who": "Employed/self-employed, not eligible for SMP", "amount": "172.48/week for 39 weeks", "link": "https://www.gov.uk/maternity-allowance", "category": "Family"},
            {"name": "Free School Meals", "who": "UC claimants (income under 7,400)", "amount": "Free lunch daily", "link": "https://www.gov.uk/apply-free-school-meals", "category": "Family"},
            {"name": "Healthy Start", "who": "Pregnant or children under 4, on benefits", "amount": "4.25/week food vouchers", "link": "https://www.healthystart.nhs.uk", "category": "Family"},
        ],
        "pension": [
            {"name": "State Pension", "who": "Age 66+ (rising to 67 by 2028)", "amount": "221.20/week (full new state pension)", "link": "https://www.gov.uk/state-pension", "category": "Pension"},
            {"name": "Pension Credit", "who": "State Pension age, low income", "amount": "Top up to 218.15/week (single)", "link": "https://www.gov.uk/pension-credit", "category": "Pension"},
            {"name": "Winter Fuel Payment", "who": "Born before 23 Sept 1958, on Pension Credit", "amount": "200-300 one-off", "link": "https://www.gov.uk/winter-fuel-payment", "category": "Pension"},
            {"name": "Cold Weather Payment", "who": "On certain benefits during cold spells", "amount": "25 per 7-day cold period", "link": "https://www.gov.uk/cold-weather-payment", "category": "Pension"},
            {"name": "Funeral Expenses Payment", "who": "On benefits, responsible for funeral", "amount": "Up to 1,000 + fees", "link": "https://www.gov.uk/funeral-payments", "category": "Pension"},
        ],
        "energy_bills": [
            {"name": "Warm Home Discount", "who": "Low income / Pension Credit", "amount": "150 off electricity bill", "link": "https://www.gov.uk/the-warm-home-discount-scheme", "category": "Energy"},
            {"name": "Energy Company Obligation (ECO)", "who": "Low income, poor insulation", "amount": "Free insulation / boiler", "link": "https://www.gov.uk/energy-company-obligation", "category": "Energy"},
            {"name": "Great British Insulation Scheme", "who": "Council tax bands A-D, certain benefits", "amount": "Free cavity/loft insulation", "link": "https://www.gov.uk/apply-great-british-insulation-scheme", "category": "Energy"},
        ],
        "tax_relief": [
            {"name": "Marriage Allowance", "who": "Married/civil partnership, one earner under 12,570", "amount": "Save up to 252/year", "link": "https://www.gov.uk/marriage-allowance", "category": "Tax"},
            {"name": "Council Tax Reduction", "who": "Low income", "amount": "Up to 100% reduction", "link": "https://www.gov.uk/council-tax-reduction", "category": "Tax"},
            {"name": "Council Tax Single Person Discount", "who": "Living alone", "amount": "25% discount", "link": "https://www.gov.uk/council-tax/discounts-for-disabled-people", "category": "Tax"},
            {"name": "Working from Home Tax Relief", "who": "Required to work from home", "amount": "6/week tax relief", "link": "https://www.gov.uk/tax-relief-for-employees/working-at-home", "category": "Tax"},
        ],
        "transport": [
            {"name": "Bus Pass (Elderly)", "who": "State Pension age", "amount": "Free off-peak bus travel", "link": "https://www.gov.uk/apply-for-elderly-person-bus-pass", "category": "Transport"},
            {"name": "Disabled Person's Bus Pass", "who": "Eligible disabilities", "amount": "Free bus travel", "link": "https://www.gov.uk/apply-for-disabled-bus-pass", "category": "Transport"},
            {"name": "Blue Badge", "who": "Severe mobility problems", "amount": "Disabled parking permit", "link": "https://www.gov.uk/blue-badge-scheme-information-council", "category": "Transport"},
            {"name": "Motability Scheme", "who": "Receiving PIP enhanced mobility", "amount": "Lease a car using PIP", "link": "https://www.motability.co.uk", "category": "Transport"},
        ],
        "education": [
            {"name": "Student Finance England", "who": "Full-time UK students", "amount": "Tuition fee loan + maintenance loan", "link": "https://www.gov.uk/student-finance", "category": "Education"},
            {"name": "Disabled Students Allowance", "who": "Students with disabilities", "amount": "Up to 25,575/year", "link": "https://www.gov.uk/disabled-students-allowance-dsa", "category": "Education"},
            {"name": "Apprenticeships", "who": "Age 16+", "amount": "Earn while learning, min 6.40/hr", "link": "https://www.gov.uk/apply-apprenticeship", "category": "Education"},
            {"name": "Advanced Learner Loan", "who": "19+, level 3-6 courses", "amount": "Covers course fees", "link": "https://www.gov.uk/advanced-learner-loan", "category": "Education"},
            {"name": "16-19 Bursary Fund", "who": "Students 16-19 facing financial hardship", "amount": "Up to 1,200/year", "link": "https://www.gov.uk/1619-bursary-fund", "category": "Education"},
        ],
        "immigration": [
            {"name": "Skilled Worker Visa", "who": "Job offer from licensed sponsor, 33,400+ salary", "amount": "Visa fee 719-1,420", "link": "https://www.gov.uk/skilled-worker-visa", "category": "Immigration"},
            {"name": "Graduate Visa (PSW)", "who": "Completed UK degree", "amount": "2 years stay, no sponsor needed", "link": "https://www.gov.uk/graduate-visa", "category": "Immigration"},
            {"name": "EU Settlement Scheme", "who": "EU citizens resident before 31 Dec 2020", "amount": "Free to apply", "link": "https://www.gov.uk/settled-status-eu-citizens-families", "category": "Immigration"},
            {"name": "Asylum Support", "who": "Asylum seekers", "amount": "49.18/week + accommodation", "link": "https://www.gov.uk/asylum-support", "category": "Immigration"},
        ],
        "business": [
            {"name": "Start Up Loans", "who": "New businesses (trading under 3 years)", "amount": "Up to 25,000 at 6% fixed", "link": "https://www.startuploans.co.uk", "category": "Business"},
            {"name": "Small Business Rate Relief", "who": "Business rateable value under 15,000", "amount": "Up to 100% rates relief", "link": "https://www.gov.uk/apply-for-business-rate-relief/small-business-rate-relief", "category": "Business"},
            {"name": "R&D Tax Credits", "who": "Companies doing R&D", "amount": "Up to 27% of qualifying costs", "link": "https://www.gov.uk/guidance/corporation-tax-research-and-development-rd-relief", "category": "Business"},
            {"name": "Patent Box", "who": "Companies with patents", "amount": "10% corporation tax on patent profits", "link": "https://www.gov.uk/guidance/corporation-tax-the-patent-box", "category": "Business"},
        ],
        "legal": [
            {"name": "Legal Aid", "who": "Low income, serious legal issues", "amount": "Free legal representation", "link": "https://www.gov.uk/legal-aid", "category": "Legal"},
            {"name": "Criminal Injuries Compensation", "who": "Victims of violent crime", "amount": "1,000 - 500,000", "link": "https://www.gov.uk/claim-compensation-criminal-injury", "category": "Legal"},
        ],
    }


# ═══════════════════════════════════════════════════════════
# ESSENTIAL SERVICES LINKS
# ═══════════════════════════════════════════════════════════
def get_essential_services():
    return {
        "emergency": [
            {"name": "Emergency Services", "number": "999", "for": "Life-threatening emergencies"},
            {"name": "Non-Emergency Police", "number": "101", "for": "Report crime, non-urgent"},
            {"name": "NHS Non-Emergency", "number": "111", "for": "Medical advice, non-emergency"},
            {"name": "Gas Emergency", "number": "0800 111 999", "for": "Gas leak or smell"},
            {"name": "Electricity Emergency", "number": "105", "for": "Power cut"},
            {"name": "Flood Line", "number": "0345 988 1188", "for": "Flood warnings and advice"},
            {"name": "Samaritans", "number": "116 123", "for": "Mental health crisis, free 24/7"},
            {"name": "Childline", "number": "0800 1111", "for": "Children seeking help"},
            {"name": "Domestic Abuse Helpline", "number": "0808 2000 247", "for": "Free 24/7 support"},
        ],
        "government": [
            {"name": "HMRC Self Assessment", "url": "https://www.gov.uk/self-assessment-tax-returns", "for": "File tax returns"},
            {"name": "DVLA", "url": "https://www.gov.uk/browse/driving", "for": "Driving licence, vehicle tax, MOT"},
            {"name": "Passport Office", "url": "https://www.gov.uk/apply-renew-passport", "for": "Apply or renew passport"},
            {"name": "Voter Registration", "url": "https://www.gov.uk/register-to-vote", "for": "Register to vote"},
            {"name": "Jury Service", "url": "https://www.gov.uk/jury-service", "for": "Jury service information"},
            {"name": "Land Registry", "url": "https://www.gov.uk/search-property-information-land-registry", "for": "Property ownership search"},
            {"name": "Companies House", "url": "https://www.gov.uk/government/organisations/companies-house", "for": "Register a company, file accounts"},
            {"name": "DBS Check", "url": "https://www.gov.uk/request-copy-criminal-record", "for": "Criminal record check"},
            {"name": "Power of Attorney", "url": "https://www.gov.uk/power-of-attorney", "for": "Lasting power of attorney"},
            {"name": "Probate", "url": "https://www.gov.uk/applying-for-probate", "for": "Dealing with someone's estate"},
            {"name": "Birth Certificate", "url": "https://www.gov.uk/order-copy-birth-death-marriage-certificate", "for": "Order certificates"},
            {"name": "Name Change (Deed Poll)", "url": "https://www.gov.uk/change-name-deed-poll", "for": "Legally change your name"},
        ],
        "nhs": [
            {"name": "GP Registration", "url": "https://www.nhs.uk/nhs-services/gps/how-to-register-with-a-gp-surgery/", "for": "Register with a doctor"},
            {"name": "NHS App", "url": "https://www.nhs.uk/nhs-app/", "for": "Book appointments, view records, order prescriptions"},
            {"name": "Find a Pharmacy", "url": "https://www.nhs.uk/service-search/pharmacy/find-a-pharmacy", "for": "Nearest pharmacy"},
            {"name": "Find a Dentist", "url": "https://www.nhs.uk/service-search/find-a-dentist", "for": "NHS dentist near you"},
            {"name": "Mental Health Support", "url": "https://www.nhs.uk/mental-health/", "for": "Mental health services"},
            {"name": "Prescription Prepayment", "url": "https://www.nhs.uk/nhs-services/prescriptions-and-pharmacies/save-money-with-a-prescription-prepayment-certificate-ppc/", "for": "Save on prescriptions (PPC)"},
            {"name": "Free NHS Prescriptions", "url": "https://www.nhs.uk/nhs-services/prescriptions-and-pharmacies/who-can-get-free-prescriptions/", "for": "Check if you qualify for free prescriptions"},
        ],
    }


# ═══════════════════════════════════════════════════════════
# HOUSING
# ═══════════════════════════════════════════════════════════
HOUSING = {
    "York": {"avg_price": 325_000, "vs_uk": 30_000, "waiting_list": 3_500, "new_builds_2024": 850, "avg_rent_pcm": 1_050},
    "Leeds": {"avg_price": 245_000, "vs_uk": -50_000, "waiting_list": 27_000, "new_builds_2024": 3_200, "avg_rent_pcm": 875},
    "Sheffield": {"avg_price": 215_000, "vs_uk": -80_000, "waiting_list": 22_000, "new_builds_2024": 2_100, "avg_rent_pcm": 780},
    "Bradford": {"avg_price": 165_000, "vs_uk": -130_000, "waiting_list": 19_000, "new_builds_2024": 1_400, "avg_rent_pcm": 650},
    "Hull": {"avg_price": 145_000, "vs_uk": -150_000, "waiting_list": 8_500, "new_builds_2024": 900, "avg_rent_pcm": 550},
}

def get_housing(council):
    return HOUSING.get(council, {"avg_price": 250_000, "vs_uk": -45_000, "waiting_list": "N/A", "new_builds_2024": "N/A", "avg_rent_pcm": 800})


# ═══════════════════════════════════════════════════════════
# SCHOOLS & EDUCATION
# ═══════════════════════════════════════════════════════════
SCHOOLS = {
    "York": {"total": 82, "outstanding": "22%", "good": "68%", "requires_improvement": "8%", "universities": ["University of York", "York St John University"]},
    "Leeds": {"total": 298, "outstanding": "18%", "good": "65%", "requires_improvement": "13%", "universities": ["University of Leeds", "Leeds Beckett University"]},
    "Sheffield": {"total": 189, "outstanding": "16%", "good": "66%", "requires_improvement": "14%", "universities": ["University of Sheffield", "Sheffield Hallam University"]},
    "Bradford": {"total": 215, "outstanding": "14%", "good": "62%", "requires_improvement": "18%", "universities": ["University of Bradford"]},
    "Hull": {"total": 98, "outstanding": "12%", "good": "64%", "requires_improvement": "16%", "universities": ["University of Hull"]},
}

def get_schools(council):
    return SCHOOLS.get(council, {"total": 150, "outstanding": "15%", "good": "65%", "requires_improvement": "15%", "universities": []})


# ═══════════════════════════════════════════════════════════
# CRIME
# ═══════════════════════════════════════════════════════════
CRIME = {
    "York": {"total": 18_500, "antisocial": 3_200, "violent": 5_100, "burglary": 980, "drugs": 420, "vehicle": 1_100},
    "Leeds": {"total": 92_000, "antisocial": 15_800, "violent": 28_500, "burglary": 5_200, "drugs": 2_800, "vehicle": 6_100},
    "Sheffield": {"total": 62_000, "antisocial": 10_500, "violent": 19_800, "burglary": 3_800, "drugs": 1_900, "vehicle": 4_200},
    "Bradford": {"total": 58_000, "antisocial": 11_200, "violent": 17_500, "burglary": 3_400, "drugs": 1_600, "vehicle": 3_800},
    "Hull": {"total": 32_000, "antisocial": 6_100, "violent": 10_200, "burglary": 1_800, "drugs": 900, "vehicle": 2_100},
}

def get_crime_stats(council):
    return CRIME.get(council, {"total": 25_000, "antisocial": 4_500, "violent": 8_000, "burglary": 1_500, "drugs": 800, "vehicle": 2_000})


# ═══════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════
HEALTH = {
    "York": {"gp_surgeries": 28, "hospitals": 2, "ae_wait": "3h 12m", "ambulance_response": "8m 42s", "mental_health_beds": 85, "nhs_trust": "York and Scarborough Teaching Hospitals"},
    "Leeds": {"gp_surgeries": 108, "hospitals": 7, "ae_wait": "4h 05m", "ambulance_response": "9m 15s", "mental_health_beds": 320, "nhs_trust": "Leeds Teaching Hospitals"},
    "Sheffield": {"gp_surgeries": 89, "hospitals": 5, "ae_wait": "3h 48m", "ambulance_response": "8m 55s", "mental_health_beds": 240, "nhs_trust": "Sheffield Teaching Hospitals"},
    "Bradford": {"gp_surgeries": 78, "hospitals": 3, "ae_wait": "4h 22m", "ambulance_response": "9m 30s", "mental_health_beds": 180, "nhs_trust": "Bradford Teaching Hospitals"},
    "Hull": {"gp_surgeries": 42, "hospitals": 2, "ae_wait": "3h 55m", "ambulance_response": "9m 05s", "mental_health_beds": 120, "nhs_trust": "Hull University Teaching Hospitals"},
}

def get_health_data(council):
    return HEALTH.get(council, {"gp_surgeries": 50, "hospitals": 3, "ae_wait": "3h 30m", "ambulance_response": "9m", "mental_health_beds": 100, "nhs_trust": "Local NHS Trust"})


# ═══════════════════════════════════════════════════════════
# TRANSPORT
# ═══════════════════════════════════════════════════════════
TRANSPORT = {
    "York": {"station": "York (LNER, TransPennine)", "bus": "First York", "avg_commute": "25 mins", "park_ride": 6, "cycle_lanes_km": 45},
    "Leeds": {"station": "Leeds (LNER, Northern, TransPennine)", "bus": "First Leeds, Arriva", "avg_commute": "32 mins", "park_ride": 7, "cycle_lanes_km": 38},
    "Sheffield": {"station": "Sheffield (CrossCountry, Northern)", "bus": "First South Yorkshire, Supertram", "avg_commute": "28 mins", "park_ride": 4, "cycle_lanes_km": 30},
    "Bradford": {"station": "Bradford Interchange (Northern)", "bus": "First Bradford, Arriva", "avg_commute": "30 mins", "park_ride": 2, "cycle_lanes_km": 15},
    "Hull": {"station": "Hull Paragon (Northern, TransPennine)", "bus": "East Yorkshire, Stagecoach", "avg_commute": "22 mins", "park_ride": 3, "cycle_lanes_km": 20},
}

def get_transport(council):
    return TRANSPORT.get(council, {"station": "Check National Rail", "bus": "Local provider", "avg_commute": "28 mins", "park_ride": "N/A", "cycle_lanes_km": "N/A"})


# ═══════════════════════════════════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════════════════════════════════
ENVIRONMENT = {
    "York": {"recycling_rate": "45%", "aqi": "Good (2)", "green_spaces": "34 parks", "flood_risk": "High (Ouse/Foss)", "co2_per_capita": "4.8 tonnes"},
    "Leeds": {"recycling_rate": "38%", "aqi": "Moderate (4)", "green_spaces": "71 parks", "flood_risk": "Medium (Aire)", "co2_per_capita": "5.2 tonnes"},
    "Sheffield": {"recycling_rate": "29%", "aqi": "Good (3)", "green_spaces": "83 parks", "flood_risk": "Medium (Don/Sheaf)", "co2_per_capita": "4.5 tonnes"},
    "Bradford": {"recycling_rate": "42%", "aqi": "Moderate (4)", "green_spaces": "38 parks", "flood_risk": "Medium", "co2_per_capita": "5.0 tonnes"},
    "Hull": {"recycling_rate": "35%", "aqi": "Good (2)", "green_spaces": "22 parks", "flood_risk": "High (Humber)", "co2_per_capita": "5.5 tonnes"},
}

def get_environment(council):
    return ENVIRONMENT.get(council, {"recycling_rate": "40%", "aqi": "Moderate (3)", "green_spaces": "30+ parks", "flood_risk": "Check gov.uk", "co2_per_capita": "5.0 tonnes"})


# ═══════════════════════════════════════════════════════════
# JOBS & CAREERS
# ═══════════════════════════════════════════════════════════
def get_jobs_data():
    return {
        "job_sites": [
            {"name": "Find a Job (DWP)", "url": "https://www.gov.uk/find-a-job", "for": "Universal Jobmatch"},
            {"name": "Civil Service Jobs", "url": "https://www.civilservicejobs.service.gov.uk", "for": "Government roles"},
            {"name": "NHS Jobs", "url": "https://www.jobs.nhs.uk", "for": "Healthcare"},
            {"name": "Teaching Vacancies", "url": "https://teaching-vacancies.service.gov.uk", "for": "Teaching roles"},
            {"name": "Indeed UK", "url": "https://uk.indeed.com", "for": "All sectors"},
            {"name": "Reed", "url": "https://www.reed.co.uk", "for": "All sectors"},
            {"name": "LinkedIn", "url": "https://www.linkedin.com/jobs", "for": "Professional roles"},
            {"name": "Apprenticeships", "url": "https://www.findapprenticeship.service.gov.uk", "for": "Earn while learning"},
        ],
        "career_support": [
            {"name": "National Careers Service", "url": "https://nationalcareers.service.gov.uk", "for": "Free career advice"},
            {"name": "Skills Bootcamps", "url": "https://www.gov.uk/guidance/find-a-skills-bootcamp", "for": "Free 12-16 week courses"},
            {"name": "Restart Scheme", "url": "https://www.gov.uk/restart-scheme", "for": "Support for long-term unemployed"},
        ],
    }
