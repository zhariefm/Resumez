import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from resume_parser import extract_resume_text
from tailor_engine import tailor_resume_and_letter, recommend_companies_for_student
from docx_generator import create_jakes_resume_docx, create_application_letter_docx
from pdf_generator import create_jakes_resume_pdf, create_application_letter_pdf

load_dotenv()

st.set_page_config(
    page_title="Resumez",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- APPLE DESIGN SYSTEM (MINIMALIST, CLEAN, NO JARGON) ---
st.markdown("""
<style>
    /* Apple Global Typography & Neutral Canvas */
    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.015em;
    }

    .block-container {
        max-width: 980px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Icon Font Protection */
    [data-testid="stIconMaterial"], 
    .material-symbols-rounded, 
    .material-symbols-outlined, 
    .material-icons,
    span[data-testid*="stIcon"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        display: inline-block !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }

    p, label, li, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #1d1d1f !important;
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* --- APPLE SEGMENTED CONTROL HEADER --- */
    .apple-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2.25rem;
        padding-bottom: 0.5rem;
    }

    .apple-brand {
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #1d1d1f !important;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .apple-nav-track {
        display: flex;
        align-items: center;
        background: #e5e5ea;
        padding: 3px;
        border-radius: 980px;
        gap: 2px;
    }

    .apple-nav-pill {
        padding: 0.35rem 1rem;
        border-radius: 980px;
        font-size: 0.82rem;
        font-weight: 500;
        color: #86868b;
        transition: all 0.2s ease;
    }

    .apple-nav-pill-active {
        background: #ffffff;
        color: #1d1d1f !important;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }

    .apple-nav-pill-done {
        color: #34c759 !important;
        font-weight: 600;
    }

    /* --- APPLE CLEAN SURFACES (CARDS) --- */
    .apple-card {
        background: #ffffff !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 18px !important;
        padding: 2.25rem 2.5rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 1.75rem !important;
        animation: appleFadeIn 0.25s ease-out;
    }

    @keyframes appleFadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .apple-title {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.03em !important;
        margin: 0 0 0.35rem 0 !important;
    }

    .apple-subtitle {
        font-size: 1rem !important;
        color: #86868b !important;
        margin: 0 0 1.75rem 0 !important;
        line-height: 1.45 !important;
    }

    /* --- APPLE INPUT FIELDS --- */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    .stTextInput>div>div,
    .stTextArea>div>div {
        background-color: #ffffff !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within,
    .stTextInput>div>div:focus-within,
    .stTextArea>div>div:focus-within {
        border-color: #0071e3 !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15) !important;
    }

    .stTextInput input, 
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        font-size: 0.94rem !important;
        border: none !important;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: 1.5px dashed #c7c7cc !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploaderDropzone"]:hover {
        background-color: #fbfbfd !important;
        border-color: #0071e3 !important;
    }

    [data-testid="stFileUploader"] button {
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 980px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 0.4rem 1.25rem !important;
    }

    /* --- APPLE BUTTONS --- */
    .stButton>button {
        border-radius: 980px !important;
        font-weight: 500 !important;
        font-size: 0.94rem !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button[kind="primary"] {
        background: #0071e3 !important;
        color: #ffffff !important;
        border: none !important;
    }

    .stButton>button[kind="primary"] * {
        color: #ffffff !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: #0077ed !important;
    }

    .stButton>button[kind="secondary"],
    .stButton>button:not([kind="primary"]) {
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
        border: 1px solid #d2d2d7 !important;
    }

    .stButton>button[kind="secondary"]:hover,
    .stButton>button:not([kind="primary"]):hover {
        background: #e8e8ed !important;
    }

    /* --- COMPANY CARDS --- */
    .apple-company-card {
        background: #ffffff;
        border: 1px solid #d2d2d7;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1.15rem;
        transition: all 0.2s ease;
    }

    .apple-company-card:hover {
        border-color: #0071e3;
        box-shadow: 0 4px 16px rgba(0, 113, 227, 0.08);
    }

    .apple-comp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .apple-comp-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1d1d1f;
    }

    .apple-link-btn {
        color: #0071e3 !important;
        font-size: 0.82rem;
        font-weight: 500;
        text-decoration: none !important;
        padding: 0.2rem 0.65rem;
        background: #f5f5f7;
        border-radius: 980px;
    }

    .apple-link-btn:hover {
        background: #e8e8ed;
    }

    .apple-score-pill {
        background: #f5f5f7;
        border: 1px solid #e5e5ea;
        color: #0071e3;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.25rem 0.65rem;
        border-radius: 980px;
    }

    /* --- METRIC CARDS --- */
    .apple-metric-card {
        background: #f5f5f7;
        border: 1px solid #e5e5ea;
        border-radius: 14px;
        padding: 1.15rem 1rem;
        text-align: center;
    }

    .apple-metric-val {
        font-size: 1.95rem;
        font-weight: 700;
        color: #1d1d1f;
        margin: 0.15rem 0;
    }

    .apple-metric-label {
        font-size: 0.76rem;
        color: #86868b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* --- JAKE'S RESUME PAPER (PURE ATS B&W) --- */
    .jakes-paper, .letter-paper {
        background: #ffffff !important;
        border: 1px solid #d2d2d7;
        padding: 2.75rem 3.25rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #000000 !important;
        line-height: 1.35;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .jakes-paper *, .letter-paper * {
        color: #000000 !important;
    }

    .jakes-name {
        text-align: center;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-bottom: 0.15rem;
    }

    .jakes-contact {
        text-align: center;
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }

    .jakes-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        border-bottom: 1px solid #000000;
        padding-bottom: 2px;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        letter-spacing: 0.03em;
    }

    .jakes-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-top: 0.25rem;
        margin-bottom: 0.1rem;
    }

    .jakes-bold { font-weight: 700; }
    .jakes-italic { font-style: italic; }

    .jakes-ul {
        margin: 0.2rem 0 0.5rem 1.25rem;
        padding: 0;
    }

    .jakes-ul li {
        font-size: 0.88rem;
        margin-bottom: 0.25rem;
    }

    /* Map Box */
    [data-testid="stDeckGlJsonChart"], [data-testid="stMap"] {
        border: 1px solid #d2d2d7 !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        border-bottom: 1px solid #d2d2d7 !important;
        padding-bottom: 4px !important;
    }

    div[data-baseweb="tab"] {
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: #86868b !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.85rem !important;
    }

    div[data-baseweb="tab"][aria-selected="true"] {
        color: #1d1d1f !important;
        font-weight: 600 !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .apple-card {
            padding: 1.35rem 1.15rem !important;
            border-radius: 16px !important;
        }
        .apple-title {
            font-size: 1.5rem !important;
        }
        .stButton>button {
            width: 100% !important;
            min-height: 44px !important;
        }
        .jakes-paper, .letter-paper {
            padding: 1.25rem 1rem !important;
        }
        .jakes-row {
            flex-direction: column !important;
            gap: 2px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- GLOBAL TECH HUBS DATABASE ---
TECH_COUNTRIES = {
    "United States": {
        "hubs": ["San Francisco Bay Area, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA", "Los Angeles, CA", "Remote (US)"],
        "coords": [37.7749, -122.4194],
        "zoom": 4,
        "city_coords": {
            "San Francisco Bay Area, CA": [37.7749, -122.4194],
            "New York, NY": [40.7128, -74.0060],
            "Seattle, WA": [47.6062, -122.3321],
            "Austin, TX": [30.2672, -97.7431],
            "Boston, MA": [42.3601, -71.0589],
            "Los Angeles, CA": [34.0522, -118.2437],
            "Remote (US)": [39.8283, -98.5795],
        }
    },
    "United Kingdom": {
        "hubs": ["London", "Cambridge", "Manchester", "Edinburgh", "Bristol", "Remote (UK)"],
        "coords": [51.5074, -0.1278],
        "zoom": 6,
        "city_coords": {
            "London": [51.5074, -0.1278],
            "Cambridge": [52.2053, 0.1218],
            "Manchester": [53.4808, -2.2426],
            "Edinburgh": [55.9533, -3.1883],
            "Bristol": [51.4545, -2.5879],
            "Remote (UK)": [54.5, -3.0],
        }
    },
    "Singapore": {
        "hubs": ["Downtown Core / Marina Bay", "One-North Tech Hub", "Jurong Innovation District", "Changi Business Park", "Remote (Singapore)"],
        "coords": [1.3521, 103.8198],
        "zoom": 11,
        "city_coords": {
            "Downtown Core / Marina Bay": [1.2879, 103.8519],
            "One-North Tech Hub": [1.2988, 103.7874],
            "Jurong Innovation District": [1.3404, 103.6967],
            "Changi Business Park": [1.3347, 103.9634],
            "Remote (Singapore)": [1.3521, 103.8198],
        }
    },
    "Canada": {
        "hubs": ["Toronto, ON", "Vancouver, BC", "Montreal, QC", "Waterloo / Kitchener, ON", "Ottawa, ON", "Remote (Canada)"],
        "coords": [43.6532, -79.3832],
        "zoom": 5,
        "city_coords": {
            "Toronto, ON": [43.6532, -79.3832],
            "Vancouver, BC": [49.2827, -123.1207],
            "Montreal, QC": [45.5017, -73.5673],
            "Waterloo / Kitchener, ON": [43.4643, -80.5204],
            "Ottawa, ON": [45.4215, -75.6972],
            "Remote (Canada)": [56.1304, -106.3468],
        }
    },
    "Germany": {
        "hubs": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Stuttgart", "Remote (Germany)"],
        "coords": [52.5200, 13.4050],
        "zoom": 6,
        "city_coords": {
            "Berlin": [52.5200, 13.4050],
            "Munich": [48.1351, 11.5820],
            "Frankfurt": [50.1109, 8.6821],
            "Hamburg": [53.5511, 9.9937],
            "Stuttgart": [48.7758, 9.1829],
            "Remote (Germany)": [51.1657, 10.4515],
        }
    },
    "Malaysia": {
        "hubs": ["Kuala Lumpur / Bangsar South", "Cyberjaya Tech Hub", "Penang / Bayan Lepas", "Petaling Jaya", "Remote (Malaysia)"],
        "coords": [3.1390, 101.6869],
        "zoom": 10,
        "city_coords": {
            "Kuala Lumpur / Bangsar South": [3.1118, 101.6669],
            "Cyberjaya Tech Hub": [2.9213, 101.6559],
            "Penang / Bayan Lepas": [5.2974, 100.2831],
            "Petaling Jaya": [3.1073, 101.6067],
            "Remote (Malaysia)": [4.2105, 101.9758],
        }
    },
    "Australia": {
        "hubs": ["Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", "Remote (Australia)"],
        "coords": [-33.8688, 151.2093],
        "zoom": 5,
        "city_coords": {
            "Sydney, NSW": [-33.8688, 151.2093],
            "Melbourne, VIC": [-37.8136, 144.9631],
            "Brisbane, QLD": [-27.4698, 153.0251],
            "Perth, WA": [-31.9505, 115.8605],
            "Remote (Australia)": [-25.2744, 133.7751],
        }
    },
    "Netherlands": {
        "hubs": ["Amsterdam", "Rotterdam", "Utrecht", "Eindhoven Tech Hub", "Remote (Netherlands)"],
        "coords": [52.3676, 4.9041],
        "zoom": 7,
        "city_coords": {
            "Amsterdam": [52.3676, 4.9041],
            "Rotterdam": [51.9244, 4.4777],
            "Utrecht": [52.0907, 5.1214],
            "Eindhoven Tech Hub": [51.4416, 5.4697],
            "Remote (Netherlands)": [52.1326, 5.2913],
        }
    },
    "India": {
        "hubs": ["Bengaluru, Karnataka", "Hyderabad, Telangana", "Pune, Maharashtra", "Gurgaon / Delhi NCR", "Mumbai", "Remote (India)"],
        "coords": [12.9716, 77.5946],
        "zoom": 5,
        "city_coords": {
            "Bengaluru, Karnataka": [12.9716, 77.5946],
            "Hyderabad, Telangana": [17.3850, 78.4867],
            "Pune, Maharashtra": [18.5204, 73.8567],
            "Gurgaon / Delhi NCR": [28.4595, 77.0266],
            "Mumbai": [19.0760, 72.8777],
            "Remote (India)": [20.5937, 78.9629],
        }
    },
    "Japan": {
        "hubs": ["Tokyo", "Osaka", "Kyoto", "Fukuoka Tech Hub", "Remote (Japan)"],
        "coords": [35.6762, 139.6503],
        "zoom": 8,
        "city_coords": {
            "Tokyo": [35.6580, 139.7016],
            "Osaka": [34.6937, 135.5023],
            "Kyoto": [35.0116, 135.7681],
            "Fukuoka Tech Hub": [33.5904, 130.4017],
            "Remote (Japan)": [36.2048, 138.2529],
        }
    },
    "Global Remote": {
        "hubs": ["Worldwide Remote", "North America Remote", "Europe / UK Remote", "APAC Remote"],
        "coords": [20.0, 0.0],
        "zoom": 2,
        "city_coords": {
            "Worldwide Remote": [20.0, 0.0],
            "North America Remote": [39.8283, -98.5795],
            "Europe / UK Remote": [54.5260, 15.2551],
            "APAC Remote": [1.3521, 103.8198],
        }
    },
    "Custom Location": {
        "hubs": ["Custom City"],
        "coords": [37.7749, -122.4194],
        "zoom": 3,
        "city_coords": {
            "Custom City": [37.7749, -122.4194]
        }
    }
}

# --- STATE INITIALIZATION ---
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "student_text" not in st.session_state:
    st.session_state.student_text = ""
if "target_country" not in st.session_state:
    st.session_state.target_country = "United States"
if "target_hub" not in st.session_state:
    st.session_state.target_hub = "San Francisco Bay Area, CA"
if "target_location" not in st.session_state:
    st.session_state.target_location = "San Francisco Bay Area, CA, United States"
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "role_title" not in st.session_state:
    st.session_state.role_title = ""
if "company_website" not in st.session_state:
    st.session_state.company_website = ""
if "recommended_companies" not in st.session_state:
    st.session_state.recommended_companies = []
if "tailored_data" not in st.session_state:
    st.session_state.tailored_data = None

# --- TOP MINIMAL HEADER ---
step = st.session_state.current_step
s1_class = "apple-nav-pill apple-nav-pill-done" if step > 1 else ("apple-nav-pill apple-nav-pill-active" if step == 1 else "apple-nav-pill")
s2_class = "apple-nav-pill apple-nav-pill-done" if step > 2 else ("apple-nav-pill apple-nav-pill-active" if step == 2 else "apple-nav-pill")
s3_class = "apple-nav-pill apple-nav-pill-active" if step == 3 else "apple-nav-pill"

st.markdown(f"""
<div class="apple-header">
    <div class="apple-brand">Resumez</div>
    <div class="apple-nav-track">
        <div class="{s1_class}">1. Profile</div>
        <div class="{s2_class}">2. Company</div>
        <div class="{s3_class}">3. Tailor</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# STEP 1: PROFILE & LOCATION
# ==============================================================================
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="apple-card">
        <h2 class="apple-title">Profile & Location</h2>
        <p class="apple-subtitle">Upload your existing resume and pick your target hiring location.</p>
    """, unsafe_allow_html=True)

    # Resume Upload
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, TXT):",
        type=["pdf", "docx", "txt", "md"]
    )
    if uploaded_file is not None:
        try:
            extracted = extract_resume_text(uploaded_file)
            st.session_state.student_text = extracted
            st.toast("Resume parsed successfully.", icon="✓")
        except Exception as e:
            st.error(str(e))

    student_text_input = st.text_area(
        "Resume Details & Background:",
        value=st.session_state.student_text,
        height=220,
        placeholder="Or paste your experience, projects, skills, and coursework here..."
    )
    st.session_state.student_text = student_text_input

    # Location Section
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("**Target Location**")
    loc_col1, loc_col2 = st.columns([1, 1], gap="medium")
    
    with loc_col1:
        country_keys = list(TECH_COUNTRIES.keys())
        country_idx = country_keys.index(st.session_state.target_country) if st.session_state.target_country in country_keys else 0

        selected_country = st.selectbox(
            "Country",
            options=country_keys,
            index=country_idx,
            label_visibility="collapsed"
        )
        st.session_state.target_country = selected_country

        country_data = TECH_COUNTRIES[selected_country]
        hub_options = country_data["hubs"]
        hub_idx = hub_options.index(st.session_state.target_hub) if st.session_state.target_hub in hub_options else 0

        selected_hub = st.selectbox(
            "City / Region",
            options=hub_options,
            index=hub_idx
        )
        st.session_state.target_hub = selected_hub

        custom_loc = ""
        if "Custom" in selected_country or "Custom" in selected_hub:
            custom_loc = st.text_input("Custom City", placeholder="e.g. Zurich, Switzerland")

        if custom_loc.strip():
            final_location_str = custom_loc.strip()
        elif "Remote" in selected_country or "Worldwide" in selected_hub:
            final_location_str = f"{selected_hub}"
        else:
            final_location_str = f"{selected_hub}, {selected_country}"

        st.session_state.target_location = final_location_str
        st.caption(f"Active location: **{final_location_str}**")

    with loc_col2:
        coords = country_data.get("city_coords", {}).get(selected_hub, country_data.get("coords", [37.7749, -122.4194]))
        zoom_level = country_data.get("zoom", 5)

        map_df = pd.DataFrame([{"lat": coords[0], "lon": coords[1]}])
        st.map(map_df, zoom=zoom_level, height=195)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Next Action
    btn_col1, btn_col2, btn_col3 = st.columns([1.5, 2, 1.5])
    with btn_col2:
        if st.button("Continue to Company Selection →", use_container_width=True, type="primary"):
            if not st.session_state.student_text.strip():
                st.warning("Please upload or enter your resume details first.")
            else:
                if not st.session_state.recommended_companies:
                    with st.spinner("Finding matching companies..."):
                        try:
                            recs = recommend_companies_for_student(
                                resume_text=st.session_state.student_text,
                                target_location=st.session_state.target_location
                            )
                            st.session_state.recommended_companies = recs
                        except Exception as e:
                            st.error(f"Error: {e}")
                st.session_state.current_step = 2
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# STEP 2: COMPANY SELECTION
# ==============================================================================
elif st.session_state.current_step == 2:
    st.markdown("""
    <div class="apple-card">
        <h2 class="apple-title">Target Company</h2>
        <p class="apple-subtitle">Select an employer matching your profile or enter a custom job description.</p>
    """, unsafe_allow_html=True)

    if st.button("← Back to Profile", type="secondary"):
        st.session_state.current_step = 1
        st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    tab_recommended, tab_custom = st.tabs(["Recommended Employers", "Custom Role"])

    with tab_recommended:
        if not st.session_state.recommended_companies:
            st.info("No recommendations found yet.")
            if st.button("Search Companies", type="primary"):
                with st.spinner("Searching..."):
                    try:
                        recs = recommend_companies_for_student(
                            resume_text=st.session_state.student_text,
                            target_location=st.session_state.target_location
                        )
                        st.session_state.recommended_companies = recs
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            for idx, rec in enumerate(st.session_state.recommended_companies):
                c_name = rec.get("company_name", "Company")
                website = rec.get("website_url", "https://google.com")
                target_loc = rec.get("target_locations", st.session_state.target_location)
                r_title = rec.get("role_title", "Software Engineer")
                overview = rec.get("company_overview", "")
                fit = rec.get("fit_score", 90)

                with st.container():
                    st.markdown(f"""
                    <div class="apple-company-card">
                        <div class="apple-comp-header">
                            <div>
                                <span class="apple-comp-name">{c_name}</span>
                                <a href="{website}" target="_blank" class="apple-link-btn" style="margin-left: 0.5rem;">Website ↗</a>
                            </div>
                            <span class="apple-score-pill">{fit}% Match</span>
                        </div>
                        <div style="font-weight: 600; color: #1d1d1f; margin-bottom: 0.2rem;">{r_title} &nbsp;•&nbsp; <span style="color: #86868b; font-weight: normal;">{target_loc}</span></div>
                        <div style="font-size: 0.9rem; color: #515154; margin-bottom: 0.5rem;">{overview}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"Tailor for {c_name} →", key=f"btn_choose_{idx}", use_container_width=True, type="primary"):
                        st.session_state.company_name = c_name
                        st.session_state.role_title = r_title
                        st.session_state.company_website = website
                        st.session_state.job_description = rec.get("job_description", "")

                        with st.spinner(f"Tailoring resume for {c_name}..."):
                            try:
                                res = tailor_resume_and_letter(
                                    resume_text=st.session_state.student_text,
                                    job_description=st.session_state.job_description,
                                    company_name=c_name,
                                    role_title=r_title,
                                    location=target_loc
                                )
                                st.session_state.tailored_data = res
                                st.session_state.current_step = 3
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    with tab_custom:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.company_name = st.text_input("Company Name", value=st.session_state.company_name, placeholder="e.g. Apple, Stripe")
        with c2:
            st.session_state.role_title = st.text_input("Role Title", value=st.session_state.role_title, placeholder="e.g. Software Engineer")

        st.session_state.company_website = st.text_input("Website URL", value=st.session_state.company_website, placeholder="e.g. https://apple.com")
        st.session_state.job_description = st.text_area(
            "Job Description",
            value=st.session_state.job_description,
            height=180,
            placeholder="Paste the role requirements and qualifications here..."
        )

        if st.button("Tailor Resume →", use_container_width=True, type="primary"):
            if not st.session_state.student_text.strip():
                st.warning("Please provide your resume details in Step 1.")
            elif not st.session_state.job_description.strip():
                st.warning("Please paste the job description.")
            else:
                with st.spinner("Tailoring documents..."):
                    try:
                        res = tailor_resume_and_letter(
                            resume_text=st.session_state.student_text,
                            job_description=st.session_state.job_description,
                            company_name=st.session_state.company_name,
                            role_title=st.session_state.role_title,
                            location=st.session_state.target_location
                        )
                        st.session_state.tailored_data = res
                        st.session_state.current_step = 3
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# STEP 3: REVIEW & EXPORT
# ==============================================================================
elif st.session_state.current_step == 3:
    data = st.session_state.tailored_data
    if not data:
        st.warning("No tailored data available.")
        if st.button("Return to Step 2"):
            st.session_state.current_step = 2
            st.rerun()
    else:
        assessment = data.get("ats_assessment", {})
        score = assessment.get("match_score", 92)
        breakdown = assessment.get("breakdown", {})
        s_score = breakdown.get("skills_match_score", 95)
        i_score = breakdown.get("impact_metric_score", 90)
        f_score = breakdown.get("format_compliance_score", 98)
        b_score = breakdown.get("brevity_score", 92)

        target_comp = assessment.get("target_company") or st.session_state.company_name or "Company"
        target_r = assessment.get("target_role") or st.session_state.role_title or "Role"
        rep_loc = assessment.get("location") or st.session_state.target_location
        website = st.session_state.company_website or ""

        st.markdown(f"""
        <div class="apple-card">
            <h2 class="apple-title">{target_comp} Application</h2>
            <p class="apple-subtitle">{target_r} &nbsp;•&nbsp; {rep_loc}</p>
        """, unsafe_allow_html=True)

        # Nav Actions
        b1, b2, b3 = st.columns([1.5, 3, 1.5])
        with b1:
            if st.button("← Change Company", type="secondary"):
                st.session_state.current_step = 2
                st.rerun()
        with b3:
            if st.button("Start Over", type="secondary"):
                st.session_state.current_step = 1
                st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Metrics Row
        m0, m1, m2, m3, m4 = st.columns(5)
        with m0:
            st.markdown(f"""
            <div class="apple-metric-card" style="background: #ffffff; border: 1.5px solid #0071e3;">
                <div class="apple-metric-label" style="color: #0071e3;">Match Score</div>
                <div class="apple-metric-val" style="color: #0071e3;">{score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m1:
            st.markdown(f"""
            <div class="apple-metric-card">
                <div class="apple-metric-label">Skills</div>
                <div class="apple-metric-val">{s_score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="apple-metric-card">
                <div class="apple-metric-label">Impact</div>
                <div class="apple-metric-val">{i_score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="apple-metric-card">
                <div class="apple-metric-label">Format</div>
                <div class="apple-metric-val">{f_score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="apple-metric-card">
                <div class="apple-metric-label">Length</div>
                <div class="apple-metric-val">{b_score}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # Downloads
        dl_col1, dl_col2 = st.columns(2, gap="medium")
        student_clean = data.get("personal_info", {}).get("name", "Candidate").replace(" ", "_")
        comp_clean = target_comp.replace(" ", "_")

        resume_docx_buf = create_jakes_resume_docx(data)
        resume_pdf_buf = create_jakes_resume_pdf(data)
        letter_docx_buf = create_application_letter_docx(data)
        letter_pdf_buf = create_application_letter_pdf(data)

        with dl_col1:
            st.markdown("**Resume (Jake's Clean ATS Format)**")
            rc1, rc2 = st.columns(2)
            with rc1:
                st.download_button(
                    "Download DOCX",
                    data=resume_docx_buf,
                    file_name=f"{student_clean}_{comp_clean}_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            with rc2:
                st.download_button(
                    "Download PDF",
                    data=resume_pdf_buf,
                    file_name=f"{student_clean}_{comp_clean}_Resume.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )

        with dl_col2:
            st.markdown("**Cover Letter**")
            lc1, lc2 = st.columns(2)
            with lc1:
                st.download_button(
                    "Download DOCX",
                    data=letter_docx_buf,
                    file_name=f"{student_clean}_{comp_clean}_Letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            with lc2:
                st.download_button(
                    "Download PDF",
                    data=letter_pdf_buf,
                    file_name=f"{student_clean}_{comp_clean}_Letter.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )

        # Tabs
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        tab_res, tab_let, tab_diff, tab_q, tab_li = st.tabs([
            "Resume Preview",
            "Cover Letter",
            "Bullet Changes",
            "Interview Prep",
            "LinkedIn"
        ])

        with tab_res:
            p_info = data.get("personal_info", {})
            contact_line = "  |  ".join([p for p in [p_info.get("phone"), p_info.get("email"), p_info.get("linkedin"), p_info.get("github"), p_info.get("portfolio")] if p])

            st.markdown('<div class="jakes-paper">', unsafe_allow_html=True)
            st.markdown(f'<div class="jakes-name">{p_info.get("name", "Candidate")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="jakes-contact">{contact_line}</div>', unsafe_allow_html=True)

            edu_list = data.get("education", [])
            if edu_list:
                st.markdown('<div class="jakes-section-title">Education</div>', unsafe_allow_html=True)
                for edu in edu_list:
                    inst = edu.get("institution", "")
                    loc = edu.get("location", "")
                    deg = edu.get("degree", "")
                    dates = edu.get("dates", "")
                    gpa = edu.get("gpa", "")
                    deg_str = deg + (f" (GPA: {gpa})" if gpa else "")

                    st.markdown(f'''
                    <div class="jakes-row">
                        <span class="jakes-bold">{inst}</span>
                        <span>{loc}</span>
                    </div>
                    <div class="jakes-row">
                        <span class="jakes-italic">{deg_str}</span>
                        <span class="jakes-italic">{dates}</span>
                    </div>
                    ''', unsafe_allow_html=True)

            exp_list = data.get("experience", [])
            if exp_list:
                st.markdown('<div class="jakes-section-title">Experience</div>', unsafe_allow_html=True)
                for exp in exp_list:
                    role = exp.get("role", "")
                    comp = exp.get("company", "")
                    loc = exp.get("location", "")
                    dates = exp.get("dates", "")

                    st.markdown(f'''
                    <div class="jakes-row">
                        <span class="jakes-bold">{role}</span>
                        <span>{dates}</span>
                    </div>
                    <div class="jakes-row">
                        <span class="jakes-italic">{comp}</span>
                        <span class="jakes-italic">{loc}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    bullets_html = "".join([f"<li>{b}</li>" for b in exp.get("bullets", [])])
                    st.markdown(f'<ul class="jakes-ul">{bullets_html}</ul>', unsafe_allow_html=True)

            proj_list = data.get("projects", [])
            if proj_list:
                st.markdown('<div class="jakes-section-title">Projects</div>', unsafe_allow_html=True)
                for proj in proj_list:
                    name = proj.get("name", "")
                    tools = proj.get("tools", "")
                    dates = proj.get("dates", "")
                    tools_str = f" | {tools}" if tools else ""

                    st.markdown(f'''
                    <div class="jakes-row">
                        <span><span class="jakes-bold">{name}</span><span class="jakes-italic">{tools_str}</span></span>
                        <span class="jakes-italic">{dates}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    bullets_html = "".join([f"<li>{b}</li>" for b in proj.get("bullets", [])])
                    st.markdown(f'<ul class="jakes-ul">{bullets_html}</ul>', unsafe_allow_html=True)

            skills_dict = data.get("technical_skills", {})
            if skills_dict:
                st.markdown('<div class="jakes-section-title">Technical Skills</div>', unsafe_allow_html=True)
                for cat, items in skills_dict.items():
                    items_str = ", ".join(items) if isinstance(items, list) else str(items)
                    cat_clean = cat.replace("_", " ").title()
                    st.markdown(f'<div style="font-size: 0.88rem; margin-bottom: 0.2rem;"><b>{cat_clean}:</b> {items_str}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab_let:
            let_data = data.get("application_letter", {})
            st.markdown('<div class="letter-paper">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 0.8rem;">{let_data.get("date", "Current Date")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1rem;"><b>To:</b> Hiring Team, {target_comp}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1rem;">{let_data.get("greeting", "Dear Hiring Team,")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1rem;">{let_data.get("opening_hook", "")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1rem;">{let_data.get("why_company", "")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1rem;">{let_data.get("student_value_add", "")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 1.5rem;">{let_data.get("closing_and_call_to_action", "")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.95rem;">{let_data.get("sign_off", "Sincerely,")}<br><b>{p_info.get("name", "Candidate")}</b></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_diff:
            transforms = data.get("bullet_transformations", [])
            if not transforms:
                st.info("No bullet edits recorded.")
            else:
                for tf in transforms:
                    st.markdown(f"""
                    <div style="background: #f5f5f7; border: 1px solid #e5e5ea; border-radius: 12px; padding: 1rem; margin-bottom: 0.85rem;">
                        <div style="font-weight: 600; color: #1d1d1f; font-size: 0.9rem; margin-bottom: 0.4rem;">
                            {tf.get('context', 'Experience')}
                        </div>
                        <div style="color: #ff3b30; font-size: 0.88rem; margin-bottom: 0.35rem;">
                            <b>Before:</b> {tf.get('original_bullet', '')}
                        </div>
                        <div style="color: #34c759; font-size: 0.88rem; margin-bottom: 0.35rem;">
                            <b>After:</b> {tf.get('elevated_bullet', '')}
                        </div>
                        <div style="color: #86868b; font-size: 0.8rem;">
                            <b>Change:</b> {tf.get('impact_enhancement', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab_q:
            interview_data = data.get("interview_prep", {})
            tech_q = interview_data.get("technical_questions", [])
            behav_q = interview_data.get("behavioral_questions", [])

            st.markdown("**Technical Scenarios**")
            for t in tech_q:
                st.markdown(f"""
                <div style="background: #f5f5f7; border-left: 3px solid #0071e3; border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.65rem;">
                    <div style="font-weight: 600; color: #1d1d1f; font-size: 0.92rem;">{t.get('question', '')}</div>
                    <div style="color: #86868b; font-size: 0.84rem; margin-top: 0.3rem;"><b>Strategy:</b> {t.get('answer_strategy', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("**Behavioral Scenarios**")
            for b in behav_q:
                st.markdown(f"""
                <div style="background: #f5f5f7; border-left: 3px solid #34c759; border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.65rem;">
                    <div style="font-weight: 600; color: #1d1d1f; font-size: 0.92rem;">{b.get('question', '')}</div>
                    <div style="color: #86868b; font-size: 0.84rem; margin-top: 0.3rem;"><b>Strategy:</b> {b.get('answer_strategy', '')}</div>
                </div>
                """, unsafe_allow_html=True)

        with tab_li:
            li_suite = data.get("linkedin_suite", {})
            st.text_input("LinkedIn Headline", value=li_suite.get("headline", ""))
            st.text_area("LinkedIn About", value=li_suite.get("about_summary", ""), height=100)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("**Matched Keywords**")
            matched_kw = assessment.get("key_matched_keywords", [])
            if matched_kw:
                st.write(", ".join(matched_kw))

        st.markdown("</div>", unsafe_allow_html=True)
