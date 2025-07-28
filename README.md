# 🚜 Tractor Log Admin Dashboard

A private admin dashboard built with [Streamlit](https://streamlit.io/) to manage tractor ploughing activity logs. Designed for internal use by field employees and supervisors.

## ✨ Features

- 🔐 Login authentication for field staff and admins
- 🧾 Log daily tractor activity: date, driver, hours, fields, etc.
- 📊 Aggregate summaries by tractor or employee
- 📤 Export log data as PDF reports
- 🌗 Toggle light/dark theme
- 📱 Mobile-friendly layout
- 🧹 Auto-clear form after submission
- 📄 Paginated views for long tables

## 🗂️ File Structure

- `app.py` – Main Streamlit dashboard
- `tractor_pdf.py` – PDF report generator
- `data.py` – Data read/write to local JSON (`db.json`)
- `auth.py` – User login/roles
- `db.json` – Local storage for log entries (temporary)
- `requirements.txt` – App dependencies

## 🚀 Deploy on Streamlit Cloud

1. Push this project to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your repo and set `app.py` as the entry point
4. Done!

> ⚠️ Note: `db.json` is not persistent in Streamlit Cloud. Consider connecting to Firebase, Supabase, or Google Sheets for long-term storage.

## 📦 Installation (Local)

```bash
pip install -r requirements.txt
streamlit run app.py

##  License
“This app is only meant for internal/company use and should not be sold or used by others commercially.”
