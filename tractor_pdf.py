from fpdf import FPDF
from fpdf.enums import XPos, YPos 
from datetime import datetime
import matplotlib.pyplot as plt
import io
import pandas as pd
import os

class TractorPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf")
        self.set_font("DejaVu", size=12)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.set_text_color(120)
        self.cell(0, 10, f"Tractor Logger | Page {self.page_no()}", align="C")

    def add_banner(self):
        self.add_page()  # ✅ Add this to create a page
        banner_path = os.path.join("assets", "tractor_banner.png")
        if os.path.exists(banner_path):
            self.image(banner_path, x=10, y=10, w=180)
            self.ln(30)


    def add_summary(self, total_acres, total_cost, total_logs):
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, f"Total Acres: {total_acres:.1f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"Total Cost: ₹{total_cost:,}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"Total Logs: {total_logs}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_chart_page_matplotlib(self, df, chart_type="tractor"):
        """Create a chart page using Matplotlib (used only in PDF export)."""
        self.add_page()
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, f"{chart_type.title()} Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        fig, ax = plt.subplots(figsize=(8, 4))

        if chart_type == "tractor" and "tractor" in df.columns and "acres" in df.columns:
            agg = df.groupby("tractor")["acres"].sum()
            ax.bar(agg.index, agg.values, color='skyblue')
            ax.set_title("Tractor Usage (Acres)")
            ax.set_ylabel("Acres")

        elif chart_type == "location" and "location" in df.columns and "acres" in df.columns:
            agg = df.groupby("location")["acres"].sum()
            ax.bar(agg.index, agg.values, color='lightgreen')
            ax.set_title("Acres by Location")
            ax.set_ylabel("Acres")

        elif chart_type == "employee" and "employee" in df.columns and "acres" in df.columns:
            agg = df.groupby("employee")["acres"].sum()
            ax.bar(agg.index, agg.values, color='salmon')
            ax.set_title("Acres by Employee")
            ax.set_ylabel("Acres")

        elif chart_type == "trend" and "date" in df.columns and "cost" in df.columns:
            df["day"] = pd.to_datetime(df["date"]).dt.date
            trend = df.groupby("day")["cost"].sum()
            ax.plot(trend.index, trend.values, marker='o')
            ax.set_title("Daily Cost Trend")
            ax.set_ylabel("Cost")

        ax.set_xlabel(chart_type.title())
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        self.image(buf, x=10, w=180)

    def add_log_table(self, df):
        self.add_page()
        self.set_font("DejaVu", size=11)
        self.cell(0, 10, "Log Summary Table", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        col_width = self.w / len(df.columns) - 5
        th = 8

        for col in df.columns:
            self.cell(col_width, th, str(col), border=1)
        self.ln(th)

        for i, row in df.iterrows():
            if i >= 50:
                self.cell(0, th, "... Table truncated to 50 rows ...", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                break
            for val in row:
                self.cell(col_width, th, str(val), border=1)
            self.ln(th)

    def export(self, filename="tractor_summary.pdf"):
        pdf_bytes = self.output(dest="S")
        return io.BytesIO(pdf_bytes)
