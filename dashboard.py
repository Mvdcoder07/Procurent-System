import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(
    page_title="AI Proctoring Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Proctoring System Dashboard")
st.markdown("**Real time suspicious activity monitor for online exams**")

st.divider()

# Auto refresh every 3 seconds
refresh = st.empty()

while True:
    with refresh.container():

        # Check if log file exists
        if os.path.exists('events_log.csv'):
            df = pd.read_csv('events_log.csv')

            if len(df) > 0:

                # Top metrics row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Events", len(df))

                with col2:
                    multiple_faces = len(df[df['event'].str.contains('Multiple', na=False)])
                    st.metric("Multiple Face Alerts", multiple_faces)

                with col3:
                    pose_alerts = len(df[df['event'].str.contains('Pose', na=False)])
                    st.metric("Head Pose Alerts", pose_alerts)

                with col4:
                    absent_alerts = len(df[df['event'].str.contains('Absent', na=False)])
                    st.metric("Absence Alerts", absent_alerts)

                st.divider()

                # Two column layout
                left, right = st.columns(2)

                with left:
                    st.subheader("📋 Event Log")
                    st.dataframe(
                        df.sort_values('timestamp', ascending=False),
                        use_container_width=True
                    )

                with right:
                    st.subheader("📊 Event Distribution")
                    event_counts = df['event'].value_counts()
                    st.bar_chart(event_counts)

                st.divider()

                # Risk Assessment
                st.subheader("⚠️ Risk Assessment")

                total = len(df)
                if total >= 10:
                    st.error("🔴 HIGH RISK — Multiple suspicious activities detected")
                elif total >= 5:
                    st.warning("🟡 MEDIUM RISK — Some suspicious activities detected")
                else:
                    st.success("🟢 LOW RISK — Minimal suspicious activity")

            else:
                st.info("No suspicious events logged yet")

        else:
            st.warning("events_log.csv not found — Run main.py first to start proctoring")

    time.sleep(3)
    refresh.empty()