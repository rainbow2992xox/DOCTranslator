import base64
import json
import jwt
import requests
import os
from odoo import models, fields, api
from ..util.util import *
from ..util.doc_util import *
from odoo.exceptions import ValidationError, UserError
import xml.etree.ElementTree as ET
from pdf2docx import Converter
from spire.pdf.common import *
from spire.pdf import *
import spire.pdf as pdf

# 设置许可证密钥
License.SetLicenseKey(os.environ.get("spire_license"))


class doc_file(models.Model):
    _name = 'doc.file'
    name = fields.Char(string='File name')
    file = fields.Binary(string='File')
    doc_definition = fields.Many2one('doc.definition', string='PharmaDoc type')
    doc_paragraphs = fields.One2many('doc.paragraph', 'doc_file', string='Paragraphs', readonly=True)
    lang = fields.Many2one('doc.lang', compute='_compute_lang', string='Language', readonly=True)
    doc_translation_files_id = fields.Many2one('doc.translation.files', string='Translation files')
    create_uid = fields.Many2one('res.users', string='Created by')
    msd_usr_id = fields.Char(related='create_uid.name', string='MSD ID', readonly=True)
    origin_file = fields.Many2one('doc.file', string='Origin File', readonly=True)


    @api.constrains('file')
    def check_file_type(self):
        lang_list = [l.name for l in self.env['doc.lang'].search([])]
        for rec in self:
            filename, extension = os.path.splitext(rec.name)
            if extension.lower() not in [".docx"]:
                raise UserError("Only DOCX files are supported. Please convert PDF files to DOCX using Adobe Acrobat before uploading.")
            if_match = False
            for lang in lang_list:
                if filename.lower().endswith(lang.lower()):
                    if_match = True

            if not if_match:
                raise UserError("Only filenames with the following suffixes are supported: %s" % (" , ".join(lang_list)))

    @api.depends('name')
    def _compute_lang(self):
        lang_list = [l.name for l in self.env['doc.lang'].search([])]
        for rec in self:
            if not rec.name:
                rec.lang = False
                continue
            rec.lang = False
            filename, extension = os.path.splitext(rec.name)
            for lang in lang_list:
                if filename.lower().endswith(lang.lower()):
                    rec.lang = self.env['doc.lang'].search([('name', '=', lang)])[0].id
                    break

    def encode(self, payload):
        return jwt.encode(payload, '123456', algorithm='HS256')

    def pdf2docx(self, rec):
        temp_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
        pdf_file_path = os.path.join(temp_folder_path, rec.name)
        binary_data = base64.b64decode(rec.file)
        with open(pdf_file_path, 'wb') as f:
            f.write(binary_data)
        print(pdf_file_path)

        docx_file_path = pdf_file_path.replace('.pdf', '.docx').replace('.PDF', '.docx')
        # pdf2docx convert pdf to docx
        # cv = Converter(pdf_file_path)
        # cv.convert(docx_file_path)  # all pages by default
        # cv.close()

        # spire.PDF convert pdf to docx
        doc = PdfDocument()
        doc.LoadFromFile(pdf_file_path)
        doc.SaveToFile(docx_file_path, FileFormat.DOCX)
        doc.Close()

        with open(docx_file_path, 'rb') as file:
            file_data = file.read()
            rec.write({'file': base64.b64encode(file_data), 'name': os.path.basename(docx_file_path)})

        with open(pdf_file_path, 'rb') as file:
            file_data = file.read()
            origin_file = self.env['doc.file'].sudo().create({'file': base64.b64encode(file_data), 'name': os.path.basename(docx_file_path), 'lang': rec.lang.id, 'msd_usr_id': rec.msd_usr_id})
            rec.write({'origin_file': origin_file.id})
            # 防止重复转换
            origin_file.write({'name': os.path.basename(pdf_file_path)})

        os.remove(pdf_file_path)
        os.remove(docx_file_path)

    def create(self, vals):
        translation_files_id = self.env.context.get('default_translation_files_id')
        task_id = self.env.context.get('default_task_id')

        new_doc_file = super(doc_file, self).create(vals)

        # 转换pdf
        filename, extension = os.path.splitext(new_doc_file.name)
        if extension.lower() == ".pdf":
            self.pdf2docx(new_doc_file)

        if translation_files_id:
            translation_files_field = self.env.context.get('default_type')
            vals['doc_translation_files_id'] = translation_files_id
            doc_translation_files = self.env['doc.translation.files'].browse(translation_files_id)
            doc_translation_files.write({translation_files_field: new_doc_file.id})

        if task_id:
            task_field = self.env.context.get('default_type')
            doc_task = self.env['doc.task'].browse(task_id)
            doc_task.write({task_field: new_doc_file.id})

        self.action_extract(new_doc_file.file, new_doc_file)
        self.env.cr.commit()

        return new_doc_file

    def unlink(self):
        # 删除与当前记录关联的所有doc_paragraphs记录
        self.mapped('doc_paragraphs').unlink()
        return super(doc_file, self).unlink()

    def action_extract(self, file_binary, doc_file):
        temp_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
        temp_file_path = os.path.join(temp_folder_path, doc_file.name)
        binary_data = base64.b64decode(file_binary)
        with open(temp_file_path, 'wb') as f:
            f.write(binary_data)
        print(temp_file_path)
        p_list = get_paragraphs(temp_file_path)
        print(len(p_list))
        print("----------------------------开始新建段落------------------------------")
        self.env['doc.paragraph'].sudo().create(
            [{'text': p['text'], 'lang': doc_file.lang.id, 'title': p['title'], 'type': '1',
              'doc_file': doc_file.id, 'paragraph_text_idx': p['paragraph_text_idx']} for p in p_list if p['type'] == 'title'])
        self.env['doc.paragraph'].sudo().create(
            [{'text': p['text'], 'lang': doc_file.lang.id, 'title': p['title'], 'type': '2',
              'doc_file': doc_file.id, 'paragraph_text_idx': p['paragraph_text_idx']} for p in p_list if p['type'] == 'text'])
        t_list = get_tables(temp_file_path)
        print(len(t_list))
        print("----------------------------开始新建表格------------------------------")
        self.env['doc.paragraph'].sudo().create([{'text': json.dumps(t[1], ensure_ascii=False),
                                                  'lang': doc_file.lang.id, 'type': '3', 'doc_file': doc_file.id} for t
                                                 in t_list])
        os.remove(temp_file_path)
