import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from resume_parser import extract_resume_text
from tailor_engine import tailor_resume_and_letter, recommend_companies_for_student
from docx_generator import create_jakes_resume_docx, create_application_letter_docx
from pdf_generator import create_jakes_resume_pdf, create_application_letter_pdf

# Load environment variables silently
load_dotenv()

st.set_page_config(
    page_title="Resumez — Enterprise Career & Resume Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- EXACT PULSEAI DRIBBBLE THEME (ALABASTER CANVAS, PEACH GLOW, ORANGE BORDER CARD, SEGOE UI) ---
st.markdown("""
<style>
    /* Warm Alabaster Canvas with Subtle Vertical Peach/Apricot Side Glows */
    html, body, [class*="css"], .stApp {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        background-color: #faf7f2 !important;
        background-image: 
            radial-gradient(at 0% 45%, rgba(253, 186, 116, 0.45) 0px, transparent 38%),
            radial-gradient(at 100% 45%, rgba(253, 186, 116, 0.45) 0px, transparent 38%),
            radial-gradient(at 50% 0%, rgba(255, 237, 213, 0.55) 0px, transparent 50%),
            linear-gradient(180deg, #faf7f2 0%, #fffdfa 40%, #faf6f0 100%) !important;
        background-attachment: fixed !important;
        color: #09090b !important;
        letter-spacing: -0.015em;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 4rem !important;
    }

    /* Streamlit & Material Icon Protection (Fixes 'uploadUpload' duplicate text bug) */
    [data-testid="stIconMaterial"], 
    .material-symbols-rounded, 
    .material-symbols-outlined, 
    .material-icons,
    [class*="material-symbols"], 
    [class*="material-icons"],
    span[data-testid*="stIcon"],
    .stIconMaterial,
    [data-testid="stFileUploader"] button span:first-child {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }

    /* Clean Dark Charcoal Typography */
    p, label, li, h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown span {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        color: #09090b !important;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- TOP NAVBAR (PULSEAI DRIBBBLE REPLICA) --- */
    .pulse-top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0 1.5rem 0;
        margin-bottom: 0.5rem;
    }

    .pulse-nav-brand {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .pulse-nav-logo {
        width: 34px;
        height: 34px;
        background: #f97316;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35);
    }

    .pulse-nav-brand-title {
        font-size: 1.18rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: #09090b !important;
        text-transform: uppercase;
    }

    .pulse-nav-capsule {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(255, 255, 255, 0.9);
        padding: 0.35rem 0.5rem;
        border-radius: 9999px;
        border: 1px solid rgba(228, 228, 231, 0.8);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    }

    .pulse-step-pill {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        color: #71717a !important;
        background: transparent;
        transition: all 0.2s ease;
    }

    .pulse-step-pill-active {
        background: #ffffff !important;
        color: #09090b !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .pulse-step-pill-done {
        color: #16a34a !important;
        font-weight: 600;
    }

    .pulse-nav-action-pill {
        background: transparent;
        border: 1.5px solid #e4e4e7;
        color: #09090b !important;
        padding: 0.4rem 1.15rem;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* --- HERO HEADER (CENTERED, JUST LIKE "Control what your AI actually does.") --- */
    .pulse-hero-box {
        text-align: center;
        max-width: 820px;
        margin: 1rem auto 2.5rem auto;
    }

    .pulse-hero-title {
        font-size: 3.25rem !important;
        font-weight: 800 !important;
        color: #09090b !important;
        line-height: 1.12 !important;
        letter-spacing: -0.035em !important;
        margin-bottom: 0.85rem !important;
    }

    .pulse-hero-subtitle {
        font-size: 1.08rem !important;
        color: #52525b !important;
        line-height: 1.55 !important;
        max-width: 620px !important;
        margin: 0 auto !important;
    }

    /* --- THE PULSEAI DASHBOARD CONTAINER (THE WARM ORANGE BORDER CARD) --- */
    .pulse-dashboard-card {
        background: #ffffff !important;
        border: 2.5px solid #fdba74 !important;
        border-radius: 32px !important;
        padding: 2.5rem 3rem !important;
        box-shadow: 0 35px 80px -15px rgba(249, 115, 22, 0.12), 0 10px 30px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 2.5rem !important;
        animation: fadeInStep 0.35s ease-out;
    }

    @keyframes fadeInStep {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Inner Top Bar matching PULSEAI card */
    .pulse-inner-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.25rem;
        margin-bottom: 1.75rem;
        border-bottom: 1px solid #f4f4f5;
        flex-wrap: wrap;
        gap: 0.85rem;
    }

    .pulse-inner-tab-active {
        background: #f4f4f5;
        color: #09090b;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
    }

    .pulse-inner-tab {
        color: #71717a;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 0.3rem 0.6rem;
    }

    .pulse-search-fake {
        background: #fbfbfb;
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        padding: 0.3rem 0.85rem;
        font-size: 0.8rem;
        color: #a1a1aa;
    }

    .pulse-icon-btn {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        border: 1px solid #e4e4e7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        background: #ffffff;
    }

    /* Section Title Row (Analytics Overview Style) */
    .pulse-section-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 1.75rem;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .pulse-section-title {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #09090b !important;
        letter-spacing: -0.025em !important;
        margin: 0 0 0.3rem 0 !important;
        line-height: 1.2 !important;
    }

    .pulse-section-subtitle {
        font-size: 0.96rem !important;
        color: #71717a !important;
        margin: 0 !important;
    }

    .pulse-header-badge {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #ea580c;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
    }

    .pulse-date-pill {
        background: #ffffff;
        border: 1.5px solid #e4e4e7;
        color: #09090b;
        font-size: 0.84rem;
        font-weight: 600;
        padding: 0.4rem 1rem;
        border-radius: 8px;
    }

    /* --- PITCH BLACK PILL BUTTONS (MATCHING "Start free trial" & "Export Report") --- */
    .stButton>button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.65rem !important;
        transition: all 0.25s ease !important;
    }

    .stButton>button[kind="primary"] {
        background: #09090b !important;
        color: #ffffff !important;
        border: 1px solid #09090b !important;
        box-shadow: 0 10px 25px -4px rgba(0, 0, 0, 0.28) !important;
    }

    .stButton>button[kind="primary"] * {
        color: #ffffff !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: #27272a !important;
        border-color: #27272a !important;
        box-shadow: 0 14px 30px -4px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-1px);
    }

    .stButton>button[kind="secondary"],
    .stButton>button:not([kind="primary"]) {
        background: #ffffff !important;
        color: #09090b !important;
        border: 1.5px solid #e4e4e7 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    .stButton>button[kind="secondary"]:hover,
    .stButton>button:not([kind="primary"]):hover {
        background: #f4f4f5 !important;
        border-color: #d4d4d8 !important;
        color: #09090b !important;
        transform: translateY(-1px);
    }

    /* --- CRISP WHITE & PEACH-ACCENTED INPUT BOXES (ZERO BLACK BOXES) --- */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    .stTextInput>div>div,
    .stTextArea>div>div {
        background-color: #ffffff !important;
        border: 1.5px solid #fed7aa !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.04) !important;
        transition: all 0.25s ease !important;
    }

    div[data-baseweb="input"]:hover,
    div[data-baseweb="base-input"]:hover,
    div[data-baseweb="textarea"]:hover,
    .stTextInput>div>div:hover,
    .stTextArea>div>div:hover {
        border-color: #fb923c !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.1) !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        border-color: #f97316 !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2) !important;
    }

    .stTextInput input, 
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #09090b !important;
        font-size: 0.94rem !important;
        border: none !important;
        border-radius: 12px !important;
    }

    .stTextInput input::placeholder, 
    .stTextArea textarea::placeholder {
        color: #a1a1aa !important;
    }

    /* Clean File Uploader Dropzone */
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }

    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #fed7aa !important;
        border-radius: 20px !important;
        padding: 1.6rem !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploaderDropzone"]:hover {
        background-color: #fff7ed !important;
        border-color: #f97316 !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #09090b !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 0.45rem 1.35rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
    }

    [data-testid="stFileUploader"] button * {
        color: #ffffff !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: #27272a !important;
    }

    /* --- STEP 2: COMPANY RECOMMENDATION CARDS --- */
    .company-card-step2 {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.35rem;
        box-shadow: 0 6px 20px -3px rgba(249, 115, 22, 0.08);
        border-left: 6px solid #f97316;
        transition: all 0.3s ease;
    }

    .company-card-step2:hover {
        background: #fffdfa;
        border-color: #f97316;
        box-shadow: 0 14px 35px -5px rgba(249, 115, 22, 0.18);
        transform: translateY(-2px);
    }

    .comp-header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }

    .comp-title-group {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        flex-wrap: wrap;
    }

    .comp-name-text {
        font-size: 1.4rem;
        font-weight: 800;
        color: #09090b !important;
        margin: 0;
    }

    .website-pill-btn {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #ea580c !important;
        padding: 0.3rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        transition: all 0.2s ease;
    }

    .website-pill-btn:hover {
        background: #f97316 !important;
        color: #ffffff !important;
        border-color: #f97316 !important;
    }

    .fit-score-badge {
        background: #fff7ed;
        color: #c2410c !important;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        border: 1px solid #fdba74;
    }

    .comp-role-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: #18181b !important;
        margin: 0.15rem 0 0.5rem 0;
    }

    .comp-location-badge {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #c2410c !important;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.5rem;
    }

    .comp-hq-text {
        font-size: 0.82rem;
        color: #71717a !important;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .comp-desc-text {
        font-size: 0.92rem;
        line-height: 1.55;
        color: #3f3f46 !important;
        margin-bottom: 0.65rem;
    }

    .comp-rationale-box {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 14px;
        padding: 0.65rem 0.95rem;
        font-size: 0.86rem;
        color: #9a3412 !important;
        margin-bottom: 0.75rem;
    }

    .skill-chip {
        display: inline-block;
        background: #f4f4f5;
        border: 1px solid #e4e4e7;
        color: #18181b !important;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.22rem 0.55rem;
        border-radius: 9999px;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    /* --- STEP 3: PULSEAI METRIC CARDS (TOTAL COST / TOTAL REQUESTS STYLE) --- */
    .pulse-metric-card {
        background: #ffffff;
        border: 1.5px solid #e4e4e7;
        border-radius: 18px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.5rem;
    }

    .pulse-metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        font-weight: 700;
        color: #71717a !important;
        letter-spacing: 0.02em;
        margin-bottom: 0.4rem;
    }

    .pulse-metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #09090b !important;
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin-bottom: 0.65rem;
    }

    /* Patterned Texture Indicator Bars matching PULSEAI */
    .bar-teal {
        height: 16px;
        border-radius: 6px;
        background: repeating-linear-gradient(45deg, #a7f3d0, #a7f3d0 6px, #6ee7b7 6px, #6ee7b7 12px);
        margin-bottom: 0.35rem;
    }

    .bar-terracotta {
        height: 16px;
        border-radius: 6px;
        background: repeating-linear-gradient(45deg, #fed7aa, #fed7aa 6px, #fb923c 6px, #fb923c 12px);
        margin-bottom: 0.35rem;
    }

    .bar-purple {
        height: 16px;
        border-radius: 6px;
        background: repeating-linear-gradient(45deg, #e9d5ff, #e9d5ff 6px, #c084fc 6px, #c084fc 12px);
        margin-bottom: 0.35rem;
    }

    .bar-orange {
        height: 16px;
        border-radius: 6px;
        background: repeating-linear-gradient(45deg, #fef08a, #fef08a 6px, #facc15 6px, #facc15 12px);
        margin-bottom: 0.35rem;
    }

    .pulse-metric-footer {
        font-size: 0.78rem;
        color: #71717a !important;
        font-weight: 500;
    }

    /* Diff Card */
    .diff-container {
        background: #ffffff;
        border: 1.5px solid #e4e4e7;
        border-radius: 18px;
        padding: 1.35rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }

    .diff-before {
        background: #fff5f5;
        border: 1px solid #fed7d7;
        border-left: 4px solid #e53e3e;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.88rem;
        color: #742a2a !important;
        margin-bottom: 0.6rem;
    }

    .diff-after {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.88rem;
        color: #14532d !important;
        margin-bottom: 0.5rem;
    }

    .diff-tag-enhancement {
        font-size: 0.82rem;
        color: #ea580c !important;
        font-weight: 700;
    }

    /* Interview Card */
    .interview-card {
        background: #ffffff;
        border: 1.5px solid #e4e4e7;
        border-radius: 18px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        border-left: 5px solid #f97316;
    }

    .interview-q-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #09090b !important;
        margin-bottom: 0.45rem;
    }

    .interview-tip-box {
        background: #fff7ed;
        border-radius: 10px;
        padding: 0.55rem 0.9rem;
        font-size: 0.85rem;
        color: #9a3412 !important;
    }

    /* Results Banner */
    .results-banner {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 24px;
        padding: 1.75rem 2.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px -4px rgba(249, 115, 22, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .download-card-box {
        background: #ffffff;
        border: 1.5px solid #e4e4e7;
        border-radius: 18px;
        padding: 1.35rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.75rem;
    }

    .badge-matched {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46 !important;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.28rem 0.65rem;
        border-radius: 9999px;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        display: inline-block;
    }

    .badge-missing {
        background: #fffbeb;
        border: 1px solid #fde68a;
        color: #92400e !important;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.28rem 0.65rem;
        border-radius: 9999px;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        display: inline-block;
    }

    /* Jake's ATS Resume Paper & Cover Letter */
    .jakes-paper {
        background: #ffffff !important;
        border: 1px solid #94a3b8;
        padding: 2.75rem 3.25rem;
        box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
        font-family: 'Segoe UI', 'Calibri', Georgia, sans-serif !important;
        color: #000000 !important;
        line-height: 1.35;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .jakes-paper * {
        font-family: 'Segoe UI', 'Calibri', Georgia, sans-serif !important;
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
        font-weight: 800;
        text-transform: uppercase;
        border-bottom: 1.5px solid #000000;
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

    .letter-paper {
        background: #ffffff !important;
        border: 1px solid #94a3b8;
        padding: 2.75rem 3.25rem;
        box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
        font-family: 'Segoe UI', 'Calibri', Georgia, sans-serif !important;
        color: #000000 !important;
        line-height: 1.55;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .letter-paper * {
        font-family: 'Segoe UI', 'Calibri', Georgia, sans-serif !important;
        color: #000000 !important;
    }

    /* Enterprise Partner Trust Strip */
    .partner-trust-bar {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2.2rem;
        flex-wrap: wrap;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #f4f4f5;
    }

    .trust-pill {
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #a1a1aa !important;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* =========================================================================
       COMPREHENSIVE MOBILE & RESPONSIVE SUITE (@media max-width: 768px & 480px)
       ========================================================================= */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 1rem !important;
            padding-bottom: 2.5rem !important;
        }

        .pulse-top-nav {
            flex-direction: column !important;
            align-items: center !important;
            gap: 0.85rem !important;
        }

        .pulse-nav-capsule {
            width: 100% !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
        }

        .pulse-hero-title {
            font-size: 2rem !important;
            line-height: 1.15 !important;
        }

        .pulse-hero-subtitle {
            font-size: 0.95rem !important;
        }

        .pulse-dashboard-card {
            padding: 1.35rem 1rem !important;
            border-radius: 22px !important;
            border-width: 2px !important;
        }

        .pulse-inner-topbar {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 0.75rem !important;
        }

        .pulse-section-title {
            font-size: 1.45rem !important;
        }

        .stButton>button {
            width: 100% !important;
            min-height: 46px !important;
        }

        .stTextInput input, 
        .stTextArea textarea {
            font-size: 16px !important;
        }

        .company-card-step2 {
            padding: 1.15rem 1rem !important;
            border-radius: 16px !important;
        }

        .comp-header-row {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 0.5rem !important;
        }

        .results-banner {
            flex-direction: column !important;
            align-items: flex-start !important;
            padding: 1.25rem 1rem !important;
        }

        .results-banner > div {
            width: 100% !important;
        }

        .jakes-paper, .letter-paper {
            padding: 1.25rem 0.95rem !important;
            font-size: 0.82rem !important;
        }

        .jakes-row {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 2px !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.3rem !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
        }

        div[data-baseweb="tab"] {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.82rem !important;
            white-space: nowrap !important;
        }
    }

    @media (max-width: 480px) {
        .pulse-hero-title {
            font-size: 1.7rem !important;
        }

        .pulse-step-pill {
            font-size: 0.72rem !important;
            padding: 0.25rem 0.55rem !important;
        }

        .website-pill-btn {
            font-size: 0.75rem !important;
            padding: 0.2rem 0.6rem !important;
        }

        .diff-container {
            padding: 0.9rem !important;
        }

        .interview-card {
            padding: 0.9rem !important;
        }
    }

    /* Live Interactive Map Box */
    [data-testid="stDeckGlJsonChart"], [data-testid="stMap"] {
        border: 1.5px solid #fed7aa !important;
        border-radius: 18px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 16px rgba(249, 115, 22, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GLOBAL TECH HUBS & COUNTRY GEOGRAPHY DATABASE ---
TECH_COUNTRIES = {
    "🇺🇸 United States": {
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
    "🇬🇧 United Kingdom": {
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
    "🇸🇬 Singapore": {
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
    "🇨🇦 Canada": {
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
    "🇩🇪 Germany": {
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
    "🇲🇾 Malaysia": {
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
    "🇦🇺 Australia": {
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
    "🇳🇱 Netherlands": {
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
    "🇮🇳 India": {
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
    "🇯🇵 Japan": {
        "hubs": ["Tokyo (Shibuya / Roppongi)", "Osaka", "Kyoto", "Fukuoka Tech Hub", "Remote (Japan)"],
        "coords": [35.6762, 139.6503],
        "zoom": 8,
        "city_coords": {
            "Tokyo (Shibuya / Roppongi)": [35.6580, 139.7016],
            "Osaka": [34.6937, 135.5023],
            "Kyoto": [35.0116, 135.7681],
            "Fukuoka Tech Hub": [33.5904, 130.4017],
            "Remote (Japan)": [36.2048, 138.2529],
        }
    },
    "🌍 Global / 100% Remote": {
        "hubs": ["Worldwide Remote", "North America Remote", "Europe / UK Remote", "APAC / Asia Remote"],
        "coords": [20.0, 0.0],
        "zoom": 2,
        "city_coords": {
            "Worldwide Remote": [20.0, 0.0],
            "North America Remote": [39.8283, -98.5795],
            "Europe / UK Remote": [54.5260, 15.2551],
            "APAC / Asia Remote": [1.3521, 103.8198],
        }
    },
    "🌐 Custom Location": {
        "hubs": ["Custom Tech Hub / City"],
        "coords": [37.7749, -122.4194],
        "zoom": 3,
        "city_coords": {
            "Custom Tech Hub / City": [37.7749, -122.4194]
        }
    }
}

# --- SESSION STATE INITIALIZATION FOR MULTI-STEP NAVIGATION ---
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "student_text" not in st.session_state:
    st.session_state.student_text = ""
if "target_country" not in st.session_state:
    st.session_state.target_country = "🇺🇸 United States"
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


# --- TOP NAVIGATION BAR & HERO HEADER (PULSEAI REPLICA) ---
step = st.session_state.current_step
s1_class = "pulse-step-pill pulse-step-pill-done" if step > 1 else ("pulse-step-pill pulse-step-pill-active" if step == 1 else "pulse-step-pill")
s2_class = "pulse-step-pill pulse-step-pill-done" if step > 2 else ("pulse-step-pill pulse-step-pill-active" if step == 2 else "pulse-step-pill")
s3_class = "pulse-step-pill pulse-step-pill-active" if step == 3 else "pulse-step-pill"

st.markdown(f"""
<div class="pulse-top-nav">
    <div class="pulse-nav-brand">
        <div class="pulse-nav-logo">⚡</div>
        <span class="pulse-nav-brand-title">RESUMEZ</span>
    </div>
    <div class="pulse-nav-capsule">
        <div class="{s1_class}"><span>{'✓' if step > 1 else '1'}</span> Candidate Profile</div>
        <div class="{s2_class}"><span>{'✓' if step > 2 else '2'}</span> Target Company</div>
        <div class="{s3_class}"><span>3</span> Enterprise Suite</div>
    </div>
    <div class="pulse-nav-action-pill">
        <span>Studio Mode ✦</span>
    </div>
</div>

<div class="pulse-hero-box">
    <h1 class="pulse-hero-title">Control where your<br>career actually goes.</h1>
    <p class="pulse-hero-subtitle">Track ATS keyword match, elevate bullets with Google XYZ metrics, and generate tailored application suites for top employers, all in one dashboard.</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# STEP 1: CANDIDATE CONTEXT (STUDENT RESUME & LOCATION)
# ==============================================================================
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="pulse-dashboard-card">
        <div class="pulse-inner-topbar">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div class="pulse-nav-logo" style="width: 28px; height: 28px; font-size: 0.9rem;">⚡</div>
                <span style="font-size: 0.95rem; font-weight: 800; letter-spacing: 0.04em; color: #09090b;">RESUMEZ</span>
                <div class="pulse-inner-tab-active">Candidate Profile</div>
                <div class="pulse-inner-tab">Company Matching</div>
                <div class="pulse-inner-tab">Tailored Assets</div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <div class="pulse-search-fake">🔍 Search skills & roles...</div>
                <div class="pulse-icon-btn">🔔</div>
                <div class="pulse-icon-btn">⚙️</div>
            </div>
        </div>
        <div class="pulse-section-header">
            <div>
                <h2 class="pulse-section-title">Candidate Profile & Context</h2>
                <p class="pulse-section-subtitle">Real-time skills extraction, experience parsing & target location preferences.</p>
            </div>
            <div class="pulse-header-badge">Step 1 of 3</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("**Upload Candidate Resume (PDF, DOCX, or TXT):**")

    # File Upload
    uploaded_file = st.file_uploader(
        "Upload existing resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt", "md"],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        try:
            extracted = extract_resume_text(uploaded_file)
            st.session_state.student_text = extracted
            st.toast(f"Parsed {uploaded_file.name} successfully!", icon="✅")
        except Exception as e:
            st.error(str(e))

    student_text_input = st.text_area(
        "Candidate Background, Experience, Coursework & Skills:",
        value=st.session_state.student_text,
        height=260,
        placeholder="Paste candidate technical stack, projects, coursework, internships, and achievements..."
    )
    st.session_state.student_text = student_text_input

    # Location Preference: Country Picker & Interactive Map
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🗺️ Target Hiring Geography & Tech Hub Map")
    st.caption("Select your target country and hiring metropolitan cluster. The interactive map will pin the active talent market:")

    loc_c1, loc_c2 = st.columns([1.1, 1.4], gap="medium")
    with loc_c1:
        country_keys = list(TECH_COUNTRIES.keys())
        country_idx = 0
        if st.session_state.target_country in country_keys:
            country_idx = country_keys.index(st.session_state.target_country)

        selected_country = st.selectbox(
            "🌍 Select Target Country:",
            options=country_keys,
            index=country_idx,
            key="country_select"
        )
        st.session_state.target_country = selected_country

        country_data = TECH_COUNTRIES[selected_country]
        hub_options = country_data["hubs"]

        hub_idx = 0
        if st.session_state.target_hub in hub_options:
            hub_idx = hub_options.index(st.session_state.target_hub)

        selected_hub = st.selectbox(
            "🏙️ Select Tech Hub / Metropolitan Area:",
            options=hub_options,
            index=hub_idx,
            key="hub_select"
        )
        st.session_state.target_hub = selected_hub

        custom_loc = ""
        if "Custom" in selected_country or "Custom" in selected_hub:
            custom_loc = st.text_input(
                "Specify Custom City / Country:",
                value=st.session_state.target_location if "Custom" in st.session_state.target_country else "",
                placeholder="e.g. Zurich, Switzerland"
            )

        # Compute full location string
        if custom_loc.strip():
            final_location_str = custom_loc.strip()
        elif "Remote" in selected_country or "Worldwide" in selected_hub:
            final_location_str = f"{selected_hub} (Global)"
        else:
            # Clean country name without flag emoji
            country_clean = selected_country.split(" ", 1)[-1]
            final_location_str = f"{selected_hub}, {country_clean}"

        st.session_state.target_location = final_location_str

        # Display Selected Hub Card Pill
        st.markdown(f"""
        <div style="background: #fff7ed; border: 1.5px solid #fed7aa; border-radius: 14px; padding: 0.85rem 1rem; margin-top: 0.75rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #ea580c; font-weight: 800; letter-spacing: 0.05em;">Active Hiring Market</div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #09090b; margin: 0.15rem 0 0.25rem 0;">
                📍 {final_location_str}
            </div>
            <span style="font-size: 0.78rem; color: #16a34a; font-weight: 600;">✓ Synced with Company Matching AI</span>
        </div>
        """, unsafe_allow_html=True)

    with loc_c2:
        # Determine coordinates for the map
        city_coords = country_data.get("city_coords", {})
        coords = city_coords.get(selected_hub, country_data.get("coords", [37.7749, -122.4194]))
        zoom_level = country_data.get("zoom", 5)

        map_df = pd.DataFrame([{
            "lat": coords[0],
            "lon": coords[1],
        }])

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #71717a;">MAP VIEW: {selected_country}</span>
            <span style="font-size: 0.75rem; color: #ea580c; font-weight: 600; background: #fff7ed; padding: 0.15rem 0.55rem; border-radius: 6px; border: 1px solid #fed7aa;">
                Coordinates: {coords[0]:.2f}°, {coords[1]:.2f}°
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.map(map_df, zoom=zoom_level, use_container_width=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    
    # Action Button to Move to Step 2
    btn_c1, btn_c2, btn_c3 = st.columns([1.5, 2, 1.5])
    with btn_c2:
        if st.button("↗ Continue to Step 2: Choose Company", use_container_width=True, type="primary"):
            if not st.session_state.student_text.strip():
                st.warning("Please upload or paste a candidate resume profile first.")
            else:
                if not st.session_state.recommended_companies:
                    with st.spinner("Analyzing candidate stack and discovering matching companies with verified websites..."):
                        try:
                            recs = recommend_companies_for_student(
                                resume_text=st.session_state.student_text,
                                target_location=st.session_state.target_location
                            )
                            st.session_state.recommended_companies = recs
                        except Exception as e:
                            st.error(f"Error fetching company matches: {e}")
                st.session_state.current_step = 2
                st.rerun()

    st.markdown("""
    <div class="partner-trust-bar">
        <span class="trust-pill">⚡ GOOGLE</span>
        <span class="trust-pill">✦ STRIPE</span>
        <span class="trust-pill">❖ DATABRICKS</span>
        <span class="trust-pill">◆ META</span>
        <span class="trust-pill">▲ VERCEL</span>
        <span class="trust-pill">● OPENAI</span>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# STEP 2: COMPANY SELECTION & DETAILS (WITH OFFICIAL WEBSITE LINKS)
# ==============================================================================
elif st.session_state.current_step == 2:
    st.markdown("""
    <div class="pulse-dashboard-card">
        <div class="pulse-inner-topbar">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div class="pulse-nav-logo" style="width: 28px; height: 28px; font-size: 0.9rem;">⚡</div>
                <span style="font-size: 0.95rem; font-weight: 800; letter-spacing: 0.04em; color: #09090b;">RESUMEZ</span>
                <div class="pulse-inner-tab">Candidate Profile</div>
                <div class="pulse-inner-tab-active">Company Matching</div>
                <div class="pulse-inner-tab">Tailored Assets</div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <div class="pulse-search-fake">🔍 Search employers...</div>
                <div class="pulse-icon-btn">🔔</div>
                <div class="pulse-icon-btn">⚙️</div>
            </div>
        </div>
        <div class="pulse-section-header">
            <div>
                <h2 class="pulse-section-title">Target Company & Role Alignment</h2>
                <p class="pulse-section-subtitle">Choose from AI-curated company matches with verified websites, or paste a custom job posting.</p>
            </div>
            <div class="pulse-header-badge">Step 2 of 3</div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation back to Step 1
    top_nav_col1, top_nav_col2 = st.columns([1.5, 4.5])
    with top_nav_col1:
        if st.button("← Back to Step 1", use_container_width=True, type="secondary"):
            st.session_state.current_step = 1
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    tab_suggested, tab_custom = st.tabs(["✨ AI Curated Company Matches", "✍️ Custom Company & Job Posting"])

    # TAB A: AI CURATED MATCHES WITH OFFICIAL WEBSITE LINKS
    with tab_suggested:
        if not st.session_state.recommended_companies:
            st.info("No recommendations found yet. Click below to analyze your profile.")
            if st.button("🔍 Find Matching Companies Now", type="primary"):
                with st.spinner("Analyzing profile and matching companies..."):
                    try:
                        recs = recommend_companies_for_student(
                            resume_text=st.session_state.student_text,
                            target_location=st.session_state.target_location
                        )
                        st.session_state.recommended_companies = recs
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.markdown(f"<p style='color: #475569; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem;'>Showing <b>{len(st.session_state.recommended_companies)}</b> verified employers matching your profile in <i>{st.session_state.target_location}</i>:</p>", unsafe_allow_html=True)

            for idx, rec in enumerate(st.session_state.recommended_companies):
                c_name = rec.get("company_name", "Company")
                website = rec.get("website_url", "https://google.com")
                hq = rec.get("headquarters", "San Francisco, CA")
                target_loc = rec.get("target_locations", st.session_state.target_location)
                policy = rec.get("work_policy", "Hybrid")
                r_title = rec.get("role_title", "Software Engineering Intern")
                overview = rec.get("company_overview", "")
                fit = rec.get("fit_score", 92)
                reason = rec.get("match_reason", "")
                skills = rec.get("skills_match", [])

                with st.container():
                    st.markdown(f"""
                    <div class="company-card-step2">
                        <div class="comp-header-row">
                            <div class="comp-title-group">
                                <span class="comp-name-text">{c_name}</span>
                                <a href="{website}" target="_blank" class="website-pill-btn">
                                    🌐 Website ↗
                                </a>
                            </div>
                            <span class="fit-score-badge">{fit}% Match</span>
                        </div>
                        <div class="comp-role-text">{r_title}</div>
                        <div>
                            <span class="comp-location-badge">📍 {target_loc}</span>
                            <span class="comp-hq-text">• <b>HQ:</b> {hq} ({policy})</span>
                        </div>
                        <div class="comp-desc-text"><b>About the Company:</b> {overview}</div>
                        <div class="comp-rationale-box"><b>Why Candidate Fits:</b> {reason}</div>
                        <div style="margin-bottom: 0.8rem;">
                            {' '.join([f'<span class="skill-chip">{s}</span>' for s in skills])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"🎯 Select {c_name} & Generate Enterprise Suite →", key=f"btn_choose_{idx}", use_container_width=True, type="primary"):
                        st.session_state.company_name = c_name
                        st.session_state.role_title = r_title
                        st.session_state.company_website = website
                        st.session_state.job_description = rec.get("job_description", "")

                        with st.spinner(f"Crafting Jake's Resume, Cover Letter, ATS Diagnostics & Interview Prep for {c_name}..."):
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
                                st.toast(f"Enterprise suite generated for {c_name}!", icon="🚀")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error tailoring documents: {e}")

    # TAB B: CUSTOM COMPANY & JOB DESCRIPTION
    with tab_custom:
        custom_c1, custom_c2 = st.columns(2)
        with custom_c1:
            comp_in = st.text_input("Target Company Name:", value=st.session_state.company_name, placeholder="e.g. Stripe, Google, Apple")
            st.session_state.company_name = comp_in
        with custom_c2:
            role_in = st.text_input("Target Role Title:", value=st.session_state.role_title, placeholder="e.g. Software Engineering Intern")
            st.session_state.role_title = role_in

        web_in = st.text_input("Company Website URL:", value=st.session_state.company_website, placeholder="e.g. https://stripe.com")
        st.session_state.company_website = web_in

        jd_in = st.text_area(
            "Paste Target Job Description & Requirements:",
            value=st.session_state.job_description,
            height=220,
            placeholder="Paste role requirements, tech stack, and responsibilities..."
        )
        st.session_state.job_description = jd_in

        if st.button("🚀 Generate Enterprise Suite →", use_container_width=True, type="primary"):
            if not st.session_state.student_text.strip():
                st.warning("Please provide student profile text in Step 1.")
            elif not st.session_state.job_description.strip():
                st.warning("Please provide the job description.")
            else:
                with st.spinner("Synthesizing Jake's Resume, Application Letter, Diagnostics & Interview Prep..."):
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
                        st.toast("Generated Enterprise Suite successfully!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating documents: {e}")

    st.markdown("""
    <div class="partner-trust-bar">
        <span class="trust-pill">⚡ GOOGLE</span>
        <span class="trust-pill">✦ STRIPE</span>
        <span class="trust-pill">❖ DATABRICKS</span>
        <span class="trust-pill">◆ META</span>
        <span class="trust-pill">▲ VERCEL</span>
        <span class="trust-pill">● OPENAI</span>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# STEP 3: ENTERPRISE SUITE (DIAGNOSTICS, DOWNLOADS, PREVIEWS & PREP)
# ==============================================================================
elif st.session_state.current_step == 3:
    data = st.session_state.tailored_data
    if not data:
        st.warning("No tailored data available. Please select a company in Step 2.")
        if st.button("Go to Step 2"):
            st.session_state.current_step = 2
            st.rerun()
    else:
        assessment = data.get("ats_assessment", {})
        score = assessment.get("match_score", 93)
        breakdown = assessment.get("breakdown", {})
        s_score = breakdown.get("skills_match_score", 95)
        i_score = breakdown.get("impact_metric_score", 91)
        f_score = breakdown.get("format_compliance_score", 99)
        b_score = breakdown.get("brevity_score", 94)

        target_comp = assessment.get("target_company") or st.session_state.company_name or "Target Company"
        target_r = assessment.get("target_role") or st.session_state.role_title or "Role"
        rep_loc = assessment.get("location") or st.session_state.target_location
        website = st.session_state.company_website or "https://google.com"

        st.markdown(f"""
        <div class="pulse-dashboard-card">
            <div class="pulse-inner-topbar">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div class="pulse-nav-logo" style="width: 28px; height: 28px; font-size: 0.9rem;">⚡</div>
                    <span style="font-size: 0.95rem; font-weight: 800; letter-spacing: 0.04em; color: #09090b;">RESUMEZ</span>
                    <div class="pulse-inner-tab">Candidate Profile</div>
                    <div class="pulse-inner-tab">Company Matching</div>
                    <div class="pulse-inner-tab-active">Enterprise Analytics</div>
                </div>
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <div class="pulse-search-fake">🔍 Search diagnostics...</div>
                    <div class="pulse-icon-btn">🔔</div>
                    <div class="pulse-icon-btn">⚙️</div>
                </div>
            </div>
            <div class="pulse-section-header">
                <div>
                    <h2 class="pulse-section-title">Enterprise Analytics Overview</h2>
                    <p class="pulse-section-subtitle">Real-time ATS infrastructure performance & tailored application suite for {target_comp}.</p>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div class="pulse-date-pill">📅 Cycle: 2026 Active</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Back & Reset Buttons Row
        b_c1, b_c2, b_c3 = st.columns([1.5, 3.5, 1.5])
        with b_c1:
            if st.button("← Choose Another Company", use_container_width=True, type="secondary"):
                st.session_state.current_step = 2
                st.rerun()
        with b_c3:
            if st.button("Start New Resume ⟲", use_container_width=True, type="secondary"):
                st.session_state.current_step = 1
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Executive Banner with Website Link
        website_markup = f'<a href="{website}" target="_blank" class="website-pill-btn" style="margin-left: 0.5rem;">🌐 Official Website ↗</a>' if website else ''
        
        st.markdown(f"""
        <div class="results-banner">
            <div>
                <span style="background: #fff7ed; color: #c2410c; font-weight: 700; font-size: 0.8rem; padding: 0.3rem 0.85rem; border-radius: 9999px; border: 1px solid #fed7aa;">
                    ✓ Enterprise Suite Generated
                </span>
                <div style="display: flex; align-items: center; margin-top: 0.4rem; flex-wrap: wrap; gap: 0.5rem;">
                    <h2 style="font-size: 1.85rem; font-weight: 800; color: #09090b !important; margin: 0;">
                        Tailored for {target_comp}
                    </h2>
                    {website_markup}
                </div>
                <p style="color: #71717a !important; font-size: 0.95rem; margin: 0.25rem 0 0 0;">
                    Target Role: <b>{target_r}</b> &nbsp;•&nbsp; Location: <b>{rep_loc}</b>
                </p>
            </div>
            <div style="text-align: right; background: #fafafa; border: 1.5px solid #e4e4e7; padding: 0.9rem 1.6rem; border-radius: 20px;">
                <span style="font-size: 0.75rem; text-transform: uppercase; color: #71717a !important; font-weight: 800; letter-spacing: 0.05em;">Overall ATS Match</span>
                <div style="font-size: 2.4rem; font-weight: 800; color: #09090b !important; line-height: 1;">{score}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4-CATEGORY ENTERPRISE ATS BREAKDOWN ROW (PULSEAI METRIC CARDS)
        st.markdown("### 📊 Enterprise ATS Performance Diagnostics")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="pulse-metric-card">
                <div class="pulse-metric-header">
                    <span>TECH STACK MATCH</span>
                    <span>↗</span>
                </div>
                <div class="pulse-metric-val">{s_score}%</div>
                <div class="bar-teal"></div>
                <div class="pulse-metric-footer">Hard skills aligned with role</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="pulse-metric-card">
                <div class="pulse-metric-header">
                    <span>XYZ IMPACT SCORE</span>
                    <span>↗</span>
                </div>
                <div class="pulse-metric-val">{i_score}%</div>
                <div class="bar-terracotta"></div>
                <div class="pulse-metric-footer">Action verbs & quantifiable metrics</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="pulse-metric-card">
                <div class="pulse-metric-header">
                    <span>ATS PARSING RATE</span>
                    <span>↗</span>
                </div>
                <div class="pulse-metric-val">{f_score}%</div>
                <div class="bar-purple"></div>
                <div class="pulse-metric-footer">Strict single-column B&W standard</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="pulse-metric-card">
                <div class="pulse-metric-header">
                    <span>1-PAGE BREVITY</span>
                    <span>↗</span>
                </div>
                <div class="pulse-metric-val">{b_score}%</div>
                <div class="bar-orange"></div>
                <div class="pulse-metric-footer">Layout & density optimized</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # DUAL DOWNLOAD CARDS (DOCX + DIRECT ATS PDF EXPORT)
        dl_col1, dl_col2 = st.columns(2, gap="medium")
        student_clean = data.get("personal_info", {}).get("name", "Student").replace(" ", "_")
        comp_clean = target_comp.replace(" ", "_")

        # Resume Downloads (.docx + .pdf)
        resume_docx_buf = create_jakes_resume_docx(data)
        resume_pdf_buf = create_jakes_resume_pdf(data)
        with dl_col1:
            st.markdown("""
            <div class="download-card-box">
                <div style="font-size: 1.05rem; font-weight: 700; color: #111827; margin-bottom: 0.2rem;">📄 Jake's Resume Template (Black & White)</div>
                <div style="font-size: 0.84rem; color: #64748b; margin-bottom: 0.75rem;">Strict ATS single-column formatting. Choose DOCX or direct PDF:</div>
            </div>
            """, unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            with rc1:
                st.download_button(
                    label="📥 Download .DOCX",
                    data=resume_docx_buf,
                    file_name=f"{student_clean}_{comp_clean}_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            with rc2:
                st.download_button(
                    label="📄 Download .PDF",
                    data=resume_pdf_buf,
                    file_name=f"{student_clean}_{comp_clean}_Resume.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )

        # Cover Letter Downloads (.docx + .pdf)
        letter_docx_buf = create_application_letter_docx(data)
        letter_pdf_buf = create_application_letter_pdf(data)
        with dl_col2:
            st.markdown("""
            <div class="download-card-box">
                <div style="font-size: 1.05rem; font-weight: 700; color: #111827; margin-bottom: 0.2rem;">✉️ Tailored Application Letter</div>
                <div style="font-size: 0.84rem; color: #64748b; margin-bottom: 0.75rem;">Custom cover letter matching employer mission. Choose DOCX or direct PDF:</div>
            </div>
            """, unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            with lc1:
                st.download_button(
                    label="📥 Download .DOCX",
                    data=letter_docx_buf,
                    file_name=f"{student_clean}_{comp_clean}_Application_Letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            with lc2:
                st.download_button(
                    label="📄 Download .PDF",
                    data=letter_pdf_buf,
                    file_name=f"{student_clean}_{comp_clean}_Application_Letter.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )

        # 5 ENTERPRISE PREVIEW TABS
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        tab_res_preview, tab_letter_preview, tab_diff, tab_interview, tab_linkedin = st.tabs([
            "📄 Jake's Resume (B&W)",
            "✉️ Application Letter",
            "🔄 Before vs. After Diff",
            "🎙️ AI Mock Interview Prep",
            "💼 LinkedIn Suite & Strategy"
        ])

        # TAB 1: JAKES RESUME PREVIEW (IN BLACK & WHITE)
        with tab_res_preview:
            p_info = data.get("personal_info", {})
            contact_line = "  |  ".join([p for p in [p_info.get("phone"), p_info.get("email"), p_info.get("linkedin"), p_info.get("github"), p_info.get("portfolio")] if p])

            st.markdown('<div class="jakes-paper">', unsafe_allow_html=True)
            st.markdown(f'<div class="jakes-name">{p_info.get("name", "Student Name")}</div>', unsafe_allow_html=True)
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
                    
                    cw = edu.get("relevant_coursework", [])
                    if cw:
                        cw_str = ", ".join(cw) if isinstance(cw, list) else str(cw)
                        st.markdown(f'<div style="font-size: 0.88rem; margin-top: 2px;"><b>Relevant Coursework:</b> {cw_str}</div>', unsafe_allow_html=True)

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
                    title = proj.get("title", "")
                    tech = proj.get("tech_stack", "")
                    dates = proj.get("dates", "")
                    title_line = f"{title}" + (f" | <i>{tech}</i>" if tech else "")

                    st.markdown(f'''
                    <div class="jakes-row">
                        <span class="jakes-bold">{title_line}</span>
                        <span>{dates}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                    bullets_html = "".join([f"<li>{b}</li>" for b in proj.get("bullets", [])])
                    st.markdown(f'<ul class="jakes-ul">{bullets_html}</ul>', unsafe_allow_html=True)

            skills = data.get("skills", {})
            if skills:
                st.markdown('<div class="jakes-section-title">Technical Skills</div>', unsafe_allow_html=True)
                if isinstance(skills, dict):
                    for cat, items in skills.items():
                        items_str = ", ".join(items) if isinstance(items, list) else str(items)
                        st.markdown(f'<div style="font-size: 0.88rem; margin-bottom: 2px;"><b>{cat}:</b> {items_str}</div>', unsafe_allow_html=True)
                elif isinstance(skills, list):
                    st.markdown(f'<div style="font-size: 0.88rem;"><b>Skills:</b> {", ".join(skills)}</div>', unsafe_allow_html=True)

            certs = data.get("certifications_or_awards", [])
            if certs:
                st.markdown('<div class="jakes-section-title">Honors & Certifications</div>', unsafe_allow_html=True)
                c_html = "".join([f"<li>{c}</li>" for c in certs])
                st.markdown(f'<ul class="jakes-ul">{c_html}</ul>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2: APPLICATION LETTER PREVIEW
        with tab_letter_preview:
            letter = data.get("application_letter", {})
            p_info = data.get("personal_info", {})
            
            st.markdown('<div class="letter-paper">', unsafe_allow_html=True)
            st.markdown(f'<h3>{p_info.get("name", "Student Name")}</h3>', unsafe_allow_html=True)
            c_parts = [p for p in [p_info.get("phone"), p_info.get("email"), p_info.get("location")] if p]
            st.markdown(f'<p style="color: #334155 !important;">{" | ".join(c_parts)}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-top: 1.5rem; color: #334155 !important;"><b>Date:</b> {letter.get("date", "October 31, 2026")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #334155 !important;"><b>To:</b> {letter.get("recipient", "Hiring Team")}<br><b>Company:</b> {target_comp}<br><b>Location:</b> {rep_loc}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 1.05rem; font-weight: 700; color: #000000 !important; margin: 1.25rem 0;">Subject: Application for {target_r}</p>', unsafe_allow_html=True)
            
            st.markdown(f'<p style="color: #000000 !important;">Dear {letter.get("recipient", "Hiring Team")} at {target_comp},</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #000000 !important;">{letter.get("opening", "")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #000000 !important;">{letter.get("body_paragraph_1", "")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #000000 !important;">{letter.get("body_paragraph_2", "")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #000000 !important;">{letter.get("closing", "")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-top: 1.5rem; color: #000000 !important;">Sincerely,<br><b>{p_info.get("name", "Student Name")}</b></p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 3: BEFORE VS AFTER BULLET TRANSFORMATIONS (FEATURE 3)
        with tab_diff:
            st.markdown("#### 🔄 Bullet Point Elevation (Google XYZ Transformation)")
            st.write("Review how raw candidate statements were restructured with active verbs, technical context, and quantifiable metrics:")
            
            transforms = data.get("bullet_transformations", [])
            if not transforms:
                st.info("Transforms generated automatically across experience & projects above.")
            else:
                for tf in transforms:
                    st.markdown(f"""
                    <div class="diff-container">
                        <div style="font-weight: 700; color: #111827; font-size: 0.95rem; margin-bottom: 0.5rem;">
                            📌 {tf.get('context', 'Experience Item')}
                        </div>
                        <div class="diff-before">
                            <b>Original Draft:</b> {tf.get('original_bullet', '')}
                        </div>
                        <div class="diff-after">
                            <b>Elevated (Google XYZ):</b> {tf.get('elevated_bullet', '')}
                        </div>
                        <div class="diff-tag-enhancement">
                            💡 <b>Impact Added:</b> {tf.get('impact_enhancement', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 4: AI MOCK INTERVIEW PREPARATION (FEATURE 2)
        with tab_interview:
            st.markdown(f"#### 🎙️ AI Mock Interview Questions for {target_comp}")
            st.write(f"Recruiters at {target_comp} formulate questions based on your highlighted projects and company values. Prepare with these tailored scenarios:")

            interview_data = data.get("interview_prep", {})
            tech_q = interview_data.get("technical_questions", [])
            behav_q = interview_data.get("behavioral_questions", [])

            st.markdown("##### ⚙️ Technical Architecture & Project Questions")
            for t in tech_q:
                st.markdown(f"""
                <div class="interview-card">
                    <div class="interview-q-title">Q: {t.get('question', '')}</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 0.4rem;">
                        <b>Focus Domain:</b> {t.get('focus_area', 'Architecture')}
                    </div>
                    <div class="interview-tip-box">
                        💡 <b>Talking Points to Hit:</b> {t.get('answer_strategy', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### 🤝 Company Culture & Behavioral Questions")
            for b in behav_q:
                st.markdown(f"""
                <div class="interview-card" style="border-left-color: #ec4899;">
                    <div class="interview-q-title">Q: {b.get('question', '')}</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 0.4rem;">
                        <b>Core Employer Value:</b> {b.get('company_value', 'Leadership')}
                    </div>
                    <div class="interview-tip-box">
                        💡 <b>STAR Method Strategy:</b> {b.get('answer_strategy', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 5: LINKEDIN SUITE & STRATEGY (FEATURE 5)
        with tab_linkedin:
            st.markdown("#### 💼 LinkedIn Profile Alignment")
            st.write("Recruiters consistently cross-reference your resume with your LinkedIn profile. Use this optimized headline and summary:")

            li_suite = data.get("linkedin_suite", {})
            st.text_input("Optimized LinkedIn Headline (Copy & Paste):", value=li_suite.get("headline", ""), help="Paste into your LinkedIn intro")
            st.text_area("Optimized LinkedIn 'About' Summary:", value=li_suite.get("about_summary", ""), height=110)

            st.divider()
            st.markdown("#### 🎯 Recruiter Strategic Assessment")
            st.write(assessment.get("tailoring_summary", ""))

            st.markdown("#### Keywords Integrated into Resume")
            matched_kw = assessment.get("key_matched_keywords", [])
            if matched_kw:
                badges_html = " ".join([f'<span class="badge-matched">✓ {kw}</span>' for kw in matched_kw])
                st.markdown(badges_html, unsafe_allow_html=True)

            st.markdown("#### Recommended Keywords for Interviews")
            missing_kw = assessment.get("missing_or_recommended_keywords", [])
            if missing_kw:
                missing_html = " ".join([f'<span class="badge-missing">ℹ {kw}</span>' for kw in missing_kw])
                st.markdown(missing_html, unsafe_allow_html=True)

        st.markdown("""
        <div class="partner-trust-bar">
            <span class="trust-pill">⚡ GOOGLE</span>
            <span class="trust-pill">✦ STRIPE</span>
            <span class="trust-pill">❖ DATABRICKS</span>
            <span class="trust-pill">◆ META</span>
            <span class="trust-pill">▲ VERCEL</span>
            <span class="trust-pill">● OPENAI</span>
        </div>
        </div>
        """, unsafe_allow_html=True)
