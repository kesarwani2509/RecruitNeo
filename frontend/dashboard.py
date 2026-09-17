import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="RecruitNeo", layout="wide", initial_sidebar_state="expanded")

def safe_error(response, fallback="Request failed"):
    try:
        data = response.json() if hasattr(response, "json") else {}
        if isinstance(data, dict):
            return data.get("detail") or data.get("message") or fallback
        if isinstance(data, str):
            return data
    except Exception:
        pass
    return fallback


def inject_corporate_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #21262d;
        --surface-glass: rgba(255, 255, 255, 0.03);
        --surface-hover: rgba(255, 255, 255, 0.06);
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-medium: rgba(255, 255, 255, 0.14);
        --accent-primary: #6366F1;
        --accent-hover: #818CF8;
        --accent-pressed: #4F46E5;
        --accent-soft: rgba(99, 102, 241, 0.15);
        --text-primary: #E5E7EB;
        --text-secondary: #9CA3AF;
        --text-tertiary: #6B7280;
        --success: #10B981;
        --success-soft: rgba(16, 185, 129, 0.12);
        --warning: #F59E0B;
        --warning-soft: rgba(245, 158, 11, 0.12);
        --danger: #EF4444;
        --danger-soft: rgba(239, 68, 68, 0.12);
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
        --transition: 150ms ease;
    }

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }

    .stApp {
        background: linear-gradient(180deg, #0d1117 0%, #111827 100%) !important;
    }
    .stApp > header { display: none !important; }

    .main .block-container {
        background: transparent !important;
        padding: 2rem 3rem !important;
        margin-top: 0 !important;
    }

    section[data-testid="stSidebar"] {
        background: #0b0e14 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }
    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.05rem !important; }

    p, span, div, label, .stMarkdown {
        color: var(--text-primary) !important;
    }

    .stButton > button {
        background: var(--accent-primary) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border-radius: var(--radius-md) !important;
        padding: 0.5rem 1.25rem !important;
        transition: background var(--transition), box-shadow var(--transition), transform var(--transition) !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    .stButton > button:hover {
        background: var(--accent-hover) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        background: var(--accent-pressed) !important;
        transform: translateY(0) !important;
    }

    .stButton > button[kind="secondary"] {
        background: var(--surface-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        box-shadow: none !important;
        color: var(--text-primary) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: var(--surface-hover) !important;
        border-color: var(--border-medium) !important;
        box-shadow: none !important;
        color: white !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input,
    .stDateInput > div > div > input:focus {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-md) !important;
        font-size: 0.875rem !important;
        transition: all var(--transition) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        outline: none !important;
    }

    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        margin-bottom: 0.25rem !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    .stSelectbox [data-baseweb="select"]:hover > div {
        border-color: var(--border-medium) !important;
    }
    .stSelectbox [data-baseweb="popover"] [data-baseweb=\"menu\"] {
        background: var(--bg-primary, #161b22) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    .stForm { background: transparent !important; border: none !important; padding: 0 !important; }

    .stExpander {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        margin-bottom: 0.75rem !important;
    }
    .stExpander > summary {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
        padding: 1rem 1.25rem !important;
    }
    .stExpander > summary:hover { color: white !important; }
    .stExpanderDetails {
        padding: 0 1.25rem 1.25rem !important;
        border-top: 1px solid var(--border-subtle) !important;
    }

    .stDataFrame {
        background: transparent !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }
    .stDataFrame table { color: var(--text-primary) !important; }
    .stDataFrame th {
        background: rgba(255, 255, 255, 0.03) !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.75rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        padding: 0.625rem 1rem !important;
    }
    .stDataFrame td {
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
        padding: 0.625rem 1rem !important;
        font-size: 0.875rem !important;
    }
    .stDataFrame tr:hover td {
        background: var(--surface-hover) !important;
    }

    .stAlert {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    .stAlert[data-baseweb="notification"][kind="success"] {
        border-left: 4px solid var(--success) !important;
        background: var(--success-soft) !important;
    }
    .stAlert[data-baseweb="notification"][kind="error"] {
        border-left: 4px solid var(--danger) !important;
        background: var(--danger-soft) !important;
    }
    .stAlert[data-baseweb="notification"][kind="info"] {
        border-left: 4px solid var(--accent-primary) !important;
        background: var(--accent-soft) !important;
    }
    .stAlert[data-baseweb="notification"][kind="warning"] {
        border-left: 4px solid var(--warning) !important;
        background: var(--warning-soft) !important;
    }

    .stSpinner > div { border-top-color: var(--accent-primary) !important; }

    .stRadio > label { color: var(--text-primary) !important; font-weight: 500 !important; }
    .stRadio [role="radiogroup"] > label {
        background: var(--surface-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.625rem 1rem !important;
        margin-bottom: 0.375rem !important;
        transition: background var(--transition), border var(--transition) !important;
        cursor: pointer !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }
    .stRadio [role="radiogroup"] > label:hover {
        border-color: var(--border-medium) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    .stRadio [role="radiogroup"] > label[data-checked="true"] {
        background: var(--accent-soft) !important;
        border-color: var(--accent-primary) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary, #0d1117) !important; }
    ::-webkit-scrollbar-thumb { background: #374151 !important; border-radius: 4px !important; }
    ::-webkit-scrollbar-thumb:hover { background: #4B5563 !important; }

    .card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        transition: background var(--transition), border var(--transition), transform var(--transition) !important;
    }
    .card:hover {
        background: rgba(255, 255, 255, 0.035) !important;
        border-color: var(--border-medium) !important;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem 1.25rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: background var(--transition), border-color var(--transition), transform var(--transition) !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.035) !important;
        border-color: var(--border-medium) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1.2 !important;
        margin-bottom: 0.375rem !important;
    }
    .metric-label {
        font-size: 0.75rem !important;
        font-weight: 400 !important;
        color: var(--text-secondary) !important;
    }
    .metric-dot {
        display: inline-block !important;
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
    }

    .verdict-badge {
        display: inline-block !important;
        padding: 0.2rem 0.75rem !important;
        border-radius: 100px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }
    .verdict-high {
        background: var(--success-soft) !important;
        color: var(--success) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
    }
    .verdict-medium {
        background: var(--warning-soft) !important;
        color: var(--warning) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
    }
    .verdict-low {
        background: var(--danger-soft) !important;
        color: var(--danger) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
    }

    .skill-tag {
        display: inline-block !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-secondary) !important;
        padding: 0.2rem 0.625rem !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.7375rem !important;
        font-weight: 500 !important;
        margin: 0.25rem 0.25rem 0.25rem 0 !important;
    }

    .section-divider {
        height: 1px !important;
        background: var(--border-subtle) !important;
        margin: 2rem 0 !important;
        width: 100% !important;
    }

    .page-header {
        margin-bottom: 2rem !important;
    }
    .page-title {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin: 0 0 0.25rem 0 !important;
    }
    .page-subtitle {
        font-size: 0.9375rem !important;
        color: var(--text-secondary) !important;
        margin: 0 !important;
    }

    .login-wrapper {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 70vh !important;
        padding: 2rem !important;
    }
    .login-panel {
        width: 100% !important;
        max-width: 440px !important;
        background: rgba(255, 255, 255, 0.025) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: 2.5rem 2.25rem !important;
        box-shadow: var(--shadow-md) !important;
    }
    .login-brand {
        text-align: center !important;
        margin-bottom: 0.25rem !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }
    .login-desc {
        text-align: center !important;
        color: var(--text-secondary) !important;
        margin-bottom: 2rem !important;
        font-size: 0.875rem !important;
    }

    .stFileUploader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--radius-lg) !important;
        padding: 2rem !important;
        transition: border-color var(--transition), background var(--transition) !important;
    }
    .stFileUploader:hover {
        border-color: var(--accent-primary) !important;
        background: rgba(99, 102, 241, 0.04) !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
    }

    .stMarkdown code {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-primary) !important;
        padding: 0.125rem 0.375rem !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.875em !important;
    }

    .stProgress > div > div > div > div {
        background: var(--accent-primary) !important;
    }
    .stSelectbox [role="listbox"] {
        background: #161b22 !important;
    }

    .nav-item {
        display: flex !important;
        align-items: center !important;
        gap: 0.625rem !important;
        padding: 0.625rem 0.875rem !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: background var(--transition), color var(--transition) !important;
        cursor: pointer !important;
        margin-bottom: 0.25rem !important;
    }
    .nav-item:hover {
        color: var(--text-primary) !important;
        background: var(--surface-hover) !important;
    }
    .nav-item.active {
        color: white !important;
        background: var(--accent-soft) !important;
        font-weight: 600 !important;
    }
    .nav-item-active-indicator {
        width: 3px !important;
        height: 20px !important;
        background: var(--accent-primary) !important;
        border-radius: 3px !important;
        margin-right: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


SVG_DASHBOARD = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
SVG_BRIEFCASE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>'
SVG_UPLOAD = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>'
SVG_USERS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>'
SVG_LOGO = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="6" fill="#6366F1"/><path d="M7 9l5 5 5-5" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def render_footer():
    st.markdown(
        '<div style="text-align:center;color:var(--text-tertiary);'
        'font-size:0.75rem;padding:2.5rem 0 1rem;border-top:1px solid var(--border-subtle);'
        'margin-top:2rem;">SK Enterprise &copy; 2026</div>',
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=None):
    st.markdown(f'<div class="page-header"><h1 class="page-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_metric_card(label, value, variant="default"):
    variant_html = ""
    if variant == "accent":
        variant_html = '<span class="metric-dot" style="background:var(--accent-primary)"></span>'
    elif variant == "success":
        variant_html = '<span class="metric-dot" style="background:var(--success)"></span>'
    elif variant == "warning":
        variant_html = '<span class="metric-dot" style="background:var(--warning)"></span>'
    elif variant == "danger":
        variant_html = '<span class="metric-dot" style="background:var(--danger)"></span>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{variant_html}{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_verdict_badge(verdict):
    css_class = {
        "High": "verdict-high",
        "Medium": "verdict-medium",
        "Low": "verdict-low"
    }.get(verdict, "verdict-low")
    return f'<span class="verdict-badge {css_class}">{verdict}</span>'


def role_can_manage_jd(jd, current_user_id):
    role = st.session_state.get("user", {}).get("role", "")
    if role == "admin":
        return True
    if role == "recruiter":
        return str(jd.get("created_by") or "") == current_user_id
    return False


def render_skill_tags(skills):
    if not skills:
        return '<span style="color: var(--text-tertiary); font-style: italic;">None</span>'
    tags = ''.join([f'<span class="skill-tag">{s}</span>' for s in skills])
    return tags


def login_page():
    inject_corporate_css()
    st.markdown('<div style="height:6vh;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:
        st.markdown('<div class="login-panel">', unsafe_allow_html=True)

        if st.session_state.get("show_register", False):
            st.markdown('<div class="login-brand">RecruitNeo</div><div class="login-desc">Create your account</div>', unsafe_allow_html=True)
            with st.form("register"):
                name = st.text_input("Full Name", key="reg_name", placeholder="John Doe")
                remail = st.text_input("Email", key="reg_email", placeholder="john@company.com")
                rpass = st.text_input("Password", type="password", key="reg_pass", placeholder="")
                role = st.selectbox("Role", ["recruiter", "admin", "student"], key="reg_role")
                location = st.text_input("Location", key="reg_loc", placeholder="Hyderabad, Bangalore, etc.")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    r = api_post("/api/auth/register", json={
                        "name": name, "email": remail, "password": rpass,
                        "role": role, "location": location,
                    })
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["user"] = data["user"]
                        st.session_state["show_register"] = False
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(safe_error(r, "Registration failed"))

            if st.button("Back to Login", use_container_width=True, type="secondary"):
                st.session_state["show_register"] = False
                st.rerun()

        else:
            st.markdown('<div class="login-brand">RecruitNeo</div><div class="login-desc">Sign in to your account</div>', unsafe_allow_html=True)
            with st.form("login"):
                email = st.text_input("Email", placeholder="recruiter@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    r = api_post("/api/auth/login", json={"email": email, "password": password})
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["user"] = data["user"]
                        st.rerun()
                    else:
                        st.error(safe_error(r, "Invalid email or password"))

            st.markdown('<div style="text-align:center; margin-top:1rem"><span style="color:var(--text-secondary); font-size:0.85rem">New to RecruitNeo?</span></div>', unsafe_allow_html=True)
            if st.button("Create an Account", use_container_width=True, type="secondary"):
                st.session_state["show_register"] = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    render_footer()


class _OfflineResponse:
    def __init__(self, message):
        self.status_code = 503
        self._message = message

    def json(self):
        return {"detail": self._message, "access_token": None, "user": None}


def _safe_request(method_fn, path, **kwargs):
    try:
        return method_fn(f"{API_BASE}{path}", **kwargs)
    except requests.exceptions.RequestException as exc:
        return _OfflineResponse(
            f"Could not reach the API at {API_BASE} ({exc.__class__.__name__}). Is the backend running?"
        )


def api_get(path, token=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return _safe_request(requests.get, path, headers=headers, params=params, timeout=60)


def api_post(path, json=None, token=None, files=None, data=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return _safe_request(requests.post, path, headers=headers, json=json, files=files, data=data, timeout=120)


def api_multipart(path, files, data, token):
    return _safe_request(
        requests.post, path,
        headers={"Authorization": f"Bearer {token}"}, files=files, data=data, timeout=300
    )


def get_plotly_layout():
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#9CA3AF", "family": "Inter"},
        "xaxis": {
            "gridcolor": "rgba(255,255,255,0.06)",
            "zerolinecolor": "rgba(255,255,255,0.06)",
            "linecolor": "rgba(255,255,255,0.08)",
            "tickfont": {"color": "#9CA3AF"},
            "titlefont": {"color": "#9CA3AF"},
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,0.06)",
            "zerolinecolor": "rgba(255,255,255,0.06)",
            "linecolor": "rgba(255,255,255,0.08)",
            "tickfont": {"color": "#9CA3AF"},
            "titlefont": {"color": "#9CA3AF"},
        },
        "legend": {
            "bgcolor": "rgba(22,26,34,0.9)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "font": {"color": "#E5E7EB"},
        },
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    }


def dashboard_page():
    inject_corporate_css()
    page_header("Overview", "Real-time recruitment metrics")

    token = st.session_state["token"]
    r = api_get("/api/stats/dashboard", token=token)
    if r.status_code != 200:
        st.error(safe_error(r, "Failed to load stats"))
        return
    stats = r.json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Job Openings", stats.get("total_jds", 0), "accent")
    with col2:
        render_metric_card("Resumes Processed", stats.get("total_resumes", 0), "default")
    with col3:
        render_metric_card("Evaluations", stats.get("total_evaluations", 0), "default")
    with col4:
        avg_score = stats.get("avg_score", 0)
        variant = "success" if avg_score >= 70 else "warning" if avg_score >= 40 else "danger"
        render_metric_card("Avg Match Score", f"{avg_score}%", variant)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if stats.get("verdict_counts"):
            df_v = pd.DataFrame([{"Verdict": k, "Count": v} for k, v in stats["verdict_counts"].items()])
            fig = px.pie(
                df_v, names="Verdict", values="Count", color="Verdict",
                color_discrete_map={"High": "#10B981", "Medium": "#F59E0B", "Low": "#EF4444"},
                hole=0.55
            )
            fig.update_layout(get_plotly_layout())
            fig.update_traces(
                textinfo="percent+label",
                textfont={"size": 13, "color": "#E5E7EB", "family": "Inter"},
                marker=dict(line=dict(color="#0d1117", width=2))
            )
            st.markdown("<h3 style='margin-bottom:1rem;'>Fit Distribution</h3>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with chart_col2:
        if stats.get("by_jd"):
            df_jd = pd.DataFrame(stats["by_jd"])
            fig = px.bar(
                df_jd, x="jd_title", y="avg_score", color="jd_title",
                text="count",
                color_discrete_sequence=["#6366F1", "#22D3EE", "#A78BFA", "#34D399", "#F472B6", "#FBBF24"]
            )
            fig.update_layout(get_plotly_layout())
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Avg Score")
            fig.update_traces(
                texttemplate="%{text}",
                textposition="outside",
                textfont={"size": 11, "color": "#9CA3AF"},
                marker_line_width=0,
            )
            st.markdown("<h3 style='margin-bottom:1rem;'>Scores by Job Role</h3>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if stats.get("location_distribution"):
        df_loc = pd.DataFrame([{"Location": k, "Resumes": v} for k, v in stats["location_distribution"].items()])
        fig = px.bar(
            df_loc, x="Location", y="Resumes", color="Location",
            color_discrete_sequence=["#312E81", "#4338CA", "#6366F1", "#818CF8", "#A5B4FC", "#C7D2FE"]
        )
        fig.update_layout(get_plotly_layout())
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Resumes")
        fig.update_traces(marker_line_width=0)
        st.markdown("<h3 style='margin:2rem 0 1rem;'>Resumes by Location</h3>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def jds_page():
    page_header("Job Openings", "Create and manage job descriptions")

    token = st.session_state["token"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>New Job Opening</h3>", unsafe_allow_html=True)

    with st.form("create_jd"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Role Title", placeholder="Senior Python Developer")
            company = st.text_input("Company", placeholder="Acme Corp")
        with col2:
            location = st.selectbox("Location", ["Any Location", "Hyderabad", "Bangalore", "Pune", "Delhi NCR", "Mumbai", "Chennai", "Remote"])

        jd_text = st.text_area("Job Description", height=200, placeholder="Paste the full job description...")

        if st.form_submit_button("Save Job Opening", use_container_width=True):
            if not title or not jd_text:
                st.warning("Title and description are required")
            else:
                r = api_post("/api/jds", json={
                    "title": title, "company": company,
                    "location": None if location == "Any Location" else location, "raw_text": jd_text,
                }, token=token)
                if r.status_code == 200:
                    st.success(f"Created: {r.json()['structured_fields'].get('title')}")
                    st.rerun()
                else:
                    st.error(safe_error(r, "Failed to create"))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("<h3>All Openings</h3>", unsafe_allow_html=True)

    r = api_get("/api/jds", token=token)
    if r.status_code == 200:
        jds = r.json()
        if not jds:
            st.markdown('<div class="card" style="text-align:center; padding:3rem;"><p style="color:var(--text-secondary);">No job openings yet</p></div>', unsafe_allow_html=True)

        current_user_id = str(st.session_state.get("user", {}).get("id", ""))
        for jd in jds:
            header = f"{jd.get('title', 'Untitled')} — {jd.get('company') or 'N/A'} ({jd.get('location') or 'Any'})"
            with st.expander(header):
                sf = jd.get("structured_fields") or {}
                min_exp = jd.get("min_experience")
                max_exp = jd.get("max_experience")
                if min_exp is None and max_exp is None:
                    exp_display = "Not specified"
                elif max_exp is None:
                    exp_display = f"{min_exp}+ years"
                else:
                    exp_display = f"{min_exp} – {max_exp} years"

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Experience:** {exp_display}")
                with col2:
                    st.markdown(f"**Candidates:** {jd.get('candidate_count', 0)}")
                skills = sf.get("required_skills", [])
                if skills:
                    st.markdown(f"**Skills:** {render_skill_tags(skills)}", unsafe_allow_html=True)
                certs = sf.get("required_certs", [])
                if certs:
                    st.markdown(f"**Certifications:** {render_skill_tags(certs)}", unsafe_allow_html=True)

                can_delete = role_can_manage_jd(jd, current_user_id)
                if can_delete:
                    st.markdown('<div class="section-divider" style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                    del_key = f"confirm_delete_jd_{jd['id']}"
                    if not st.session_state.get(del_key):
                        if st.button("Delete Job Opening", key=f"del_jd_{jd['id']}", type="secondary"):
                            st.session_state[del_key] = True
                            st.rerun()
                    else:
                        st.warning("Delete this job opening? This cannot be undone.")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Confirm Delete", key=f"confirm_del_jd_{jd['id']}", type="primary", use_container_width=True):
                                r2 = _safe_request(requests.delete, f"/api/jds/{jd['id']}",
                                                    headers={"Authorization": f"Bearer {token}"})
                                if r2.status_code == 200:
                                    st.session_state.pop(del_key, None)
                                    st.success("Job opening deleted")
                                    st.rerun()
                                else:
                                    st.error(safe_error(r2, "Failed to delete job opening"))
                        with c2:
                            if st.button("Cancel", key=f"cancel_del_jd_{jd['id']}", type="secondary", use_container_width=True):
                                st.session_state.pop(del_key, None)
                                st.rerun()


def fetch_jd_options(token):
    """Fetch job openings as an ordered {label: jd_id} dict for dropdowns."""
    r = api_get("/api/jds", token=token)
    jds = r.json() if r.status_code == 200 else []
    jd_options = {}
    for jd in jds:
        jd_id = jd.get("id")
        if jd_id is None:
            continue
        label = f"{jd.get('title', 'Untitled')} ({jd.get('location') or 'Any'})"
        jd_options[label] = jd_id
    return jd_options


def upload_page():
    page_header("Resume Intake", "Upload and evaluate candidate resumes")

    token = st.session_state["token"]
    jd_options = fetch_jd_options(token)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Evaluation Context</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_jd = st.selectbox("Target Job Opening", ["All JDs"] + list(jd_options.keys()))
    with col2:
        location = st.selectbox("Candidate Location", ["Any Location", "Hyderabad", "Bangalore", "Pune", "Delhi NCR", "Mumbai", "Chennai", "Remote"])

    candidate_name = st.text_input("Candidate Name", placeholder="Auto-extracted from resume")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Upload Resume</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-secondary);'>PDF or DOCX</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["pdf", "docx", "doc"], label_visibility="collapsed")

    if uploaded:
        st.markdown(f'<div style="background:var(--accent-soft);border:1px solid rgba(99,102,241,0.3);border-radius:var(--radius-md);padding:0.75rem 1rem;margin:1rem 0;"><span style="color:var(--accent-hover);font-weight:500;">{uploaded.name}</span> <span style="color:var(--text-secondary);margin-left:1rem;">{uploaded.size / 1024:.1f} KB</span></div>', unsafe_allow_html=True)

    if uploaded and st.button("Run Evaluation", use_container_width=True):
        with st.spinner("Parsing and scoring resume..."):
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
            data = {}
            if selected_jd != "All JDs":
                data["jd_id"] = jd_options[selected_jd]
            if candidate_name:
                data["candidate_name"] = candidate_name
            if location != "Any Location":
                data["location"] = location
            r = api_multipart("/api/resumes/upload", files, data, token)
            if r.status_code == 200:
                evals = r.json()
                st.success(f"{len(evals)} evaluation(s) generated")
                for e in evals:
                    verdict_class = "verdict-high" if e['fit_verdict'] == "High" else "verdict-medium" if e['fit_verdict'] == "Medium" else "verdict-low"
                    st.markdown(f"""
                    <div class="card">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                            <div style="font-size:2rem;font-weight:700;">{e['relevance_score']}<span style="font-size:1rem;color:var(--text-secondary);margin-left:0.5rem;">/ 100</span></div>
                            <span class="verdict-badge {verdict_class}">{e['fit_verdict']}</span>
                        </div>
                        <div style="display:flex;gap:1.5rem;margin-top:0.75rem;flex-wrap:wrap;font-size:0.813rem;color:var(--text-secondary);">
                            <span>Keyword: <strong style="color:var(--text-primary);">{e['keyword_score']}</strong></span>
                            <span>Semantic: <strong style="color:var(--text-primary);">{e['semantic_score']}</strong></span>
                            <span>Experience: <strong style="color:var(--text-primary);">{e['experience_score']}</strong></span>
                            <span>Certification: <strong style="color:var(--text-primary);">{e['certification_score']}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(safe_error(r, "Evaluation failed"))
    st.markdown('</div>', unsafe_allow_html=True)


def results_page():
    page_header("Candidate Evaluations", "Filter, compare, and review candidate analytics")

    token = st.session_state["token"]

    jd_options = fetch_jd_options(token)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Filters</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_jd = st.selectbox("Job Opening", ["All Job Openings"] + list(jd_options.keys()))
    with col2:
        verdict = st.selectbox("Verdict", ["All Verdicts", "High", "Medium", "Low"])
    with col3:
        min_score = st.number_input("Min Score", min_value=0, max_value=100, value=0)
    with col4:
        location = st.selectbox("Location", ["All Locations", "Hyderabad", "Bangalore", "Pune", "Delhi NCR", "Mumbai", "Chennai", "Remote"])
    st.markdown('</div>', unsafe_allow_html=True)

    params = {}
    if selected_jd != "All Job Openings":
        params["jd_id"] = jd_options[selected_jd]
    if verdict != "All Verdicts":
        params["verdict"] = verdict
    if min_score > 0:
        params["min_score"] = min_score
    if location != "All Locations":
        params["location"] = location

    r = api_get("/api/evaluations", token=token, params=params)
    if r.status_code != 200:
        st.error("Failed to load evaluations")
        return
    evals = r.json()

    if not evals:
        st.markdown('<div class="card" style="text-align:center;padding:3rem;"><p style="color:var(--text-secondary);">No evaluations match the current filters</p></div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame([{
        "ID": str(e["id"])[:8],
        "Score": e["relevance_score"],
        "Verdict": e["fit_verdict"],
        "Keyword": e["keyword_score"],
        "Semantic": e["semantic_score"],
        "Exp": e["experience_score"],
        "Cert": e["certification_score"],
    } for e in evals])

    eval_ids = {str(e["id"])[:8]: e["id"] for e in evals}
    df_sorted = df.sort_values("Score", ascending=False)

    st.dataframe(
        df_sorted[["ID", "Score", "Verdict", "Keyword", "Semantic", "Exp", "Cert"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d")
        }
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("<h3>Detailed View</h3>", unsafe_allow_html=True)

    sel_id_short = st.selectbox(
        "Select evaluation",
        df_sorted["ID"].tolist(),
        format_func=lambda x: f"{x} — Score: {df_sorted[df_sorted['ID']==x]['Score'].values[0]}"
    )

    if sel_id_short:
        eid = eval_ids.get(sel_id_short)
        if eid:
            r = api_get(f"/api/evaluations/{eid}", token=token)
            if r.status_code == 200:
                d = r.json()

                st.markdown('<div class="card">', unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"<strong>Candidate:</strong> {d.get('candidate_name', 'N/A')} &nbsp;·&nbsp; {d.get('candidate_email', 'N/A')}", unsafe_allow_html=True)
                    st.markdown(f"<strong>Role:</strong> {d.get('jd_title', 'N/A')} — {d.get('jd_location') or 'N/A'} &nbsp;·&nbsp; Location: {d.get('resume_location', 'N/A')}", unsafe_allow_html=True)
                    verdict_badge = render_verdict_badge(d.get('fit_verdict', 'Low'))
                    st.markdown(f"<strong>Score:</strong> <span style='font-size:1.5rem;font-weight:700;color:var(--accent-primary);'>{d.get('relevance_score', 0)}</span>/100&nbsp;&nbsp;{verdict_badge}", unsafe_allow_html=True)
                with col2:
                    bd = d.get("score_breakdown") or {}
                    if bd:
                        bdf = pd.DataFrame([{"Component": k.replace("_", " ").title(), "Score": v} for k, v in bd.items()])
                        fig = px.bar(bdf, x="Component", y="Score", color="Component",
                                     color_discrete_sequence=["#6366F1", "#818CF8", "#A78BFA", "#8B5CF6"])
                        fig.update_layout(get_plotly_layout())
                        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Score", height=280,
                                         margin=dict(l=20, r=20, t=10, b=40))
                        fig.update_traces(marker_line_width=0)
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                gap_col1, gap_col2, gap_col3 = st.columns(3)
                with gap_col1:
                    st.markdown("<strong>Missing Skills</strong>", unsafe_allow_html=True)
                    skills = d.get("missing_skills") or []
                    st.markdown(render_skill_tags(skills) if skills else '<span style="color:var(--text-tertiary);">None</span>', unsafe_allow_html=True)
                with gap_col2:
                    st.markdown("<strong>Missing Certifications</strong>", unsafe_allow_html=True)
                    certs = d.get("missing_certs") or []
                    st.markdown(render_skill_tags(certs) if certs else '<span style="color:var(--text-tertiary);">None</span>', unsafe_allow_html=True)
                with gap_col3:
                    st.markdown("<strong>Missing Project Types</strong>", unsafe_allow_html=True)
                    projects = d.get("missing_projects") or []
                    st.markdown(render_skill_tags(projects) if projects else '<span style="color:var(--text-tertiary);">None</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("<strong>Feedback for Candidate</strong>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:var(--text-secondary);line-height:1.7;white-space:pre-wrap;'>{d.get('feedback_text', 'No feedback available')}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

def admin_users_page():
    page_header("Manage Users", "View and update roles across the organization")
    token = st.session_state["token"]
    current_user_id = str(st.session_state.get("user", {}).get("id", ""))
    r = api_get("/api/admin/users", token=token)
    if r.status_code != 200:
        st.error(safe_error(r, "Failed to load users"))
        return
    users = r.json()
    for u in users:
        is_self = str(u["id"]) == current_user_id
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            label = f"**{u['name']}** — {u['email']}"
            if is_self:
                label += "  &nbsp;·&nbsp; *(you)*"
            st.markdown(label, unsafe_allow_html=True)
        with col2:
            new_role = st.selectbox("Role", ["recruiter", "admin", "student"],
                                     index=["recruiter", "admin", "student"].index(u["role"]),
                                     key=f"role_{u['id']}", label_visibility="collapsed")
        with col3:
            del_key = f"confirm_delete_user_{u['id']}"
            if is_self:
                st.button("Delete", key=f"del_user_{u['id']}", disabled=True, use_container_width=True)
            elif not st.session_state.get(del_key):
                if st.button("Delete", key=f"del_user_{u['id']}", type="secondary", use_container_width=True):
                    st.session_state[del_key] = True
                    st.rerun()

        if not is_self and st.session_state.get(del_key):
            st.warning(f"Delete **{u['name']}**? This permanently removes their account and cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Confirm Delete", key=f"confirm_del_user_{u['id']}", type="primary", use_container_width=True):
                    r2 = _safe_request(requests.delete, f"/api/admin/users/{u['id']}",
                                        headers={"Authorization": f"Bearer {token}"})
                    if r2.status_code == 200:
                        st.session_state.pop(del_key, None)
                        st.success(f"Deleted {u['name']}")
                        st.rerun()
                    else:
                        st.error(safe_error(r2, "Failed to delete user"))
            with c2:
                if st.button("Cancel", key=f"cancel_del_user_{u['id']}", type="secondary", use_container_width=True):
                    st.session_state.pop(del_key, None)
                    st.rerun()

        if new_role != u["role"]:
            r2 = _safe_request(requests.patch, f"/api/admin/users/{u['id']}",
                                headers={"Authorization": f"Bearer {token}"}, json={"role": new_role})
            if r2.status_code == 200:
                st.success(f"Updated {u['name']} to {new_role}")
                st.rerun()

def student_evaluations_page():
    page_header("My Evaluations", "Your resume results and progress across job openings")
    token = st.session_state["token"]
    r = api_get("/api/evaluations/history/mine", token=token)
    if r.status_code != 200:
        st.error(safe_error(r, "Failed to load evaluations"))
        return
    evals = r.json()
    if not evals:
        st.info("No evaluations yet — upload your resume to get matched against open roles.")
        return

    by_jd = {}
    for e in evals:
        by_jd.setdefault(e["jd_id"], []).append(e)

    for jd_id, items in by_jd.items():
        items = sorted(items, key=lambda x: x["evaluated_at"])
        latest = items[-1]
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f"<h3 style='margin-top:0;'>{latest.get('jd_title') or 'Job Opening'}</h3>", unsafe_allow_html=True)

        if len(items) > 1:
            delta = latest["relevance_score"] - items[0]["relevance_score"]
            df = pd.DataFrame({"Attempt": list(range(1, len(items) + 1)),
                                "Score": [i["relevance_score"] for i in items]})
            fig = px.bar(df, x="Attempt", y="Score", color_discrete_sequence=["#6366F1"])
            fig.update_layout(get_plotly_layout())
            fig.update_layout(height=200, showlegend=False, margin=dict(l=20, r=20, t=10, b=30))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            sign = "+" if delta >= 0 else ""
            color = "var(--success)" if delta >= 0 else "var(--danger)"
            st.markdown(f'<div style="color:{color};font-weight:600;font-size:0.85rem;">{sign}{delta} points across {len(items)} uploads</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:1.5rem;font-weight:700;'>{latest['relevance_score']}/100</div>", unsafe_allow_html=True)

        st.markdown(render_verdict_badge(latest["fit_verdict"]), unsafe_allow_html=True)

        gap_col1, gap_col2, gap_col3 = st.columns(3)
        with gap_col1:
            st.markdown("<strong>Missing Skills</strong>", unsafe_allow_html=True)
            st.markdown(render_skill_tags(latest.get("missing_skills") or []), unsafe_allow_html=True)
        with gap_col2:
            st.markdown("<strong>Missing Certifications</strong>", unsafe_allow_html=True)
            st.markdown(render_skill_tags(latest.get("missing_certs") or []), unsafe_allow_html=True)
        with gap_col3:
            st.markdown("<strong>Missing Project Types</strong>", unsafe_allow_html=True)
            st.markdown(render_skill_tags(latest.get("missing_projects") or []), unsafe_allow_html=True)

        st.markdown('<div class="section-divider" style="margin:1rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("<strong>Feedback for You</strong>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:var(--text-secondary);line-height:1.7;white-space:pre-wrap;'>"
            f"{latest.get('feedback_text') or 'No feedback available yet.'}</div>",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    inject_corporate_css()

    if "token" not in st.session_state:
        login_page()
        return

    user = st.session_state.get("user", {})
    role = user.get("role", "recruiter")

    if role == "admin":
        nav_pages = ["Overview", "Job Openings", "Resume Intake", "Candidate Evaluations", "Manage Users"]
    elif role == "student":
        nav_pages = ["My Evaluations", "Upload Resume"]
    else:
        nav_pages = ["Overview", "Job Openings", "Resume Intake", "Candidate Evaluations"]

    if "_nav_page" not in st.session_state or st.session_state["_nav_page"] >= len(nav_pages):
        st.session_state["_nav_page"] = 0

    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.625rem;padding:1.5rem 1rem 1.25rem;border-bottom:1px solid var(--border-subtle);margin-bottom:0.75rem;">
            {SVG_LOGO}
            <div>
                <div style="font-weight:700;font-size:1.125rem;color:var(--text-primary);">RecruitNeo</div>
                <div style="font-size:0.7rem;color:var(--text-tertiary);">Enterprise</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for i, label in enumerate(nav_pages):
            active = i == st.session_state["_nav_page"]
            if st.button(label, key=f"nav_{i}",
                         use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state["_nav_page"] = i
                st.rerun()

        st.markdown('<div style="border-top:1px solid var(--border-subtle);margin:1rem 0 0.75rem;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="padding:0 0.75rem;margin-bottom:0.5rem;"><div style="color:var(--text-primary);font-weight:500;font-size:0.875rem;">{user.get("name", "User")}</div><div style="color:var(--text-secondary);font-size:0.8rem;text-transform:capitalize;">{user.get("role", "recruiter")}</div></div>', unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True, type="secondary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        page = nav_pages[st.session_state["_nav_page"]]

    if page == "Overview":
        dashboard_page()
    elif page == "Job Openings":
        jds_page()
    elif page == "Resume Intake":
        upload_page()
    elif page == "Candidate Evaluations":
        results_page()
    elif page == "Manage Users":
        admin_users_page()
    elif page == "My Evaluations":
        student_evaluations_page()
    elif page == "Upload Resume":
        upload_page()

    render_footer()


if __name__ == '__main__':
    main()