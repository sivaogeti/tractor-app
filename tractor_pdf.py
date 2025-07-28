from fpdf import FPDF
from fpdf.enums import XPos, YPos 
from datetime import datetime
import plotly.io as pio
import io
import plotly.io as pio
pio.kaleido.scope.default_format = "png"

class TractorPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf")
        self.set_font("DejaVu", size=12)

    def header(self):
        # Optional: add a header on each page
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.set_text_color(120)
        self.cell(0, 10, f"Tractor Logger | Page {self.page_no()}", align="C")

    def add_banner(self, banner_path="images/tractor_banner.png"):
        self.image(banner_path, x=10, y=10, w=180)
        self.set_y(200)

    def add_summary(self, total_acres, total_cost, total_logs):
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, f"Total Acres: {total_acres:.1f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"Total Cost: ₹{total_cost:,}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"Total Logs: {total_logs}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_chart_page(self, fig, title=""):
        self.add_page()
        if title:
            self.set_font("DejaVu", size=12)
            self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        img_bytes = pio.to_image(fig, format="png", width=800, height=400, scale=2)
        img_stream = io.BytesIO(img_bytes)
        self.image(img_stream, x=10, w=180)

    def add_log_table(self, df):
        self.add_page()
        self.set_font("DejaVu", size=11)
        self.cell(0, 10, "Log Summary Table", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        col_width = self.w / len(df.columns) - 5
        th = 8  # row height

        # Table header
        for col in df.columns:
            self.cell(col_width, th, str(col), border=1)
        self.ln(th)

        # Table rows (limit 50 for sanity)
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
