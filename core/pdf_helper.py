import base64
import io

from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen.canvas import Canvas


class GenerateFromTemplate:
    def __init__(self, template_bytes):
        self.output = None
        buffer = base64.b64decode(template_bytes)
        pdf_stream = io.BytesIO(buffer)

        self.template_pdf = PdfReader(pdf_stream)
        # self.template_page = self.template_pdf.pages[0]
        self.template_page = self.template_pdf.pages

        self.packet = io.BytesIO()
        self.c = Canvas(self.packet, pagesize=(self.template_page[0].mediabox.width, self.template_page[0].mediabox.height))

    def draw_grid(self):
        width = self.template_page[0].mediabox.width
        height = self.template_page[0].mediabox.height
        grid_size = 10

        for x in range(0, int(width), grid_size):
            self.c.drawString(x, 0, str(x))
            self.c.line(x, 0, x, height)

        for y in range(0, int(height), grid_size):
            self.c.drawString(0, y, str(y))
            self.c.line(0, y, width, y)

    def add_text(self, text, point):
        if text is None:
            text = "-"
        text = str(text)
        self.c.setFont('Times-Roman', 8)
        self.c.drawString(point[0], point[1], text)

    def merge(self):
        self.c.save()
        self.packet.seek(0)
        result_pdf = PdfReader(self.packet)
        result = result_pdf.pages[0]

        self.output = PdfWriter()

        op = Transformation().rotate(0).translate(tx=0, ty=0)
        result.add_transformation(op)
        for index, page in enumerate(self.template_page):
            if index == 0:
                page.merge_page(result)
                self.output.add_page(page)
            else:
                page.merge_page(self.template_page[index])
                self.output.add_page(page)


    def generate(self, dest):
        output_stream = open(dest, "wb")
        self.output.write(output_stream)
        output_stream.close()

    def return_bytes(self):
        # writer = PdfWriter()
        with io.BytesIO() as bytes_stream:
            self.output.write(bytes_stream)
            return bytes_stream.getvalue()
