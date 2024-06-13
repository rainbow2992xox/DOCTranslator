import docx
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.shared import RGBColor
from docx.shared import Pt


# doc = docx.Document('C:\\Users\\Rainbow\\Downloads\\MK-3543-008-00-DEMO-CN (6).docx')
#
#
#
# # doc = docx.Document('C:\\Users\\Rainbow\\Desktop\\Odoo\\DocTranslator\\data\\chenyufe\\alignment\\MK-3543-007-00-DEMO-CN.docx')
# # doc.styles.default("Normal")
# for paragraph in doc.paragraphs:
#     # paragraph.style.name = 'MyBodyText'
#     paragraph.insert_paragraph_before(paragraph.text, 'MyBodyText')
#     paragraph.clear()

# for p in doc.paragraphs:
#     print(p)
#
# doc2 = docx.Document('C:\\Users\\Rainbow\\Desktop\\Odoo\\DocTranslator\\data\\chenyufe\\alignment\\MK-3543-007-00-DEMO-CN.docx')
# for p in doc2.paragraphs:
#     print(p)
# 转换文本框为普通文本
# 保存文档
# doc.save('C:\\Users\\Rainbow\\Downloads\\MK-3543-008-00-DEMO-CN (convert).docx')

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def remove_framePr_from_paragraphs(doc_path):
    doc = Document(doc_path)

    for paragraph in doc.paragraphs:
        _remove_framePr(paragraph._element)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _remove_framePr(paragraph._element)

    doc.save('C:\\Users\\Rainbow\\Downloads\\MK-3543-008-00-DEMO-CN (convert).docx')


def _remove_framePr(paragraph_element):
    for pPr in paragraph_element.findall(qn('w:pPr')):
        for framePr in pPr.findall(qn('w:framePr')):
            pPr.remove(framePr)
        for pStyle in pPr.findall(qn('w:pStyle')):
            pPr.remove(pStyle)
        # 添加默认样式
        new_pStyle = OxmlElement('w:pStyle')
        new_pStyle.set(qn('w:val'), 'Normal')
        pPr.append(new_pStyle)


# 示例用法
remove_framePr_from_paragraphs('C:\\Users\\Rainbow\\Downloads\\MK-3543-008-00-DEMO-CN (6).docx')

# Example usage
