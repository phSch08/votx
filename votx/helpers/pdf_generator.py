from datetime import datetime

from fpdf import FPDF


def generate_registration_pdf(
    headline1: str,
    headline2: str,
    dateline: str,
    token_description: str,
    url: str,
    token_list: list[tuple[str, list[str]]],
):
    pdf = FPDF(orientation="P", unit="mm", format="A4")

    pdf.set_font("helvetica", style="", size=15)

    for idx, token in enumerate(token_list):
        if idx % 3 == 0:
            pdf.add_page()
            pdf.set_xy(0, 0)
        pdf.cell(w=210, h=7, new_x="LEFT", new_y="NEXT")
        pdf.set_font("helvetica", style="B", size=25)
        pdf.cell(w=210, h=9, text=headline1, align="C", new_x="LEFT", new_y="NEXT")
        pdf.set_font("helvetica", style="", size=12)
        pdf.cell(w=210, h=3, new_x="LEFT", new_y="NEXT")
        pdf.cell(w=210, h=5, text=headline2, align="C", new_x="LEFT", new_y="NEXT")
        pdf.cell(w=210, h=5, text=dateline, align="C", new_x="LEFT", new_y="NEXT")

        pdf.cell(w=210, h=5, new_x="LEFT", new_y="NEXT")
        pdf.cell(
            w=210, h=5, text=" · ".join(token[1]), align="C", new_x="LEFT", new_y="NEXT"
        )

        pdf.cell(w=210, h=5, new_x="LEFT", new_y="NEXT")
        pdf.set_font("helvetica", style="B", size=20)
        pdf.cell(w=210, h=15, text=url, align="C", new_x="LEFT", new_y="NEXT")
        pdf.set_font("helvetica", style="", size=12)
        pdf.cell(w=210, h=5, new_x="LEFT", new_y="NEXT")

        pdf.cell(
            w=100,
            h=7,
            text=token_description,
            align="C",
            new_x="LEFT",
            new_y="NEXT",
            border="RTL",
            center=True,
        )

        pdf.set_font("helvetica", style="B", size=20)
        pdf.cell(
            w=100,
            h=10,
            text=token[0],
            align="C",
            new_x="LEFT",
            new_y="NEXT",
            border="RBL",
            center=True,
        )

        pdf.set_x(0)
        pdf.cell(w=210, h=11, new_x="LEFT", new_y="NEXT", border="B")

    return pdf


def generate_ballot_protocol(
    ballot_title: str,
    results: list[tuple[str, int]],
    events: list[tuple[datetime, str]],
    votes: list[tuple[str, str]],
):
    class PDF(FPDF):
        def footer(self):
            self.set_font("helvetica", style="B", size=15)
            self.set_y(-15)
            self.set_font("helvetica", style="I", size=7)
            self.set_text_color(100)
            self.cell(w=0, h=10, text=f"Seite {self.page_no()} von {{nb}}", align="C")

        def header(self):
            self.set_font("helvetica", style="B", size=15)
            self.set_fill_color(116, 64, 190)
            self.set_xy(0, 0)
            self.cell(w=210, h=25, fill=True)

            self.set_text_color(255)
            self.set_xy(15, 0)
            self.cell(
                w=120, h=25, text="Wahlprotokoll", align="L", new_x="LEFT", new_y="NEXT"
            )

            self.image(
                "votx/static/logo.svg", x=180, y=5, w=20, h=15, keep_aspect_ratio=True
            )
            self.set_xy(20, 30)

    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_font("helvetica", style="B", size=15)
    pdf.add_page()

    pdf.cell(w=10, h=10, new_x="LEFT", new_y="NEXT")
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(w=40, text="Wahltitel", new_x="RIGHT", new_y="TOP")
    pdf.set_font("helvetica", style="", size=11)
    pdf.multi_cell(w=100, text=ballot_title, new_y="NEXT")

    pdf.set_x(20)
    pdf.cell(w=10, h=10, new_x="LEFT", new_y="NEXT")

    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(h=6, w=30, text="Ergebnis", new_x="RIGHT", new_y="TOP")
    pdf.set_font("helvetica", style="", size=11)
    for r in results:
        pdf.set_x(60)
        pdf.set_font("helvetica", style="I", size=7)
        pdf.set_text_color(100)
        pdf.cell(h=6, w=30, text=f"Stimmen: {r[1]}", new_x="RIGHT", new_y="TOP")
        pdf.set_font("helvetica", style="", size=11)
        pdf.set_text_color(0)
        pdf.multi_cell(h=6, w=80, text=r[0], new_y="NEXT")

    pdf.set_x(20)
    pdf.cell(w=10, h=10, new_x="LEFT", new_y="NEXT")
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(h=6, w=60, text="Ereignisprotokoll", new_x="RIGHT", new_y="TOP")

    for e in events:
        pdf.set_x(60)
        pdf.set_font("helvetica", style="I", size=7)
        pdf.set_text_color(100)
        pdf.cell(
            h=6,
            w=30,
            text=e[0].strftime("%d.%m.%y %H:%M:%S"),
            new_x="RIGHT",
            new_y="TOP",
        )
        pdf.set_font("helvetica", style="", size=11)
        pdf.set_text_color(0)
        pdf.multi_cell(h=6, w=80, text=e[1], new_y="NEXT")

    pdf.set_x(20)
    pdf.cell(w=10, h=10, new_x="LEFT", new_y="NEXT")
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(h=6, w=60, text="Abgegebene Stimmen", new_x="LEFT", new_y="NEXT")
    for vote in votes:
        pdf.set_x(20)
        pdf.set_font("helvetica", style="I", size=7)
        pdf.set_text_color(100)
        pdf.cell(h=6, w=40, text=vote[1], new_x="RIGHT", new_y="TOP")
        pdf.set_font("helvetica", style="", size=11)
        pdf.set_text_color(0)
        pdf.cell(h=6, w=130, text=vote[0], new_x="RIGHT", new_y="NEXT", border="")

    return pdf
