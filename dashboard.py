# dashboard.py
# AI Proctoring System — Admin Dashboard
# Developer: Mangesh Deokar
# SYCET IGNITE HACKATHON 2026

import streamlit as st
import pandas as pd
import glob
import os
import time

# ================================
# Page Configuration
# ================================
st.set_page_config(
    page_title="AI Proctoring Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ================================
# Auto Refresh Every 5 Seconds
# ================================
st.markdown(
    """
    <meta http-equiv="refresh" content="5">
    """,
    unsafe_allow_html=True
)

# ================================
# Helper Functions
# ================================
def get_risk_level(events):
    if events >= 10:
        return "HIGH"
    elif events >= 5:
        return "MEDIUM"
    else:
        return "LOW"

def load_all_students():
    log_files = glob.glob('logs/events_*.csv')
    all_data = []

    for log_file in log_files:
        try:
            df = pd.read_csv(log_file)
            if len(df) > 0:
                student_id = df['student_id'].iloc[0]
                total = len(df)
                all_data.append({
                    'Student ID': student_id,
                    'Total Events': total,
                    'Multiple Face Alerts': int(len(df[df['event'].str.contains('Multiple', na=False)])),
                    'Pose Alerts': int(len(df[df['event'].str.contains('Pose', na=False)])),
                    'Absence Alerts': int(len(df[df['event'].str.contains('Absent', na=False)])),
                    'Risk Level': get_risk_level(total)
                })
        except:
            pass

    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# ================================
# Dashboard Title
# ================================
st.title("🎓 AI Proctoring System")
st.markdown("**Real time suspicious activity monitor for online exams**")
st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')} — Auto refreshes every 5 seconds")
st.divider()

# ================================
# Load Data
# ================================
summary_df = load_all_students()

if len(summary_df) > 0:

    # ================================
    # Top Metrics
    # ================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Students", len(summary_df))

    with col2:
        high_risk = len(summary_df[summary_df['Risk Level'] == 'HIGH'])
        st.metric("High Risk", high_risk,
                 delta=f"{high_risk} need review",
                 delta_color="inverse")

    with col3:
        medium_risk = len(summary_df[summary_df['Risk Level'] == 'MEDIUM'])
        st.metric("Medium Risk", medium_risk)

    with col4:
        total_events = int(summary_df['Total Events'].sum())
        st.metric("Total Events", total_events)

    st.divider()

    # ================================
    # Risk Alerts
    # ================================
    high_risk_df = summary_df[summary_df['Risk Level'] == 'HIGH']
    medium_risk_df = summary_df[summary_df['Risk Level'] == 'MEDIUM']

    if len(high_risk_df) > 0:
        st.error(f"🔴 ALERT — {len(high_risk_df)} HIGH RISK students detected!")
        st.dataframe(high_risk_df, use_container_width=True)

    if len(medium_risk_df) > 0:
        st.warning(f"🟡 WARNING — {len(medium_risk_df)} MEDIUM RISK students detected.")

    st.divider()

    # ================================
    # Two Column Layout
    # ================================
    left, right = st.columns(2)

    with left:
        st.subheader("📋 All Students Overview")
        st.dataframe(summary_df, use_container_width=True)

    with right:
        st.subheader("📊 Risk Distribution")
        risk_counts = summary_df['Risk Level'].value_counts()
        st.bar_chart(risk_counts)

    st.divider()

    # ================================
    # Event Type Analysis
    # ================================
    st.subheader("📈 Event Type Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_face = int(summary_df['Multiple Face Alerts'].sum())
        st.metric("Face Alerts", total_face)
        st.progress(min(total_face / max(total_events, 1), 1.0))

    with col2:
        total_pose = int(summary_df['Pose Alerts'].sum())
        st.metric("Pose Alerts", total_pose)
        st.progress(min(total_pose / max(total_events, 1), 1.0))

    with col3:
        total_absence = int(summary_df['Absence Alerts'].sum())
        st.metric("Absence Alerts", total_absence)
        st.progress(min(total_absence / max(total_events, 1), 1.0))

    st.divider()

    # ================================
    # Individual Student Detail
    # ================================
    st.subheader("🔍 Individual Student Detail")

    student_ids = summary_df['Student ID'].tolist()
    selected_student = st.selectbox(
        "Select Student ID to view details",
        student_ids
    )

    if selected_student:
        log_file = f"logs/events_{selected_student}.csv"

        if os.path.exists(log_file):
            student_df = pd.read_csv(log_file)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"Events for {selected_student}")
                st.dataframe(student_df, use_container_width=True)

            with col2:
                st.subheader("Event Breakdown")
                event_counts = student_df['event'].value_counts()
                st.bar_chart(event_counts)

            risk = get_risk_level(len(student_df))
            if risk == "HIGH":
                st.error(f"🔴 Student {selected_student} — HIGH RISK")
            elif risk == "MEDIUM":
                st.warning(f"🟡 Student {selected_student} — MEDIUM RISK")
            else:
                st.success(f"🟢 Student {selected_student} — LOW RISK")

    st.divider()

    # ================================
    # System Performance
    # ================================
    st.subheader("⚡ System Performance")

    try:
        import psutil
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("CPU Usage", f"{psutil.cpu_percent()}%")

        with col2:
            st.metric("Memory Usage",
                     f"{psutil.virtual_memory().percent}%")

        with col3:
            st.metric("Active Log Files",
                     len(glob.glob('logs/events_*.csv')))
    except:
        st.info("Install psutil for system metrics")

else:
    st.info("No student data yet — Run main.py to start proctoring")
    st.markdown("""
    ### How To Start
    1. Open terminal
    2. Run `python main.py`
    3. Dashboard updates automatically every 5 seconds
    """)

# ================================
# Footer
# ================================
st.divider()
st.markdown(
    "**AI Proctoring System** — Developed by Tech Titans | SYCET IGNITE HACKATHON 2026"
)