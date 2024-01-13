from dataclasses import dataclass

@dataclass
class PDFObj:
    string : str
    index : int
    char_index : int

# PDFWriter will handle all file writing
# It is specialized for the task
class PDFWriter:
    def __init__(self, width, height, num_pages, bg_color, with_text):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.drawing = False

        self.objects = []
        self.drawStream = ""
        self.textStream = ""
        
        self.data = "%PDF-1.6\n"
        self.objects.append(PDFObj("1 0 obj <</Type /Catalog /Pages 2 0 R>>\nendobj\n", 1, self.get_current_length()))

        pages_ref = ""
        for i in range(num_pages):
            pages_ref += str(len(self.objects) + 2 + i) + " 0 R"
            if i + 1 < num_pages:
                pages_ref += ' ';

        self.objects.append(PDFObj("2 0 obj <</Type /Pages /Kids [" + pages_ref + "] /Count " + str(num_pages) + ">>\nendobj\n", 2, self.get_current_length()))

        resources = ""
        contents_offset = 0
        if with_text:
            resources = "/Resources <</Font <</F1 " + str(len(self.objects) + 1 + num_pages) + " 0 R>>>>"
            contents_offset += 1

        for i in range(num_pages):
            contents_index = len(self.objects) + num_pages + contents_offset + 1
            self.objects.append(
            PDFObj(str(len(self.objects) + 1) + " 0 obj<</Type /Page /Parent 2 0 R " + resources + "/MediaBox [0 0 " + str(self.width) + " " + str(self.height) + "] /Contents " + str(contents_index) + " 0 R>>\nendobj\n", len(self.objects) + 1, self.get_current_length()))

        if with_text:
            self.objects.append(PDFObj(str(len(self.objects) + 1) + " 0 obj<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n", len(self.objects) + 1, self.get_current_length()))

    def get_current_length(self):
        return len(self.data) + sum([len(obj.string) for obj in self.objects])
        
    def start_draw(self, x, y, clear_stream):
        if self.drawing:
            print("Currently Drawing.")
            return

        self.drawing = True

        if clear_stream:
            self.draw_stream = ""
        else:
            self.draw_stream += "\n"

        self.draw_stream += "q " + str(self.bg_color[0] / 255.0) + " " + str(self.bg_color[1] / 255.0) + " " + str(self.bg_color[2] / 255.0) + " rg 0 0 " + str(self.width) + " " + str(self.height) + " re f Q\n"
        
        self.draw_stream += str(x) + " " + str(y) + " m ";

    def draw_rect(self, x, y, width, height):
        if not self.drawing:
            print("Not Currently Drawing.")
            return

        #print("(", x, y, width, height, ")")
        self.draw_stream += f"{x} {self.height - y - height} {width} {height} re "

    def end_draw(self):
        self.draw_stream += "h S Q\n"
        self.drawing = False

    def add_text(self, x, y, font_size, text, clear_stream):
        if self.text_stream != "":
            self.text_stream += ' '

        if clear_stream:
            self.text_stream = ""

        self.text_stream += f"BT /F1 {font_size} Tf {x} {self.height - y} Td({text})Tj ET"

    def empty_streams(self):
        self.draw_stream = ""
        self.text_stream = ""

    def finalize_stream_obj(self):
        self.objects.append(PDFObj(
            f"{len(self.objects) + 1} 0 obj<</Length {len(self.draw_stream) + len(self.text_stream)}>>\nstream\n{self.draw_stream}{self.text_stream}\nendstream\nendobj\n", len(self.objects) + 1, self.get_current_length()
        ))

    def finalize_pdf(self):
        for obj in self.objects:
            self.data += obj.string

        to_xref = len(self.data)

        self.data += f"xref\n0 {len(self.objects) + 1}\n0000000000 65535 f\n"

        for obj in self.objects:
            str_num = str(obj.char_index)
            while len(str_num) < 10:
                str_num = '0' + str_num
            self.data += str_num + " 00000 n\n"

        self.data += f"trailer <</Size {len(self.objects) + 1}/Root 1 0 R>>\nstartxref\n{to_xref}\n%%EOF"

    def save_pdf(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.data)