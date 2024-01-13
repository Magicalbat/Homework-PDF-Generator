from pdfwriter import PDFWriter
from enum import Enum, auto

import math

class SetTypes(Enum):
    ALL = auto()
    EVEN = auto()
    ODD = auto()
    EVERY = auto()

class PageGenerator:
    def __init__(self, problems_text, height, padding, box_num, bg_color):
        #print(problems_text, type(problems_text))
        self.problems_text = problems_text
        self.problems = []
        self.parse_problems(self.problems_text)

        self.height = height
        self.width = height * (17.0/22.0)

        self.padding = (self.width * padding[0], self.height * padding[1])
        self.box_num = tuple(box_num)
        self.box_dim = ((self.width * 0.75) / self.box_num[0], (self.height * 0.75) / self.box_num[1])

        self.bg_color = bg_color

    def create_pdf(self, file_path=None):
        num_pages = math.ceil(len(self.problems) / (self.box_num[0] * self.box_num[1]))

        pdf_writer = PDFWriter(self.width, self.height, num_pages, self.bg_color, True)

        i = 0
        for j in range(num_pages):
            pdf_writer.empty_streams()
            pdf_writer.start_draw(self.padding[0], self.padding[1], True);

            pdf_writer.add_text(24, 24, 16, self.problems_text, False)

            for y in range(self.box_num[1]):
                for x in range(self.box_num[0]):
                    if i < len(self.problems) and self.problems[i]:
                        pdf_writer.add_text(self.padding[0] + self.box_dim[0] * x + 4, self.padding[1] + self.box_dim[1] * y + 18, 16, str(self.problems[i]), False)
                        pdf_writer.draw_rect(self.padding[0] + self.box_dim[0] * x, self.padding[1] + self.box_dim[1] * y, self.box_dim[0], self.box_dim[1])
                        
                    i += 1
            pdf_writer.end_draw()
            pdf_writer.finalize_stream_obj()
            
        pdf_writer.finalize_pdf()
        if type(file_path) == str: 
            pdf_writer.save_pdf(file_path)
        else:
            return pdf_writer.data
            
        return ""

    def parse_problems(self, problems_text):
        numbers_str = problems_text.split(':')[-1].replace(' ', '')

        for elem in numbers_str.split(','):
            if elem.isnumeric():
                self.problems.append(int(elem))
                continue
            
            set_type = SetTypes.ALL
            every_factor = 0

            if "even" in elem or "(E)" in elem:
                set_type = SetTypes.EVEN
                elem = elem[:-4]
            elif "odd" in elem or "(O)" in elem:
                set_type = SetTypes.ODD
                elem = elem[:-3]
            elif "every" in elem:
                set_type = SetTypes.EVERY
                every_factor = elem[elem.find("every") + 5:]
                elem = elem[:-5-len(every_factor)]
                every_factor = int(every_factor)

            elem = elem.split('-')
            start = int(elem[0])
            end = int(elem[1])
            for i in range(start, end+1):
                if set_type == SetTypes.EVEN:
                    if i % 2 != 0:
                        continue
                elif set_type == SetTypes.ODD:
                    if i % 2 == 0:
                        continue
                elif set_type == SetTypes.EVERY:
                    if (i - start) % every_factor != 0:
                        continue
                    
                self.problems.append(i)