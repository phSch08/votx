from fpdf import FPDF


class PdfGenerator():

    def __init__(self, headline1: str, headline2: str, dateline: str, tokenDescription: str):
        self.headline1 = headline1
        self.headline2 = headline2
        self.dateline = dateline
        self.tokenDescription = tokenDescription

    def generateRegistrationPDF(self, tokenList: list[tuple[str, list[str]]]):
        pdf = FPDF(orientation="P", unit="mm", format="A4")

        pdf.set_font("helvetica", style="", size=15)

        for idx, token in enumerate(tokenList):
            if idx % 3 == 0:
                pdf.add_page()
                pdf.set_xy(0, 0)
            pdf.cell(w=210, h=15, new_x="LEFT", new_y="NEXT")
            pdf.set_font("helvetica", style="B", size=25)
            pdf.cell(w=210, h=9, text=self.headline1,
                     align="C", new_x="LEFT", new_y="NEXT")
            pdf.set_font("helvetica", style="", size=12)
            pdf.cell(w=210, h=5, new_x="LEFT", new_y="NEXT")
            pdf.cell(w=210, h=5, text=self.headline2,
                     align="C", new_x="LEFT", new_y="NEXT")
            pdf.cell(w=210, h=5, text=self.dateline,
                     align="C", new_x="LEFT", new_y="NEXT")

            pdf.cell(w=210, h=10, new_x="LEFT", new_y="NEXT")
            pdf.cell(w=210, h=5, text=" · ".join(token[1]),
                     align="C", new_x="LEFT", new_y="NEXT")
            pdf.cell(w=210, h=10, new_x="LEFT", new_y="NEXT")

            pdf.cell(w=100, h=7, text=self.tokenDescription, align="C",
                     new_x="LEFT", new_y="NEXT", border="RTL", center=True)

            pdf.set_font("helvetica", style="B", size=20)
            pdf.cell(w=100, h=10, text=token[0], align="C",
                     new_x="LEFT", new_y="NEXT", border="RBL", center=True)

            pdf.set_x(0)
            pdf.cell(w=210, h=11, new_x="LEFT", new_y="NEXT", border="B")

        return pdf


if __name__ == '__main__':
    gen = PdfGenerator("Wahlschein", "Vollversammlung",
                       "29.02.2025", "Ihr Wahlcode")
    gen.generateRegistrationPDF(
        [
            ("12345 - 67890 - 24680", ["Jugendwahl", "Vorstandswahl", "Entlastung Vorstand"]),
            ("12345 - 67890 - 24680", ["Jugendwahl"]),
        ]).output("test.pdf")
