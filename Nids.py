import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import socket
import ssl
from urllib.parse import urlparse
from datetime import datetime
import os
import time
import json
import re
import random
from dotenv import load_dotenv
from google import genai

# =========================
# PAGE CONFIG
# =========================

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

st.set_page_config(
    page_title="NIDS | Network Security",
    page_icon="🛡️",
    layout="wide"
)


st.markdown("""
<style>
/* =========================
   NIDS DARK DASHBOARD THEME
   ========================= */

.stApp {
    background:
        radial-gradient(circle at 85% 0%, rgba(59,130,246,.08), transparent 28%),
        #0b0f14;
    color: #f5f7fa;
}

.block-container {
    max-width: 1500px;
    padding: 2.2rem 3rem 4rem 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1724 0%, #0b111b 100%);
    border-right: 1px solid #263244;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1rem .75rem 1.2rem .75rem;
}

[data-testid="stSidebar"] .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 12px;
    margin: 2px 4px 18px 4px;
    border-radius: 14px;
    background: linear-gradient(145deg, #172233, #111925);
    border: 1px solid #2a394d;
    box-shadow: 0 10px 28px rgba(0,0,0,.22);
}

[data-testid="stSidebar"] .sidebar-brand-icon {
    font-size: 1.65rem;
    line-height: 1;
}

[data-testid="stSidebar"] .sidebar-brand-title {
    color: #f5f7fa;
    font-size: 1.02rem;
    font-weight: 800;
}

[data-testid="stSidebar"] .sidebar-brand-subtitle {
    color: #7f91a8;
    font-size: .70rem;
    margin-top: 3px;
}

[data-testid="stSidebar"] .sidebar-nav-label {
    color: #708198;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .12em;
    padding: 0 12px 7px;
}

/* Sidebar navigation buttons */
[data-testid="stSidebar"] [data-testid="stButton"] {
    margin: 0 0 5px 0;
}

[data-testid="stSidebar"] [data-testid="stButton"] > button {
    width: 100%;
    min-height: 40px;
    justify-content: flex-start;
    text-align: left;
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid #253247;
    background: #121a26;
    color: #dbe5f2 !important;
    font-size: .88rem;
    font-weight: 600;
    box-shadow: none;
    transition: all .15s ease;
}

[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: #1a2a3f;
    border-color: #3b5d82;
    color: #ffffff !important;
    transform: translateX(2px);
}

/* Streamlit primary button = currently selected page */
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(90deg, #1d3b60, #19304c);
    border-color: #3970a6;
    color: #ffffff !important;
    font-weight: 750;
    box-shadow: inset 3px 0 0 #55a8ff, 0 6px 16px rgba(0,0,0,.18);
}

/* Make the system status a real card */
[data-testid="stSidebar"] .sidebar-system-card {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 22px 4px 0;
    padding: 14px 13px;
    border-radius: 12px;
    background: linear-gradient(135deg, #123c2e, #102f27);
    border: 1px solid #1d694a;
    box-shadow: 0 9px 22px rgba(0,0,0,.20);
}

[data-testid="stSidebar"] .sidebar-system-dot {
    width: 10px;
    height: 10px;
    flex: 0 0 10px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 12px rgba(74,222,128,.65);
}

[data-testid="stSidebar"] .sidebar-system-title {
    color: #eafff3;
    font-size: .87rem;
    font-weight: 750;
}

[data-testid="stSidebar"] .sidebar-system-subtitle {
    color: #86bba5;
    font-size: .68rem;
    margin-top: 4px;
}

/* Typography */
h1 {
    font-size: 2.35rem !important;
    font-weight: 750 !important;
    letter-spacing: -0.035em;
}

h2 {
    font-size: 1.65rem !important;
    font-weight: 700 !important;
}

h3 {
    font-weight: 650 !important;
}

[data-testid="stCaptionContainer"] {
    color: #8f9aaa !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #151b25, #111720);
    border: 1px solid #252e3b;
    border-radius: 14px;
    padding: 16px 18px;
    min-height: 112px;
    box-shadow: 0 8px 24px rgba(0,0,0,.16);
}

[data-testid="stMetricLabel"] {
    color: #9ca8b8 !important;
}

[data-testid="stMetricValue"] {
    color: #f5f7fa !important;
    font-weight: 750 !important;
}

[data-testid="stMetricDelta"] {
    color: #65e6a1 !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    min-height: 42px;
    border-radius: 9px;
    font-weight: 650;
    background: #161d28;
    color: #f5f7fa;
    border: 1px solid #2b3645;
    transition: all .15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #4f9cff;
    color: #ffffff;
    background: #1a2535;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 11px;
    border: 1px solid #2b3645;
}

/* Inputs */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background: #151b25 !important;
    border-color: #2b3645 !important;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    border: 1px solid #252e3b;
    border-radius: 11px;
    overflow: hidden;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #121821;
    border: 1px solid #252e3b;
    border-radius: 11px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #121821;
    border: 1px dashed #344154;
    border-radius: 12px;
    padding: 10px;
}

/* Dashboard custom cards */
.nids-hero {
    background: linear-gradient(135deg, #121a27 0%, #10151e 60%, #111c2c 100%);
    border: 1px solid #263244;
    border-radius: 18px;
    padding: 28px 30px;
    margin: 4px 0 24px 0;
    box-shadow: 0 16px 45px rgba(0,0,0,.22);
}

.nids-hero-title {
    font-size: 2rem;
    font-weight: 780;
    margin-bottom: 7px;
}

.nids-hero-subtitle {
    color: #98a4b5;
    font-size: 1rem;
    line-height: 1.55;
}

.nids-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #123b2d;
    color: #69e6a6;
    border: 1px solid #1c6849;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: .86rem;
    font-weight: 700;
    margin-top: 16px;
}

.nids-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 10px rgba(74,222,128,.7);
}

.nids-card {
    background: linear-gradient(145deg, #151b25, #111720);
    border: 1px solid #252e3b;
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    box-shadow: 0 8px 25px rgba(0,0,0,.14);
}

.nids-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 7px;
}

.nids-card-text {
    color: #8f9aaa;
    line-height: 1.5;
    font-size: .91rem;
}

.nids-chip {
    display: inline-block;
    padding: 5px 9px;
    margin: 3px 4px 3px 0;
    border-radius: 7px;
    background: #1a2230;
    border: 1px solid #293547;
    color: #cbd5e1;
    font-size: .82rem;
}

.nids-section {
    margin: 28px 0 12px 0;
}

.nids-pipeline {
    display: flex;
    align-items: stretch;
    gap: 10px;
}

.nids-step {
    flex: 1;
    background: #121821;
    border: 1px solid #252e3b;
    border-radius: 13px;
    padding: 18px;
}

.nids-step-number {
    color: #63a4ff;
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .08em;
}

.nids-step-title {
    font-weight: 700;
    margin: 6px 0;
}

.nids-step-text {
    color: #8f9aaa;
    font-size: .88rem;
    line-height: 1.45;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .nids-pipeline {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)

model = joblib.load("random_forest_model.joblib.pkl")
protocol_encoder = joblib.load("protocol_encoder.pkl")
flag_encoder = joblib.load("flag_encoder.pkl")
service_encoder = joblib.load("service_encoder.pkl")


if "history" not in st.session_state:
    st.session_state.history = []

if "gemini_generated_history" not in st.session_state:
    st.session_state.gemini_generated_history = []

#=========================
# SIDEBAR
# =========================

st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-icon">🛡️</div>
    <div>
        <div class="sidebar-brand-title">Network Security</div>
        <div class="sidebar-brand-subtitle">Intrusion Detection System</div>
    </div>
</div>
<div class="sidebar-nav-label">NAVIGATION</div>
""", unsafe_allow_html=True)

nav_items = [
    "🏠 Dashboard",
    "🔍 Analyze Traffic",
    "🧪 Try Demo",
    "🤖 AI Traffic Generator",
    "📡 Live Traffic",
    "🌐 Website Security & Health",
    "📊 Analytics",
    "🕘 Prediction History",
    "📄 Reports",
    "ℹ️ About Project"
]

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

for nav_item in nav_items:
    nav_key = "nav_" + re.sub(r"[^a-zA-Z0-9]+", "_", nav_item).strip("_")
    if st.sidebar.button(
        nav_item,
        key=nav_key,
        use_container_width=True,
        type="primary" if st.session_state.page == nav_item else "secondary"
    ):
        st.session_state.page = nav_item
        st.rerun()

page = st.session_state.page

st.sidebar.markdown("""
<div class="sidebar-system-card">
    <div class="sidebar-system-dot"></div>
    <div>
        <div class="sidebar-system-title">Detection System Ready</div>
        <div class="sidebar-system-subtitle">Random Forest • 15 Network Features</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================
# DASHBOARD
# =========================
# =========================
# SHARED DEMO TRAFFIC DATA
# Used by Demo Mode and Live Traffic
# =========================

demo_data = {

"🟢 Normal Traffic": {
    "protocol": "tcp",
    "service": "ftp_data",
    "flag": "SF",
    "duration": 0,
    "src_bytes": 491,
    "dst_bytes": 0,
    "logged_in": "No",
    "count": 2,
    "same_srv_rate": 1.0,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "dst_host_diff_srv_rate": 0.03,
    "dst_host_same_src_port_rate": 0.17,
    "dst_host_srv_diff_host_rate": 0.0,
    "dst_host_srv_count": 25
},

"🔴 DoS Attack": {
    "protocol": "tcp",
    "service": "private",
    "flag": "S0",
    "duration": 0,
    "src_bytes": 0,
    "dst_bytes": 0,
    "logged_in": "No",
    "count": 123,
    "same_srv_rate": 0.05,
    "serror_rate": 1.0,
    "srv_serror_rate": 1.0,
    "dst_host_diff_srv_rate": 0.05,
    "dst_host_same_src_port_rate": 0.0,
    "dst_host_srv_diff_host_rate": 0.0,
    "dst_host_srv_count": 26
},

"🟠 Probe Attack": {
    "protocol": "icmp",
    "service": "eco_i",
    "flag": "SF",
    "duration": 0,
    "src_bytes": 18,
    "dst_bytes": 0,
    "logged_in": "No",
    "count": 1,
    "same_srv_rate": 1.0,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "dst_host_diff_srv_rate": 0.0,
    "dst_host_same_src_port_rate": 1.0,
    "dst_host_srv_diff_host_rate": 1.0,
    "dst_host_srv_count": 16
},

"🔴 R2L Attack": {
    "protocol": "tcp",
    "service": "ftp_data",
    "flag": "SF",
    "duration": 0,
    "src_bytes": 334,
    "dst_bytes": 0,
    "logged_in": "Yes",
    "count": 2,
    "same_srv_rate": 1.0,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "dst_host_diff_srv_rate": 0.0,
    "dst_host_same_src_port_rate": 1.0,
    "dst_host_srv_diff_host_rate": 0.2,
    "dst_host_srv_count": 20
},

"🟣 U2R Attack": {
    "protocol": "tcp",
    "service": "ftp_data",
    "flag": "SF",
    "duration": 0,
    "src_bytes": 0,
    "dst_bytes": 5696,
    "logged_in": "Yes",
    "count": 1,
    "same_srv_rate": 1.0,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "dst_host_diff_srv_rate": 0.0,
    "dst_host_same_src_port_rate": 1.0,
    "dst_host_srv_diff_host_rate": 0.02,
    "dst_host_srv_count": 81
}
}

if page=="🏠 Dashboard":
    st.markdown("""
    <div class="nids-hero">
        <div class="nids-hero-title">🛡️ Network Intrusion Detection System</div>
        <div class="nids-hero-subtitle">
            AI-assisted network traffic analysis powered by a trained Random Forest
            model. Analyze traffic, test scenarios, inspect predictions, and review
            detection history from one dashboard.
        </div>
        <div class="nids-status">
            <span class="nids-dot"></span>
            Detection System Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # STATUS CARDS
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("System Status", "Ready", "Detection Online")

    with col2:
        st.metric("Detection Model", "Random Forest", "15 Features")

    with col3:
        st.metric("Model Accuracy", "99.81%", "Validated Performance")

    with col4:
        st.metric("Detection Classes", "5", "Normal + 4 Attacks")

    st.markdown('<div class="nids-section"></div>', unsafe_allow_html=True)

    # =========================
    # QUICK ACTIONS
    # =========================
    st.subheader("🚀 Quick Actions")
    st.caption("Choose the workflow you want to demonstrate.")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.markdown("""
        <div class="nids-card">
            <div class="nids-card-title">🔍 Analyze Traffic</div>
            <div class="nids-card-text">
                Enter network traffic values and let the trained model classify
                the activity with a confidence score.
            </div>
            <br>
            <span class="nids-chip">Manual Input</span>
            <span class="nids-chip">15 Features</span>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown("""
        <div class="nids-card">
            <div class="nids-card-title">🧪 Try Demo</div>
            <div class="nids-card-text">
                Use prepared examples for Normal, DoS, Probe, R2L and U2R
                traffic without entering values manually.
            </div>
            <br>
            <span class="nids-chip">Fast Demo</span>
            <span class="nids-chip">5 Classes</span>
        </div>
        """, unsafe_allow_html=True)

    with a3:
        st.markdown("""
        <div class="nids-card">
            <div class="nids-card-title">🤖 AI Traffic Generator</div>
            <div class="nids-card-text">
                Gemini creates a synthetic scenario and 15 traffic features,
                then Random Forest independently predicts the generated traffic.
            </div>
            <br>
            <span class="nids-chip">Gemini</span>
            <span class="nids-chip">RF Comparison</span>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # DETECTION CLASSES
    # =========================
    st.markdown('<div class="nids-section"></div>', unsafe_allow_html=True)
    st.subheader("🎯 Detection Classes")
    st.caption("Traffic categories recognized by the trained model.")

    c1, c2, c3, c4, c5 = st.columns(5)

    class_cards = [
        ("🟢", "Normal", "Regular network activity"),
        ("🔴", "DoS", "Availability-disruption pattern"),
        ("🟠", "Probe", "Scanning / discovery pattern"),
        ("🔴", "R2L", "Remote-to-local activity"),
        ("🟣", "U2R", "Privilege-escalation pattern"),
    ]

    for col, (icon, name, desc) in zip(
        [c1, c2, c3, c4, c5],
        class_cards
    ):
        with col:
            st.markdown(
                f"""
                <div class="nids-card">
                    <div style="font-size:1.45rem">{icon}</div>
                    <div class="nids-card-title">{name}</div>
                    <div class="nids-card-text">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # HOW IT WORKS
    # =========================
    st.markdown('<div class="nids-section"></div>', unsafe_allow_html=True)
    st.subheader("⚙️ How Detection Works")
    st.caption("The main processing flow of the NIDS.")

    st.markdown("""
    <div class="nids-pipeline">
        <div class="nids-step">
            <div class="nids-step-number">STEP 01</div>
            <div class="nids-step-title">Traffic Input</div>
            <div class="nids-step-text">
                Network traffic is represented using 15 measurable features.
            </div>
        </div>
        <div class="nids-step">
            <div class="nids-step-number">STEP 02</div>
            <div class="nids-step-title">Feature Processing</div>
            <div class="nids-step-text">
                Categorical values are converted using the same encoders used
                during model training.
            </div>
        </div>
        <div class="nids-step">
            <div class="nids-step-number">STEP 03</div>
            <div class="nids-step-title">Random Forest</div>
            <div class="nids-step-text">
                The trained classifier analyzes the 15-feature traffic record.
            </div>
        </div>
        <div class="nids-step">
            <div class="nids-step-number">STEP 04</div>
            <div class="nids-step-title">Detection Result</div>
            <div class="nids-step-text">
                The system displays the predicted class and model confidence.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nids-section"></div>', unsafe_allow_html=True)
    st.success(
        "🟢 System ready — for the quickest presentation, open **Try Demo** "
        "or **AI Traffic Generator**."
    )

if page=="🔍 Analyze Traffic":
    st.title("🔍 Analyze Network Traffic")
    st.caption("Enter the connection details below"
               "The system will analyze them and provide a simple result")
    st.markdown("---")
    st.info( "💡 You don't need cybersecurity knowledge. "
        "Enter the available traffic information and click Analyze."
    )
    # =========================
    # TRAFFIC DETAILS
    # =========================

    st.subheader("📥 Traffic Details")
    col1,col2=st.columns(2)
    with col1:
        protocol_type=st.selectbox(
            "🌐 Protocol",
            protocol_encoder.classes_,
            help="The communcation protocol used by the connection"
        )

        service=st.selectbox(
            "🛠️ Service",
            service_encoder.classes_,
            help="The network service used by the connection"
        )
        flag=st.selectbox(  "🔗 Connection Status",
            flag_encoder.classes_,
            help="Status of the network connection."
        )
        duration = st.slider(
    "⏱️ Connection Time (Seconds)",
    min_value=0,
    max_value=100,
    value=0,
    step=1
)

        src_bytes = st.number_input(
            "📤 Data Sent (Bytes)",
            min_value=0,
            value=0
        )

        dst_bytes = st.number_input(
            "📥 Data Received (Bytes)",
            min_value=0,
            value=0
        )

        logged_in = st.selectbox(
            "🔐 Login Successful?",
            ["No", "Yes"]
        )

        count = st.slider(
    "🔄 Recent Connections",
    min_value=0,
    max_value=500,
    value=0,
    step=1
)
    with col2:
         same_srv_rate = st.slider(
    "📊 Same Service Usage",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Higher values mean most connections use the same service."
)

         serror_rate = st.slider(
    "⚠️ Connection Error Rate",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Connection error rate between 0 and 1."
)

         srv_serror_rate = st.slider(
    "⚠️ Service Error Rate",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Service error rate between 0 and 1."
)

         dst_host_diff_srv_rate = st.slider(
    "🌐 Different Service Usage",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Percentage of different services contacted."
)

         dst_host_same_src_port_rate = st.slider(
    "🔌 Same Port Usage",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Usage rate of the same source port."
)

         dst_host_srv_diff_host_rate = st.slider(
    "🖥️ Different Host Usage",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.01,
    help="Rate of connections to different hosts."
)

         dst_host_srv_count = st.slider(
    "📡 Services Used by Destination",
    min_value=0,
    max_value=255,
    value=0,
    step=1
)

    st.markdown("---")

    # =========================
    # ANALYZE BUTTON
    # =========================
    if st.button("🛡️ Analyze Traffic",use_container_width=True):
        protocol = protocol_encoder.transform(
            [protocol_type]
        )[0]

        service_name = service_encoder.transform(
            [service]
        )[0]

        flag_name = flag_encoder.transform(
            [flag]
        )[0]

        logged_in_value = 1 if logged_in == "Yes" else 0

        input_data = np.array([[
            duration,
            protocol,
            service_name,
            flag_name,
            src_bytes,
            dst_bytes,
            logged_in_value,
            count,
            same_srv_rate,
            serror_rate,
            srv_serror_rate,
            dst_host_diff_srv_rate,
            dst_host_same_src_port_rate,
            dst_host_srv_diff_host_rate,
            dst_host_srv_count
        ]])

        with st.spinner("🔍 Analyzing network traffic..."):
            # Keep the loading state visible for a short, consistent demo delay.
            time.sleep(3)
            prediction = model.predict(input_data)[0]
            confidence = model.predict_proba(input_data).max() * 100

        class_names = {
            0: "Normal",
            1: "DoS",
            2: "R2L",
            3: "Probe",
            4: "U2R"
        }

        result = class_names[prediction]

        # =========================
        # RESULT
        # =========================

        st.markdown("---")
        st.subheader("🛡️ Detection Result")

        if result == "Normal":
            st.success(f"## 🟢 Network Traffic is Normal\n\nNo suspicious activity was detected in this traffic.\n\n**Confidence:** {confidence:.2f}%")
            risk = "Low"
        elif result == "Probe":
            st.warning(f"## 🟠 Suspicious Activity Detected\n\n**Attack Type:** Probe\n\nThe traffic may indicate scanning or information-gathering activity.\n\n**Confidence:** {confidence:.2f}%")
            risk = "Medium"
        else:
            st.error(f"## 🚨 Intrusion Detected\n\n**Attack Type:** {result}\n\nThe traffic pattern shows characteristics associated with malicious activity.\n\n**Confidence:** {confidence:.2f}%")
            risk = "High"

        explanations = {
            "Normal": "The traffic pattern appears similar to normal network activity.",
            "DoS": "The traffic may indicate an attempt to overwhelm a system with excessive requests.",
            "Probe": "The traffic may indicate scanning or information-gathering activity.",
            "R2L": "The traffic may indicate an attempt to gain local access from a remote system.",
            "U2R": "The traffic may indicate an attempt to gain higher system privileges."
        }
        st.info(f"### 📖 What does this mean?\n\n{explanations[result]}")

        recommendations = {
            "Normal": "No immediate action is required.",
            "DoS": "Review incoming traffic and consider blocking suspicious sources.",
            "Probe": "Review network scans and investigate unusual connection attempts.",
            "R2L": "Review authentication activity and unauthorized login attempts.",
            "U2R": "Review user privileges and investigate possible privilege escalation."
        }
        st.info(f"### 💡 Recommended Action\n\n{recommendations[result]}")

        st.session_state.history.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Prediction": result,
            "Risk": risk,
            "Confidence": f"{confidence:.2f}%",
            "Source": "Manual"
        })

# =========================
# DEMO MODE
# =========================

if page == "🧪 Try Demo":

    st.title("🧪 Try the Detection Demo")
    st.caption("Choose a ready-made traffic scenario and see how the AI responds.")
    st.info("💡 No technical knowledge required. Select a scenario and click Analyze.")

    scenario = st.selectbox("Choose a traffic scenario", [
        "🟢 Normal Traffic",
        "🔴 DoS Attack",
        "🟠 Probe Attack",
        "🔴 R2L Attack",
        "🟣 U2R Attack"
    ])

    selected = demo_data[scenario]

    st.markdown("---")
    st.subheader("📋 Selected Traffic Scenario")

    st.caption(
        "These values are automatically provided by the selected demo. "
        "No manual entry is required."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌐 Connection")

        st.write(f"**Protocol:** `{selected['protocol']}`")
        st.write(f"**Service:** `{selected['service']}`")
        st.write(f"**Connection Status:** `{selected['flag']}`")
        st.write(f"**Connection Time:** `{selected['duration']} sec`")

        st.markdown("### 📡 Data Transfer")

        st.write(f"**Data Sent:** `{selected['src_bytes']} bytes`")
        st.write(f"**Data Received:** `{selected['dst_bytes']} bytes`")

    with col2:
        st.markdown("### 🔐 Connection Behaviour")

        st.write(f"**Login Successful:** `{selected['logged_in']}`")
        st.write(f"**Recent Connections:** `{selected['count']}`")
        st.write(f"**Same Service Usage:** `{selected['same_srv_rate']}`")
        st.write(f"**Connection Error Rate:** `{selected['serror_rate']}`")
        st.write(f"**Service Error Rate:** `{selected['srv_serror_rate']}`")

        st.markdown("### 🌍 Host Behaviour")

        st.write(
            f"**Different Service Usage:** "
            f"`{selected['dst_host_diff_srv_rate']}`"
        )
        st.write(
            f"**Same Port Usage:** "
            f"`{selected['dst_host_same_src_port_rate']}`"
        )
        st.write(
            f"**Different Host Usage:** "
            f"`{selected['dst_host_srv_diff_host_rate']}`"
        )
        st.write(
            f"**Destination Services:** "
            f"`{selected['dst_host_srv_count']}`"
        )

    st.markdown("---")

    st.info(
        "💡 The selected scenario automatically supplies all 15 "
        "network features to the trained Random Forest model."
    )

    if st.button("🛡️ Analyze This Example", use_container_width=True):
        protocol = protocol_encoder.transform([selected["protocol"]])[0]
        service_name = service_encoder.transform([selected["service"]])[0]
        flag_name = flag_encoder.transform([selected["flag"]])[0]
        logged_in_value = 1 if selected["logged_in"] == "Yes" else 0
        input_data = np.array([[selected["duration"], protocol, service_name, flag_name, selected["src_bytes"], selected["dst_bytes"], logged_in_value, selected["count"], selected["same_srv_rate"], selected["serror_rate"], selected["srv_serror_rate"], selected["dst_host_diff_srv_rate"], selected["dst_host_same_src_port_rate"], selected["dst_host_srv_diff_host_rate"], selected["dst_host_srv_count"]]])
        prediction = model.predict(input_data)[0]
        confidence = model.predict_proba(input_data).max() * 100
        class_names = {0:"Normal",1:"DoS",2:"R2L",3:"Probe",4:"U2R"}
        result = class_names[prediction]
        st.markdown("---")
        if result == "Normal":
            st.success(f"## 🟢 Normal Traffic\n\nNo suspicious activity detected.\n\n**Confidence:** {confidence:.2f}%")
        else:
            st.error(f"## 🚨 Intrusion Detected\n\n**Attack Type:** {result}\n\n**Confidence:** {confidence:.2f}%")
        st.info("This demonstration uses predefined network traffic examples and the same trained Random Forest model.")

        # Save Demo prediction so it appears in Analytics / History
        if result == "Normal":
            demo_risk = "Low"
        elif result == "Probe":
            demo_risk = "Medium"
        else:
            demo_risk = "High"

        st.session_state.history.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Prediction": result,
            "Risk": demo_risk,
            "Confidence": f"{confidence:.2f}%",
            "Source": "Demo"
        })



# =========================
# LIVE TRAFFIC MONITOR
# =========================


# =========================
# AI TRAFFIC GENERATOR
# =========================

if "gemini_generated_history" not in st.session_state:
    st.session_state.gemini_generated_history = []

if page == "🤖 AI Traffic Generator":

    st.title("🤖 AI Traffic Scenario Generator")
    st.caption(
        "Gemini generates the traffic scenario AND the 15 model features. "
        "Random Forest independently classifies those generated features."
    )

    st.info(
        "🔬 No predefined attack template is used here. Gemini receives only "
        "the feature definitions and valid categorical values, then generates "
        "a complete synthetic traffic record."
    )

    if gemini_client is None:
        st.error(
            "Gemini API key not found. Add GEMINI_API_KEY to your .env file "
            "and restart Streamlit."
        )
    else:

        if st.button(
            "🤖 Generate Traffic Scenario",
            use_container_width=True
        ):

            feature_definitions = {
                "duration": "Connection duration in seconds. Non-negative integer.",
                "protocol": "Network protocol used by the connection.",
                "service": "Destination network service.",
                "flag": "Connection status/flag from the network connection.",
                "src_bytes": "Bytes sent from source to destination. Non-negative integer.",
                "dst_bytes": "Bytes sent from destination to source. Non-negative integer.",
                "logged_in": "Whether the connection resulted in a successful login: Yes or No.",
                "count": "Number of connections to the same destination host in the recent observation window. Non-negative integer.",
                "same_srv_rate": "Fraction of recent connections to the same service. Must be between 0 and 1.",
                "serror_rate": "Fraction of connections with SYN error status. Must be between 0 and 1.",
                "srv_serror_rate": "Fraction of connections to the same service with SYN error status. Must be between 0 and 1.",
                "dst_host_diff_srv_rate": "Fraction of connections to the destination host using a different service. Must be between 0 and 1.",
                "dst_host_same_src_port_rate": "Fraction of connections to the destination host using the same source port. Must be between 0 and 1.",
                "dst_host_srv_diff_host_rate": "Fraction of connections to the same service on the destination host coming from different hosts. Must be between 0 and 1.",
                "dst_host_srv_count": "Number of recent connections to the same service on the destination host. Non-negative integer."
            }

            # Read valid categorical values from the encoders already used by
            # the trained model. Gemini can choose among these, but no values
            # are supplied for the actual traffic record.
            valid_protocols = [str(x) for x in protocol_encoder.classes_]
            valid_services = [str(x) for x in service_encoder.classes_]
            valid_flags = [str(x) for x in flag_encoder.classes_]

            previous_classes = [
                item.get("class", "")
                for item in st.session_state.gemini_generated_history
            ]

            previous_scenarios = [
                item.get("scenario", "")
                for item in st.session_state.gemini_generated_history[-8:]
            ]

            prompt = f"""
You are an AI traffic-scenario generator for an educational Network Intrusion
Detection System (NIDS).

IMPORTANT VARIETY RULE:
- Every time the user clicks Generate Traffic Scenario, create a NEW scenario.
- Do NOT repeat a previous scenario.
- Do NOT repeat the same attack class when another unused class is available.
- Prefer an attack class that has not appeared recently.
- If all classes have already appeared, choose a different class from the
  immediately previous generation and create a substantially different
  traffic situation.
- Change the traffic characteristics and story between generations.
- The user should see a different attack/traffic scenario on every generation.

Recently generated classes:
{previous_classes}

Recently generated scenarios:
{previous_scenarios}


Your task is to independently generate ONE realistic synthetic network
traffic record and predict its traffic class.

Allowed classes:
Normal, DoS, Probe, R2L, U2R

The trained Random Forest expects EXACTLY these 15 features:

{feature_definitions}

Valid categorical values:
protocol: {valid_protocols}
service: {valid_services}
flag: {valid_flags}
logged_in: ["Yes", "No"]

Generate the feature values yourself. There is NO predefined attack template.

Return ONLY valid JSON in exactly this structure:
{{
  "class": "Normal|DoS|Probe|R2L|U2R",
  "scenario": "2-4 sentence explanation in very simple, non-technical language that a beginner can understand",
  "reason": "one short, simple sentence explaining in everyday language why this traffic looks like the selected class",
  "features": {{
    "duration": 0,
    "protocol": "tcp",
    "service": "http",
    "flag": "SF",
    "src_bytes": 0,
    "dst_bytes": 0,
    "logged_in": "No",
    "count": 1,
    "same_srv_rate": 0.5,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "dst_host_diff_srv_rate": 0.0,
    "dst_host_same_src_port_rate": 0.0,
    "dst_host_srv_diff_host_rate": 0.0,
    "dst_host_srv_count": 1
  }}
}}

Requirements:
- Generate all 15 feature values yourself.
- The class must be your own classification of the generated traffic.
- Keep categorical values exactly within the allowed lists.
- Non-negative integer fields must be valid integers.
- Rate fields must be decimal numbers from 0.0 to 1.0.
- Keep the combination of values internally consistent with the scenario.
- Explain the scenario like you are teaching a beginner. Avoid jargon such as
  "SYN", "RST", "socket exhaustion", "three-way handshake", or "packet flags"
  unless you immediately explain it in simple words.
- Do not copy a predefined attack template.
- Never repeat a previously generated scenario.
- Avoid repeating the previous class unless no other class is reasonably available.

SCENARIO DIFFICULTY:
- In most generations, create a clear and representative traffic pattern whose
  class should be recognizable by a trained NIDS model.
- Occasionally (roughly 1 out of 5 generations), create a realistic borderline
  or ambiguous traffic pattern where characteristics overlap with another
  class. Do NOT use random nonsense values just to force a misclassification.
- Borderline scenarios must still be internally consistent, realistic, and
  within plausible traffic ranges.
- Do not tell the UI user whether the sample was intended to be easy or
  challenging. The Random Forest must make its prediction independently.

This is for simulation/education only.
- Do not provide exploit instructions, attack commands, payloads, or operational
  instructions for attacking real systems.
"""

            try:
                with st.spinner("Gemini is generating traffic features..."):

                    # Try the preferred models first. Flash-Lite is used only
                    # as a last-resort fallback when both preferred models are
                    # temporarily unavailable.
                    models_to_try = [
                        "gemini-3.7-flash",
                        "gemini-3.6-flash",
                        "gemini-3.5-flash-lite"
                    ]

                    response = None
                    model_used = None
                    last_error = None

                    for model_name in models_to_try:
                        try:
                            response = gemini_client.models.generate_content(
                                model=model_name,
                                contents=prompt
                            )
                            model_used = model_name
                            break

                        except Exception as model_error:
                            last_error = model_error
                            error_text = str(model_error).lower()

                            # Only move to the next model for temporary capacity
                            # / availability problems. This guarantees that
                            # 3.7 is actually attempted before 3.6, and 3.6
                            # before Flash-Lite.
                            transient = (
                                "503" in error_text
                                or "unavailable" in error_text
                                or "high demand" in error_text
                                or "429" in error_text
                                or "resource exhausted" in error_text
                                or "overloaded" in error_text
                            )

                            if not transient:
                                raise

                    if response is None:
                        raise RuntimeError(
                            f"All Gemini models were temporarily unavailable. "
                            f"Last error: {last_error}"
                        )

                    raw = response.text.strip()
                    raw = re.sub(
                        r"^```(?:json)?\s*|\s*```$",
                        "",
                        raw,
                        flags=re.IGNORECASE
                    ).strip()

                    generated = json.loads(raw)

                generated_class = generated.get("class", "")
                features = generated.get("features", {})

                allowed_classes = {"Normal", "DoS", "Probe", "R2L", "U2R"}
                if generated_class not in allowed_classes:
                    st.error("Gemini returned an invalid traffic class.")
                    st.stop()

                required_features = list(feature_definitions.keys())
                missing = [f for f in required_features if f not in features]

                if missing:
                    st.error(
                        f"Gemini did not return all 15 required features: {missing}"
                    )
                    st.stop()

                # Validate categorical values before passing anything to the model.
                if features["protocol"] not in valid_protocols:
                    st.error("Gemini generated an unsupported protocol value.")
                    st.stop()

                if features["service"] not in valid_services:
                    st.error("Gemini generated an unsupported service value.")
                    st.stop()

                if features["flag"] not in valid_flags:
                    st.error("Gemini generated an unsupported flag value.")
                    st.stop()

                if features["logged_in"] not in {"Yes", "No"}:
                    st.error("Gemini generated an invalid logged_in value.")
                    st.stop()

                integer_features = [
                    "duration",
                    "src_bytes",
                    "dst_bytes",
                    "count",
                    "dst_host_srv_count"
                ]

                for name in integer_features:
                    value = features[name]
                    if (
                        isinstance(value, bool)
                        or not isinstance(value, int)
                        or value < 0
                    ):
                        st.error(
                            f"Gemini generated an invalid value for {name}: {value}"
                        )
                        st.stop()

                rate_features = [
                    "same_srv_rate",
                    "serror_rate",
                    "srv_serror_rate",
                    "dst_host_diff_srv_rate",
                    "dst_host_same_src_port_rate",
                    "dst_host_srv_diff_host_rate"
                ]

                for name in rate_features:
                    value = features[name]
                    if (
                        isinstance(value, bool)
                        or not isinstance(value, (int, float))
                        or not 0 <= float(value) <= 1
                    ):
                        st.error(
                            f"Gemini generated an invalid rate for {name}: {value}"
                        )
                        st.stop()

                # Remember successful generations so the next prompt can avoid
                # repeating the same class or scenario.
                st.session_state.gemini_generated_history.append({
                    "class": generated_class,
                    "scenario": generated.get("scenario", "")
                })

                # Keep only recent history to keep prompts compact.
                st.session_state.gemini_generated_history = (
                    st.session_state.gemini_generated_history[-8:]
                )

                st.markdown("---")
                st.subheader("🧠 AI-Generated Traffic Scenario")

                st.caption(
                    f"✨ Generated by Gemini • Model: **{model_used}**"
                )

                st.write(
                    generated.get(
                        "scenario",
                        "No scenario description."
                    )
                )

                st.write(
                    f"**Gemini Expected Class:** `{generated_class}`"
                )

                st.write(
                    f"**Why Gemini chose it:** "
                    f"{generated.get('reason', 'Not provided.')}"
                )

                st.markdown("### 🔢 Gemini-Generated Traffic Features")
                st.caption(
                    "These are the 15 traffic values generated by Gemini. "
                    "The same values are passed to the Random Forest model."
                )

                feature_rows = [
                    ("Connection Time", features["duration"]),
                    ("Protocol", features["protocol"]),
                    ("Service", features["service"]),
                    ("Connection Status", features["flag"]),
                    ("Data Sent", features["src_bytes"]),
                    ("Data Received", features["dst_bytes"]),
                    ("Login Successful", features["logged_in"]),
                    ("Recent Connections", features["count"]),
                    ("Same Service Usage", features["same_srv_rate"]),
                    ("Connection Error Rate", features["serror_rate"]),
                    ("Service Error Rate", features["srv_serror_rate"]),
                    ("Different Service Usage", features["dst_host_diff_srv_rate"]),
                    ("Same Port Usage", features["dst_host_same_src_port_rate"]),
                    ("Different Host Usage", features["dst_host_srv_diff_host_rate"]),
                    ("Service Connection Count", features["dst_host_srv_count"]),
                ]

                feature_df = pd.DataFrame(
                    feature_rows,
                    columns=["Feature", "Gemini Value"]
                )

                st.dataframe(
                    feature_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Convert Gemini's categorical values using the SAME encoders
                # used during training, then pass the generated record directly
                # to Random Forest.
                protocol = protocol_encoder.transform(
                    [features["protocol"]]
                )[0]

                service_name = service_encoder.transform(
                    [features["service"]]
                )[0]

                flag_name = flag_encoder.transform(
                    [features["flag"]]
                )[0]

                logged_in_value = (
                    1 if features["logged_in"] == "Yes" else 0
                )

                ai_input = np.array([[
                    features["duration"],
                    protocol,
                    service_name,
                    flag_name,
                    features["src_bytes"],
                    features["dst_bytes"],
                    logged_in_value,
                    features["count"],
                    features["same_srv_rate"],
                    features["serror_rate"],
                    features["srv_serror_rate"],
                    features["dst_host_diff_srv_rate"],
                    features["dst_host_same_src_port_rate"],
                    features["dst_host_srv_diff_host_rate"],
                    features["dst_host_srv_count"]
                ]])

                prediction = model.predict(ai_input)[0]
                confidence = model.predict_proba(ai_input).max() * 100

                class_names = {
                    0: "Normal",
                    1: "DoS",
                    2: "R2L",
                    3: "Probe",
                    4: "U2R"
                }

                result = class_names[prediction]

                if result == "Normal":
                    risk = "Low"
                    st.success(
                        f"## 🟢 Random Forest Prediction: Normal\n\n"
                        f"**Confidence:** {confidence:.2f}%"
                    )

                elif result == "Probe":
                    risk = "Medium"
                    st.warning(
                        f"## 🟠 Random Forest Prediction: Probe\n\n"
                        f"**Confidence:** {confidence:.2f}%"
                    )

                else:
                    risk = "High"
                    st.error(
                        f"## 🚨 Random Forest Prediction: {result}\n\n"
                        f"**Confidence:** {confidence:.2f}%"
                    )

                if generated_class == result:
                    st.success(
                        "✅ Gemini expected class and Random Forest prediction agree."
                    )
                else:
                    st.warning(
                        "⚠️ Model disagreement: Random Forest predicted a different class. "
                        "This is a useful example of a challenging traffic pattern."
                    )

                st.session_state.history.append({
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Prediction": result,
                    "Risk": risk,
                    "Confidence": f"{confidence:.2f}%",
                    "Source": "Gemini Scenario"
                })

            except json.JSONDecodeError:
                st.error(
                    "Gemini returned an unexpected format. "
                    "Please click Generate again."
                )

            except Exception as e:
                st.error(
                    f"Gemini request failed: {e}"
                )


if page == "📡 Live Traffic":

    st.title("📡 Live Traffic Monitor")
    st.caption("Continuous traffic-flow monitoring using the trained Random Forest model.")

    st.info(
        "ℹ️ Demo-safe live stream: controlled traffic-flow samples are "
        "processed automatically. Actual packet capture is not enabled."
    )

    if "live_running" not in st.session_state:
        st.session_state.live_running = False
    if "live_index" not in st.session_state:
        st.session_state.live_index = -1
    if "live_history" not in st.session_state:
        st.session_state.live_history = []

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        if st.button("▶️ Start Monitoring", use_container_width=True):
            st.session_state.live_running = True

    with c2:
        if st.button("⏹️ Stop Monitoring", use_container_width=True):
            st.session_state.live_running = False

    with c3:
        st.metric(
            "Monitor Status",
            "🟢 Active" if st.session_state.live_running else "⚪ Stopped"
        )

    st.markdown("---")

    if st.session_state.live_running:

        scenarios = [
            ("🟢 Normal Traffic", demo_data["🟢 Normal Traffic"]),
            ("🔴 DoS Attack", demo_data["🔴 DoS Attack"]),
            ("🟠 Probe Attack", demo_data["🟠 Probe Attack"]),
            ("🔴 R2L Attack", demo_data["🔴 R2L Attack"]),
            ("🟣 U2R Attack", demo_data["🟣 U2R Attack"])
        ]

        st.session_state.live_index = (
            st.session_state.live_index + 1
        ) % len(scenarios)

        scenario_name, selected = scenarios[st.session_state.live_index]

        protocol = protocol_encoder.transform([selected["protocol"]])[0]
        service_name = service_encoder.transform([selected["service"]])[0]
        flag_name = flag_encoder.transform([selected["flag"]])[0]
        logged_in_value = 1 if selected["logged_in"] == "Yes" else 0

        live_input = np.array([[
            selected["duration"],
            protocol,
            service_name,
            flag_name,
            selected["src_bytes"],
            selected["dst_bytes"],
            logged_in_value,
            selected["count"],
            selected["same_srv_rate"],
            selected["serror_rate"],
            selected["srv_serror_rate"],
            selected["dst_host_diff_srv_rate"],
            selected["dst_host_same_src_port_rate"],
            selected["dst_host_srv_diff_host_rate"],
            selected["dst_host_srv_count"]
        ]])

        prediction = model.predict(live_input)[0]
        confidence = model.predict_proba(live_input).max() * 100

        class_names = {
            0: "Normal",
            1: "DoS",
            2: "R2L",
            3: "Probe",
            4: "U2R"
        }

        result = class_names[prediction]

        if result == "Normal":
            risk = "Low"
        elif result == "Probe":
            risk = "Medium"
        else:
            risk = "High"

        record = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Traffic": scenario_name,
            "Prediction": result,
            "Risk": risk,
            "Confidence": f"{confidence:.2f}%"
        }

        st.session_state.live_history.append(record)
        st.session_state.live_history = st.session_state.live_history[-10:]

        st.session_state.history.append({
            "Time": record["Time"],
            "Prediction": result,
            "Risk": risk,
            "Confidence": record["Confidence"],
            "Source": "Live Monitor"
        })

        st.subheader("🚨 Current Detection")

        if result == "Normal":
            st.success(
                f"## 🟢 Normal Traffic\n\n"
                f"No suspicious activity detected.\n\n"
                f"**Confidence:** {confidence:.2f}%"
            )
        elif result == "Probe":
            st.warning(
                f"## 🟠 Probe Activity Detected\n\n"
                f"Possible scanning or information-gathering activity.\n\n"
                f"**Confidence:** {confidence:.2f}%"
            )
        else:
            st.error(
                f"## 🚨 {result} Attack Detected\n\n"
                f"Suspicious network activity has been detected.\n\n"
                f"**Confidence:** {confidence:.2f}%"
            )

        total = len(st.session_state.live_history)
        normal = sum(x["Risk"] == "Low" for x in st.session_state.live_history)
        threats = total - normal

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📦 Flows Analyzed", total)
        with c2:
            st.metric("🟢 Normal", normal)
        with c3:
            st.metric("🚨 Threats", threats)

        st.markdown("---")
        st.subheader("📋 Current Traffic Details")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Protocol", selected["protocol"])
        with c2:
            st.metric("Service", selected["service"])
        with c3:
            st.metric("Status", selected["flag"])
        with c4:
            st.metric("Connections", selected["count"])

        st.markdown("---")
        st.subheader("📡 Live Detection Feed")

        st.dataframe(
            pd.DataFrame(st.session_state.live_history[::-1]),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "### ⚪ Monitoring is stopped\n\n"
            "Click **▶️ Start Monitoring** to begin."
        )

        if st.session_state.live_history:
            st.subheader("🕒 Previous Monitoring Results")
            st.dataframe(
                pd.DataFrame(st.session_state.live_history[::-1]),
                use_container_width=True,
                hide_index=True
            )



# =========================
# WEBSITE TRAFFIC CHECK
# =========================

if page == "🌐 Website Traffic":

    st.title("🌐 Website Traffic Check")
    st.caption(
        "Quick health and traffic-behaviour check for an authorized website."
    )

    st.info(
        "ℹ️ This checks the website's public HTTP/HTTPS response. "
        "It does not inspect private visitor analytics."
    )

    url = st.text_input(
        "Website URL",
        placeholder="https://example.com"
    )

    if st.button("🔍 Check Website", use_container_width=True):

        if not url.strip():
            st.warning("Please enter a website URL.")

        else:
            target = url.strip()

            if not target.startswith(("http://", "https://")):
                target = "https://" + target

            try:
                with st.spinner("Checking website..."):
                    response = requests.get(
                        target,
                        timeout=8,
                        allow_redirects=True,
                        headers={"User-Agent": "NIDS-Website-Checker/1.0"}
                    )

                response_time = response.elapsed.total_seconds()
                data_kb = len(response.content) / 1024

                status_ok = 200 <= response.status_code < 400
                https_ok = target.lower().startswith("https://")

                if status_ok and response_time < 3:
                    traffic_status = "Normal"
                    risk = "Low"
                elif status_ok and response_time < 7:
                    traffic_status = "Slow / Check"
                    risk = "Medium"
                else:
                    traffic_status = "Unusual / Unreachable"
                    risk = "High"

                st.markdown("---")
                st.subheader("📊 Website Result")

                if traffic_status == "Normal":
                    st.success(
                        "🟢 Traffic appears normal — the website responded successfully."
                    )
                elif traffic_status == "Slow / Check":
                    st.warning(
                        "🟠 Traffic needs attention — the website responded, "
                        "but the response was slower than expected."
                    )
                else:
                    st.error(
                        "🔴 Something unusual is happening — the website is "
                        "slow or did not return a normal response."
                    )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric("HTTP Status", str(response.status_code))

                with c2:
                    st.metric("Response Time", f"{response_time:.2f} sec")

                with c3:
                    st.metric("Data Received", f"{data_kb:.1f} KB")

                with c4:
                    st.metric(
                        "HTTPS",
                        "Enabled" if https_ok else "Not detected"
                    )

                st.markdown("---")
                st.subheader("🔎 Connection Details")

                st.write(f"**Requested URL:** `{target}`")
                st.write(f"**Final URL:** `{response.url}`")
                st.write(f"**Risk Level:** `{risk}`")

            except requests.exceptions.Timeout:
                st.error(
                    "⏱️ Request timed out. The website did not respond within 8 seconds."
                )

            except requests.exceptions.RequestException as e:
                st.error(
                    f"🔴 Website could not be checked. Reason: `{e}`"
                )





# =========================
# WEBSITE SECURITY & HEALTH
# =========================

if page == "🌐 Website Security & Health":

    st.title("🌐 Website Security & Health")
    st.caption(
        "Passive security and availability check for a website you are authorized to inspect."
    )

    st.info(
        "ℹ️ This performs a normal HTTP/HTTPS request only. "
        "It does not scan, attack, or inspect private visitor analytics."
    )

    url = st.text_input(
        "Website URL",
        placeholder="https://example.com"
    )

    if st.button("🔍 Run Website Check", use_container_width=True):

        if not url.strip():
            st.warning("Please enter a website URL.")

        else:
            target = url.strip()

            if not target.startswith(("http://", "https://")):
                target = "https://" + target

            parsed = urlparse(target)
            hostname = parsed.hostname

            if not hostname:
                st.error("Please enter a valid website URL.")

            else:

                try:
                    with st.spinner("Checking website security and health..."):

                        response = requests.get(
                            target,
                            timeout=8,
                            allow_redirects=True,
                            headers={
                                "User-Agent": "NIDS-Website-Health-Checker/1.0"
                            }
                        )

                        response_time = response.elapsed.total_seconds()
                        response_size_kb = len(response.content) / 1024
                        redirect_count = len(response.history)
                        headers = {
                            k.lower(): v
                            for k, v in response.headers.items()
                        }

                    # -------------------------
                    # BASIC STATUS
                    # -------------------------

                    status_ok = 200 <= response.status_code < 400
                    https_enabled = parsed.scheme.lower() == "https"

                    # -------------------------
                    # DNS
                    # -------------------------

                    ip_address = "Unavailable"

                    try:
                        ip_address = socket.gethostbyname(hostname)
                    except socket.gaierror:
                        pass

                    # -------------------------
                    # TLS CERTIFICATE
                    # -------------------------

                    tls_ok = False
                    certificate_info = "Not checked"

                    if https_enabled:

                        try:
                            context = ssl.create_default_context()

                            with socket.create_connection(
                                (hostname, 443),
                                timeout=5
                            ) as sock:

                                with context.wrap_socket(
                                    sock,
                                    server_hostname=hostname
                                ) as secure_sock:

                                    cert = secure_sock.getpeercert()

                            tls_ok = True
                            certificate_info = "Valid TLS connection"

                        except Exception:
                            certificate_info = "TLS check failed"

                    # -------------------------
                    # SIMPLE WEBSITE HEALTH
                    # -------------------------

                    health_points = 0

                    if status_ok:
                        health_points += 50

                    if https_enabled:
                        health_points += 25

                    if https_enabled and tls_ok:
                        health_points += 15

                    if response_time < 3:
                        health_points += 10
                    elif response_time < 7:
                        health_points += 5

                    health_score = min(health_points, 100)

                    if health_score >= 80:
                        overall = "Good"
                        risk_level = "Low"
                    elif health_score >= 55:
                        overall = "Needs Attention"
                        risk_level = "Medium"
                    else:
                        overall = "Poor"
                        risk_level = "High"

                    # -------------------------
                    # RESULT
                    # -------------------------

                    st.markdown("---")
                    st.subheader("🌐 Website Health")

                    st.metric("🛡️ Risk Level", risk_level)

                    if overall == "Good":
                        st.success(
                            f"🟢 **Good — {health_score}/100**"
                        )
                    elif overall == "Needs Attention":
                        st.warning(
                            f"🟠 **Needs Attention — {health_score}/100**"
                        )
                    else:
                        st.error(
                            f"🔴 **Critical — {health_score}/100**"
                        )

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric(
                            "HTTP Status",
                            response.status_code
                        )

                    with c2:
                        st.metric(
                            "Response Time",
                            f"{response_time:.2f}s"
                        )

                    with c3:
                        st.metric(
                            "HTTPS",
                            "Enabled" if https_enabled else "No"
                        )

                    with c4:
                        st.metric(
                            "Redirects",
                            redirect_count
                        )

                    # -------------------------
                    # CONNECTION INFO
                    # -------------------------

                    st.markdown("---")
                    st.subheader("🌐 Connection Information")

                    c1, c2 = st.columns(2)

                    with c1:
                        st.write(f"**Domain:** `{hostname}`")
                        st.write(f"**Resolved IP:** `{ip_address}`")
                        st.write(f"**Final URL:** `{response.url}`")

                    with c2:
                        st.write(f"**Response Size:** `{response_size_kb:.1f} KB`")
                        st.write(f"**Redirects:** `{redirect_count}`")
                        st.write(f"**TLS:** `{certificate_info}`")

                    # -------------------------
                    # WEBSITE HEALTH SUMMARY
                    # -------------------------

                    st.markdown("---")
                    st.subheader("📋 Website Health Checks")

                    health_checks = pd.DataFrame([
                        {
                            "Check": "Website reachable",
                            "Status": "✅ Normal" if status_ok else "❌ Failed"
                        },
                        {
                            "Check": "HTTPS",
                            "Status": "✅ Enabled" if https_enabled else "⚠️ Not detected"
                        },
                        {
                            "Check": "TLS connection",
                            "Status": "✅ Valid" if tls_ok else ("— Not checked" if not https_enabled else "⚠️ Check failed")
                        },
                        {
                            "Check": "Response speed",
                            "Status": (
                                "✅ Fast"
                                if response_time < 3
                                else "🟠 Slow"
                                if response_time < 7
                                else "🔴 Very slow"
                            )
                        },
                        {
                            "Check": "Redirects",
                            "Status": (
                                "✅ None"
                                if redirect_count == 0
                                else f"ℹ️ {redirect_count} redirect(s)"
                            )
                        }
                    ])

                    st.dataframe(
                        health_checks,
                        use_container_width=True,
                        hide_index=True
                    )

                    # -------------------------
                    # SIMPLE EXPLANATION
                    # -------------------------

                    st.markdown("---")
                    st.subheader("💡 What This Means")

                    st.info(f"🛡️ Risk Level: **{risk_level}**")

                    explanations = []

                    if status_ok:
                        explanations.append(
                            "The website responded successfully."
                        )
                    else:
                        explanations.append(
                            "The website did not return a normal successful response."
                        )

                    if https_enabled and tls_ok:
                        explanations.append(
                            "HTTPS and the TLS connection are working."
                        )
                    elif not https_enabled:
                        explanations.append(
                            "HTTPS was not detected for the entered URL."
                        )

                    if response_time < 3:
                        explanations.append(
                            "The response was fast."
                        )
                    elif response_time < 7:
                        explanations.append(
                            "The response was slower than the preferred threshold."
                        )
                    else:
                        explanations.append(
                            "The response was very slow and may need attention."
                        )

                    for item in explanations:
                        st.write(f"• {item}")

                    st.caption(
                        "This score is a simple health indicator, not a penetration test "
                        "or proof that a website is secure."
                    )

                except requests.exceptions.Timeout:
                    st.error(
                        "⏱️ The website did not respond within 8 seconds."
                    )

                except requests.exceptions.RequestException as e:
                    st.error(
                        f"🔴 Website could not be checked: `{e}`"
                    )



if page== "📊 Analytics":
    st.title("📊 Detection Analytics")
    st.caption("Overview of Network Traffic predictions made by the system")

    history=st.session_state.get("history",[])
    if len(history)==0:
        st.info(
            "📭 No predictions yet. "
            "Run an analysis or try Demo Mode first."
        )
    else:
        history_df = pd.DataFrame(history)

        # Older session entries may not have Source; keep Analytics compatible.
        if "Source" not in history_df.columns:
            history_df["Source"] = "Manual"
        else:
            history_df["Source"] = history_df["Source"].fillna("Manual")
         # =========================
        # SUMMARY CARDS
        # =========================
        total_predictions=len(history_df)
        normal_count = int((history_df["Risk"] == "Low").sum())
        suspicious_count = int((history_df["Risk"] != "Low").sum())
        col1 ,col2,col3=st.columns(3)
        with col1:
            st.metric("🔢 Total Predictions",
                total_predictions
            )

        with col2:
            st.metric(
                "🟢 Normal Traffic",
                normal_count
            )

        with col3:
            st.metric(
                "🚨 Suspicious Traffic",
                suspicious_count
            )

        st.markdown("---")
         # =========================
        # PREDICTION CHART
        # =========================
        st.subheader("📈 Prediction Distribution")
        prediction_counts=(history_df["Prediction"].value_counts())
        st.bar_chart(prediction_counts)

        st.subheader("🧪 Demo vs Manual")
        source_counts = history_df["Source"].value_counts()
        st.bar_chart(source_counts)

        st.markdown("---")
        # =========================
        # CONFIDENCE
        # =========================

        st.subheader("🎯 Model Confidence")

        confidence_df = history_df.copy()

        confidence_df["Confidence"] = (
            confidence_df["Confidence"]
            .str.replace("%", "")
            .astype(float)
        )
        st.line_chart(confidence_df["Confidence"])
        st.markdown("---")
         # =========================
        # PREDICTION HISTORY
        # =========================

        st.subheader("🕒 Prediction History")

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )



# =========================
# PREDICTION HISTORY
# =========================

if page == "🕘 Prediction History":
    st.title("🕘 Prediction History")
    st.caption("All predictions made during this application session.")

    history = st.session_state.get("history", [])

    if not history:
        st.info(
            "📭 No predictions yet. Use Analyze Traffic, Try Demo, "
            "or AI Traffic Generator to create predictions."
        )
    else:
        history_df = pd.DataFrame(history)

        if "Source" not in history_df.columns:
            history_df["Source"] = "Manual"

        st.metric("🔢 Total Predictions", len(history_df))

        st.markdown("---")
        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        if st.button("🗑️ Clear Prediction History"):
            st.session_state.history = []
            st.rerun()


# =========================
# REPORTS
# =========================

if page == "📄 Reports":
    st.title("📄 Reports")
    st.caption("Generate a simple summary report from the current prediction history.")

    history = st.session_state.get("history", [])

    if not history:
        st.info(
            "📭 No prediction data available yet. "
            "Run at least one traffic analysis first."
        )
    else:
        report_df = pd.DataFrame(history)

        if "Source" not in report_df.columns:
            report_df["Source"] = "Manual"

        total = len(report_df)
        normal = int((report_df["Risk"] == "Low").sum())
        suspicious = total - normal

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Predictions", total)

        with col2:
            st.metric("Normal", normal)

        with col3:
            st.metric("Suspicious", suspicious)

        st.markdown("---")
        st.subheader("📊 Prediction Summary")

        prediction_summary = (
            report_df["Prediction"]
            .value_counts()
            .rename_axis("Prediction")
            .reset_index(name="Count")
        )

        st.dataframe(
            prediction_summary,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("🔍 Recent Results")
        st.dataframe(
            report_df.tail(10),
            use_container_width=True,
            hide_index=True
        )

        # Build a plain-text report suitable for saving/submitting.
        report_lines = [
            "NETWORK INTRUSION DETECTION SYSTEM - PREDICTION REPORT",
            "=" * 55,
            f"Total predictions: {total}",
            f"Normal predictions: {normal}",
            f"Suspicious predictions: {suspicious}",
            "",
            "Prediction counts:"
        ]

        for _, row in prediction_summary.iterrows():
            report_lines.append(
                f"- {row['Prediction']}: {row['Count']}"
            )

        report_lines.extend([
            "",
            "Prediction history:",
            report_df.to_string(index=False)
        ])

        report_text = "\n".join(report_lines)

        st.download_button(
            "⬇️ Download Report",
            data=report_text,
            file_name="nids_prediction_report.txt",
            mime="text/plain",
            use_container_width=True
        )


# =========================
# ABOUT PROJECT
# =========================

if page == "ℹ️ About Project":
    st.title("ℹ️ About the Project")
    st.caption("Network Intrusion Detection System")

    st.markdown(
        """
        ### 🛡️ What is this project?

        This project is a **Network Intrusion Detection System (NIDS)** that
        analyzes network-traffic features and uses a trained **Random Forest**
        machine-learning model to classify traffic.

        The system can identify five traffic classes:

        - 🟢 **Normal** — regular network activity
        - 🔴 **DoS** — denial-of-service type traffic
        - 🟠 **Probe** — scanning or information-gathering activity
        - 🔴 **R2L** — remote-to-local attack traffic
        - 🟣 **U2R** — user-to-root / privilege-escalation type traffic

        ### 🤖 AI Traffic Generator

        The project also includes a **Gemini-powered traffic scenario
        generator**. Gemini generates a synthetic traffic scenario along with
        the 15 feature values required by the Random Forest.

        The generated values are then passed independently to the trained
        Random Forest. The interface shows both:

        **Gemini Expected Class → Random Forest Prediction**

        This allows the application to demonstrate both successful
        classifications and challenging cases where the model may disagree.

        ### 📊 Model Features

        The Random Forest uses 15 network-traffic features covering:

        - connection time
        - protocol and service
        - connection status
        - data sent and received
        - login status
        - recent connection behaviour
        - service/error rates
        - destination-host behaviour

        ### 🌐 Website Security & Health

        The application also provides a basic website health checker that
        examines reachability, HTTP status, response time, HTTPS, TLS,
        redirects, resolved IP information, and a simple risk indicator.

        ### 📡 Live Traffic

        The Live Traffic section provides a demonstration view of changing
        traffic and applies the trained detection model to the displayed
        traffic data.

        ### 📈 Analytics & Reports

        Prediction History stores results from the current application
        session. Analytics summarizes those results, while Reports provides
        a simple downloadable prediction report.

        ### ⚠️ Important Note

        This is an educational/demo NIDS project. Model predictions are not
        a guarantee of real-world attack detection, and the website health
        score is a basic indicator rather than a full security audit.
        """
    )
