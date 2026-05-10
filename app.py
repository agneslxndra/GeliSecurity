import streamlit as st
import pandas as pd
import plotly.express as px

from database import init_db, insert_finding, get_all_findings, update_status
from ai_engine import generate_remediation, generate_autofix
from pdf_generator import generate_pdf_report, generate_autofix_pdf_report
# from streamlit_option_menu import option_menu

def get_severity_score(severity):
    score_mapping = {
        "Low": 1.0,
        "Medium": 2.0,
        "High": 3.0,
        "Critical": 4.0
    }

    return score_mapping.get(severity, 0.0)

init_db()

st.set_page_config(
    page_title="GeliSecure",
    page_icon="🛡️",
    layout="wide"
)

# with st.sidebar:
#     selected = option_menu(
#         menu_title="Main Menu", 
#         options=["Overview", "New Finding", "Library", "AutoFix", "Report"], 
#         icons=["house", "plus-circle", "book", "robot", "file-earmark-text"], # Pakai Bootstrap Icons
#         menu_icon="cast", 
#         default_index=0,
#         styles={
#             "container": {"padding": "5px", "background-color": "#f8f9fa"},
#             "icon": {"color": "orange", "font-size": "18px"}, 
#             "nav-link": {"font-size": "14px", "text-align": "left", "margin":"5px", "--hover-color": "#eee"},
#             "nav-link-selected": {"background-color": "#007bff"},
#         }
#     )

# --- TEMPATKAN DI SINI (Setelah st.set_page_config) ---
st.markdown("""
<style>
/* =========================
   GLOBAL FONT
========================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* =========================
   MAIN BACKGROUND
========================= */
.stApp {
    background-color: #0E1117;
    color: #F9FAFB;
}

/* =========================
   SIDEBAR
========================= */
[data-testid="stSidebar"] {
    background-color: #1F2430;
}

[data-testid="stSidebar"] * {
    color: #F9FAFB !important;
}

/* Hide original radio circle */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none;
}

/* Sidebar menu container */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
    padding-top: 10px;
}

/* Default sidebar menu item */
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background-color: transparent;
    border-radius: 12px;
    padding: 12px 16px !important;
    margin-bottom: 6px;
    border: 1px solid transparent;
    transition: all 0.25s ease;
    cursor: pointer;
}

/* Sidebar text */
[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: #E5E7EB !important;
    font-weight: 600 !important;
}

/* Hover menu */
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #374151 !important;
    transform: translateX(4px);
}

/* Active / selected menu */
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #2563EB !important;
    border: 1px solid #60A5FA !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
}

/* Active menu text */
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* =========================
   TITLES & TEXT
========================= */
h1, h2, h3 {
    color: #F9FAFB !important;
    font-weight: 800 !important;
}

p, label, span {
    color: #E5E7EB;
}

/* Caption */
[data-testid="stCaptionContainer"] {
    color: #A1A1AA !important;
}

/* =========================
   METRIC CARDS
========================= */
div[data-testid="stMetric"] {
    background: #161B22 !important;
    border: 1px solid #2D333B !important;
    padding: 18px 20px !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22) !important;
}

/* Metric label */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label p {
    color: #9CA3AF !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

/* Metric value */
div[data-testid="stMetric"] div[data-testid="stMetricValue"],
div[data-testid="stMetric"] div[data-testid="stMetricValue"] * {
    color: #F9FAFB !important;
    font-weight: 800 !important;
    font-size: 34px !important;
}

/* Metric delta */
div[data-testid="stMetric"] div[data-testid="stMetricDelta"],
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] * {
    font-weight: 700 !important;
}

/* =========================
   INPUTS
========================= */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #F9FAFB !important;
    color: #111827 !important;
    border-radius: 10px !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label {
    color: #F9FAFB !important;
    font-weight: 600 !important;
}

/* =========================
   BUTTON
========================= */
.stButton > button {
    background-color: #2563EB !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.55rem 1rem !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background-color: #1D4ED8 !important;
    border: none !important;
}

/* =========================
   INFO BOX
========================= */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* =========================
   DATAFRAME / TABLE AREA
========================= */
[data-testid="stDataFrame"] {
    background: #161B22 !important;
    border: 1px solid #2D333B !important;
    border-radius: 18px !important;
    padding: 10px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22) !important;
}

[data-testid="stDataFrame"] div {
    border-color: #2D333B !important;
}

[data-testid="stDataFrame"] iframe {
    border-radius: 14px !important;
}

/* =========================
   PLOTLY CHART CARD AREA
========================= */
[data-testid="stPlotlyChart"] {
    background: #161B22 !important;
    border: 1px solid #2D333B !important;
    border-radius: 18px !important;
    padding: 16px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22) !important;
}

/* Hilangin frame putih bawaan */
[data-testid="stPlotlyChart"] > div {
    background: transparent !important;
}

/* Divider biar subtle */
hr {
    border-color: #2D333B !important;
}
            
</style>
""", unsafe_allow_html=True)



st.title("🛡️ GeliSecure")
st.caption("AI-Powered Vulnerability Remediation Platform for Developer-Friendly Security Fixes")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "New Finding",
        "Findings Library",
        "AutoFix Assistant",
        "Remediation Report"
    ]
)


# =========================
# DASHBOARD
# =========================

if menu == "Overview":
    st.header("📊 Security Remediation Overview")
    st.caption("Monitor vulnerability findings, remediation status, and AI-generated security insights.")

    # 1. AMBIL DATA DULU
    rows = get_all_findings()

    if len(rows) == 0:
        st.info("No findings available yet. Please add a finding first.")
    else:
        # 2. PROSES DATAFRAME
        df = pd.DataFrame(rows, columns=[
            "ID", "Application", "Finding", "Severity", "Score", 
            "Affected URL", "Description", "Evidence", "Language", 
            "AI Result", "Status", "Created At"
        ])

        # 3. HITUNG STATISTIK (Didefinisikan sebelum dipakai di Metric)
        total_findings = len(df)
        open_findings = len(df[df["Status"] == "Open"])
        fixed_findings = len(df[df["Status"] == "Fixed"])
        critical_findings = len(df[df["Severity"] == "Critical"])
        average_score = round(df["Score"].mean(), 2)

        # 4. TAMPILKAN METRICS (Sekarang variabel sudah ada nilainya)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Findings", total_findings)
        m2.metric("Open Findings", open_findings, delta=f"{open_findings} Active", delta_color="inverse")
        m3.metric("Fixed", fixed_findings, delta="Resolved")
        # Warna merah untuk Critical
        m4.metric("Critical", critical_findings, delta="Immediate", delta_color="inverse")
        m5.metric("Avg Score", f"{average_score}/4.0")

        st.divider()

        # 5. VISUALISASI (Chart)
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            severity_count = df["Severity"].value_counts().reset_index()
            severity_count.columns = ["Severity", "Total"]
            fig_pie = px.pie(
                severity_count,
                names="Severity",
                values="Total",
                hole=0.5,
                title="Findings by Severity",
                color_discrete_sequence=["#D32F2F", "#F57C00", "#FBC02D", "#388E3C"]
            )
            fig_pie.update_layout(
                margin=dict(t=55, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F9FAFB"),
                title=dict(
                    text="Findings by Severity",
                    font=dict(size=18, color="#F9FAFB"),
                    x=0.02
                ),
                legend=dict(
                    font=dict(color="#F9FAFB"),
                    bgcolor="rgba(0,0,0,0)"
                )
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            status_count = df["Status"].value_counts().reset_index()
            status_count.columns = ["Status", "Total"]
            fig_bar = px.bar(
                status_count,
                x="Status",
                y="Total",
                title="Findings by Status",
                color="Status",
                color_discrete_map={"Open": "#D32F2F", "Fixed": "#388E3C", "Accepted Risk": "#757575"}
            )
            fig_bar.update_layout(
                showlegend=False,
                margin=dict(t=55, b=40, l=40, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F9FAFB"),
                title=dict(
                    text="Findings by Status",
                    font=dict(size=18, color="#F9FAFB"),
                    x=0.02
                ),
                xaxis=dict(
                    gridcolor="#2D333B",
                    zerolinecolor="#2D333B"
                ),
                yaxis=dict(
                    gridcolor="#2D333B",
                    zerolinecolor="#2D333B"
                )
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # 6. TABEL RECENT FINDINGS
        st.subheader("📑 Recent Findings")
        st.dataframe(
            df[["ID", "Application", "Finding", "Severity", "Score", "Status", "Created At"]],
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Risk Score", 
                    min_value=0, 
                    max_value=4,
                    format="%.1f"
                ),
                # GANTI BadgeColumn JADI SelectboxColumn
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Open", "Fixed", "Accepted Risk"],
                    help="Status terkini dari temuan"
                ),
                "Created At": st.column_config.DatetimeColumn(
                    "Timestamp", 
                    format="D MMM YYYY, HH:mm"
                )
            },
            use_container_width=True,
            hide_index=True
        )


# =========================
# ADD FINDING
# =========================
elif menu == "New Finding":
    st.header("New Vulnerability Finding")
    st.caption("Submit a security finding and generate AI-powered remediation guidance.")

    application_name = st.text_input("Application Name")
    finding_title = st.text_input("Finding Title")

    severity = st.selectbox(
        "Severity",
        ["Low", "Medium", "High", "Critical"],
        key="new_finding_severity"
    )

    score = get_severity_score(severity)
    st.info(f"Severity Score: {score:.1f}")

    affected_url = st.text_input("Affected URL")
    description = st.text_area("Description")
    evidence = st.text_area("Evidence")

    language = st.selectbox(
        "Target Language",
        ["Python", "PHP", "JavaScript", "Java", "Other"]
    )

    submitted = st.button("Generate Remediation")

    if submitted:
        if application_name == "" or finding_title == "" or description == "":
            st.error("Please fill Application Name, Finding Title, and Description.")
        else:
            ai_result = generate_remediation(
                finding_title,
                severity,
                description,
                affected_url,
                language
            )

            insert_finding(
                application_name,
                finding_title,
                severity,
                score,
                affected_url,
                description,
                evidence,
                language,
                ai_result
            )

            st.success("Finding saved and remediation generated successfully.")
            st.markdown(ai_result)


# =========================
# FINDINGS DATA
# =========================
elif menu == "Findings Library":
    st.header("Findings Library")
    st.caption("View, track, and update all vulnerability findings.")

    rows = get_all_findings()

    if len(rows) == 0:
        st.info("No findings available.")
    else:
        df = pd.DataFrame(rows, columns=[
            "ID",
            "Application",
            "Finding",
            "Severity",
            "Score",
            "Affected URL",
            "Description",
            "Evidence",
            "Language",
            "AI Result",
            "Status",
            "Created At"
        ])

        st.dataframe(df)

        st.subheader("Update Finding Status")

        finding_id = st.number_input("Finding ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ["Open", "Fixed", "Accepted Risk"])

        if st.button("Update Status"):
            update_status(finding_id, new_status)
            st.success("Status updated successfully. Please refresh the page.")


# =========================
# AUTOFIX ASSISTANT
# =========================
elif menu == "AutoFix Assistant":
    st.header("AutoFix Assistant")
    st.caption("Paste vulnerable code and let AI generate a safer fixed version.")

    st.info(
        "Fitur ini membantu developer mendapatkan contoh secure code fix. "
        "Hasil AutoFix tetap perlu direview sebelum diterapkan ke production."
    )

    col_left, col_right = st.columns(2)

    with col_left:
        finding_title = st.text_input(
            "Finding Title",
            placeholder="Example: SQL Injection"
        )

        severity = st.selectbox(
            "Severity",
            ["Low", "Medium", "High", "Critical"],
            key="autofix_severity"
        )

        language = st.selectbox(
            "Programming Language",
            ["Python", "PHP", "JavaScript", "Java", "Other"],
            key="autofix_language"
        )

        vulnerable_code = st.text_area(
            "Paste Vulnerable Code",
            height=350,
            placeholder="Paste your vulnerable code here..."
        )

        generate_fix = st.button("Generate AutoFix")

    with col_right:
        st.subheader("AutoFix Result")

        if generate_fix:
            if finding_title == "" or vulnerable_code == "":
                st.error("Please fill Finding Title and paste the vulnerable code first.")
            else:
                with st.spinner("Generating secure fix..."):
                    autofix_result = generate_autofix(
                        finding_title=finding_title,
                        severity=severity,
                        language=language,
                        vulnerable_code=vulnerable_code
                    )

                st.success("AutoFix generated successfully.")
                st.markdown(autofix_result)

                autofix_pdf_data = {
                    "Finding Title": finding_title,
                    "Severity": severity,
                    "Language": language,
                    "Vulnerable Code": vulnerable_code,
                    "AutoFix Result": autofix_result
                }

                autofix_pdf_file = generate_autofix_pdf_report(autofix_pdf_data)

                st.download_button(
                    label="Download AutoFix as PDF",
                    data=autofix_pdf_file,
                    file_name="quickfix_autofix_report.pdf",
                    mime="application/pdf"
                )
        else:
            st.write("AutoFix result will appear here after generation.")

# =========================
# EXPORT REPORT
# =========================
elif menu == "Remediation Report":
    st.header("Remediation Report")
    st.caption("Generate and export AI-assisted vulnerability remediation reports.")

    rows = get_all_findings()

    if len(rows) == 0:
        st.info("No findings available to export.")
    else:
        df = pd.DataFrame(rows, columns=[
            "ID",
            "Application",
            "Finding",
            "Severity",
            "Score",
            "Affected URL",
            "Description",
            "Evidence",
            "Language",
            "AI Result",
            "Status",
            "Created At"
        ])

        selected_id = st.selectbox("Select Finding ID", df["ID"].tolist())

        selected = df[df["ID"] == selected_id].iloc[0]

        report = f"""
# GeliSecure Report

## Application
{selected["Application"]}

## Finding
{selected["Finding"]}

## Severity
{selected["Severity"]}

## Risk Score
{selected["Score"]}

## Affected URL
{selected["Affected URL"]}

## Description
{selected["Description"]}

## Evidence
{selected["Evidence"]}

## Status
{selected["Status"]}

## AI Remediation Result
{selected["AI Result"]}

## Created At
{selected["Created At"]}
"""

        st.markdown(report)

        pdf_file = generate_pdf_report(selected)

        st.download_button(
            label="Download Report as PDF",
            data=pdf_file,
            file_name=f"quickfix_report_{selected_id}.pdf",
            mime="application/pdf"
        )