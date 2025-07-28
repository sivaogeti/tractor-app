# Updated app.py with Plotly for UI and Matplotlib for PDF export

import streamlit as st
from auth import authenticate
from data import add_log, get_user_logs, get_all_logs
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import io
import base64
from tractor_pdf import TractorPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="Tractor Logger", layout="wide")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🚜 Tractor Work Logger - Login")
    role = st.radio("Login as", ["employee", "admin"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_role = authenticate(username, password)
        if user_role == role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user_role
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials or role mismatch.")
    st.stop()

# --- LOGOUT ---
st.sidebar.title("Navigation")
st.sidebar.write(f"Logged in as: `{st.session_state.username}` ({st.session_state.role})")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- EMPLOYEE DASHBOARD ---
if st.session_state.role == "employee":
    st.title("📝 Employee Dashboard")

    with st.form("log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_entry = st.date_input("Date", value=date.today(), min_value=date.today())
            customer = st.text_input("Customer Name")
            location = st.text_input("Customer Location")
        with col2:
            tractor = st.text_input("Tractor Model")
            acres = st.number_input("Acres Ploughed", min_value=0.0, step=0.5)
            cost = int(acres * 100)

        st.write(f"💰 Auto-calculated Cost: ₹{cost}")
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            if not (customer and location and tractor and acres > 0):
                st.warning("❗ Please fill all fields and ensure acres > 0 before submitting.")
            else:
                add_log({
                    "date": str(date_entry),
                    "customer": customer,
                    "location": location,
                    "tractor": tractor,
                    "acres": acres,
                    "cost": cost,
                    "employee": st.session_state.username
                })
                st.success("✅ Entry saved!")

    st.subheader("📋 Your Work Log")
    df = pd.DataFrame(get_user_logs(st.session_state.username))
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    st.dataframe(df, use_container_width=True, height=400)

# --- ADMIN DASHBOARD ---
elif st.session_state.role == "admin":
    st.title("📊 Admin Dashboard")
    df = pd.DataFrame(get_all_logs())

    # 🔁 Fix: Ensure datetime BEFORE using for filtering
    df["date"] = pd.to_datetime(df["date"])

    # --- Filters ---
    with st.expander("🔍 Filter Logs"):
        col1, col2 = st.columns(2)
        with col1:
            employee_filter = st.selectbox("Employee", ["All"] + sorted(df["employee"].unique().tolist()))
            customer_filter = st.multiselect("Customer(s)", sorted(df["customer"].unique()))
            location_filter = st.multiselect("Location(s)", sorted(df["location"].unique()))
        with col2:
            tractor_filter = st.multiselect("Tractor Model(s)", sorted(df["tractor"].unique()))
            date_range = st.date_input("Date Range", [df["date"].min().date(), df["date"].max().date()])


    # --- Apply Filters ---
    if employee_filter != "All":
        df = df[df["employee"] == employee_filter]
    if customer_filter:
        df = df[df["customer"].isin(customer_filter)]
    if location_filter:
        df = df[df["location"].isin(location_filter)]
    if tractor_filter:
        df = df[df["tractor"].isin(tractor_filter)]
    if date_range and len(date_range) == 2:
        df = df[(df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))]

    # --- Display Filtered Table with Pagination ---
    st.subheader("📋 Filtered Log Entries")
    rows_per_page = 10
    total_pages = max(1, (len(df) + rows_per_page - 1) // rows_per_page)
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
    start_idx, end_idx = (page - 1) * rows_per_page, page * rows_per_page
    st.dataframe(df.sort_values("date", ascending=False).iloc[start_idx:end_idx], use_container_width=True)

    # --- Summary ---
    total_acres = df["acres"].sum()
    total_cost = df["cost"].sum()
    total_logs = len(df)

    st.markdown("### 📊 Summary Metrics")
    st.markdown(f"**Total Acres:** {total_acres:.1f} | **Total Cost:** ₹{total_cost:,} | **Total Logs:** {total_logs}")

    # --- Aggregated Summaries ---
    st.subheader("📌 Aggregated Views")
    tab1, tab2 = st.tabs(["Per Tractor", "Per Employee"])
    with tab1:
        st.dataframe(df.groupby("tractor")[["acres", "cost"]].sum().reset_index())
    with tab2:
        st.dataframe(df.groupby("employee")[["acres", "cost"]].sum().reset_index())

    st.subheader("📊 Charts")
    fig1 = px.pie(df, names="tractor", title="Tractor Usage")
    fig2 = px.bar(df.groupby("location")["acres"].sum().reset_index(), x="location", y="acres")
    fig3 = px.bar(df.groupby("employee")["acres"].sum().reset_index(), x="employee", y="acres")
    df["day"] = df["date"].dt.date
    fig4 = px.line(df.groupby("day")["cost"].sum().reset_index(), x="day", y="cost", markers=True)

    for fig in [fig1, fig2, fig3, fig4]:
        st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Download CSV", df.to_csv(index=False).encode("utf-8"), "tractor_logs.csv")

    if st.button("📄 Export Summary to PDF"):
        with st.spinner("Generating PDF..."):
            pdf = TractorPDF()
            pdf.add_banner()
            pdf.add_summary(total_acres, total_cost, total_logs)
            pdf.add_chart_page_matplotlib(df, chart_type="tractor")
            pdf.add_chart_page_matplotlib(df, chart_type="location")
            pdf.add_chart_page_matplotlib(df, chart_type="employee")
            pdf.add_chart_page_matplotlib(df, chart_type="trend")
            pdf.add_log_table(df)
    
            filename = f"tractor_summary_{datetime.now().strftime('%Y-%m-%d_%H%M')}.pdf"
            pdf_buffer = pdf.output(dest='S')
            b64 = base64.b64encode(pdf_buffer).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download PDF</a>',
                unsafe_allow_html=True
            )

