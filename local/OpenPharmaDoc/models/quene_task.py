from odoo import models, fields, api
import math
from ..util.util import *
from docx import Document
import base64
import os
from ..util.agent_util import *
import statistics
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)
# import translator.Translator_main as ts

# from ..util.translator.Translator_main import *
import io

from ..util.agent_util import *
from ..util.doc_util import *
import pandas as pd


class quene_task(models.Model):
    _name = 'doc.quene.task'
    type = fields.Selection([('对齐', '对齐'), ('实体提取', '实体提取'), ('翻译', '翻译')], string='Type', default='1',
                            readonly=True)
    status = fields.Selection([('1', '未开始'), ('2', '进行中'), ('3', '已完成'), ('4', '已失败')], string='Status',
                              default='1')
    target_lang = fields.Many2one('doc.lang', 'Target language', readonly=True)
    source_lang = fields.Many2one('doc.lang', 'Source language', readonly=True)
    target_file = fields.Many2one('doc.file', 'Target file', readonly=True)
    source_file = fields.Many2one('doc.file', 'Source file', readonly=True)
    target_align_paragraphs = fields.One2many('doc.paragraph', 'target_quene_task_id', string='Target align paragraph')
    source_align_paragraphs = fields.One2many('doc.paragraph', 'source_quene_task_id', string='Source align paragraph')
    source_text = fields.Text(string='Source text', readonly=True)
    target_text = fields.Text(string='Target text', readonly=True)
    task_id = fields.Many2one('doc.task', string='AI Task', readonly=True)
    translation_file_id = fields.Many2one('doc.translation.files', string='Corpus Files', readonly=True)
    score = fields.Float(string='Trans Score', readonly=True)

    def upload(self, msd_id=None):
        # folder_path = 'C:\\Users\\Rainbow\\Desktop\\Odoo\\DocTranslator\\data'
        folder_path = '/home'
        translation_files = import_corpus(folder_path, msd_id)
        fail_list = []
        for t in translation_files:
            print("-------------------------------开始导入----------------------------------")
            print(t)
            print("-------------------------------开始导入----------------------------------")
            try:
                with open(t['en'], 'rb') as file:
                    file_data = file.read()
                    en_doc_file = self.env['doc.file'].sudo().create(
                        {'file': base64.b64encode(file_data), 'msd_usr_id': t['msd_usr_id'],
                         'name': os.path.basename(t['en']), 'lang': 1})

                with open(t['cn'], 'rb') as file:
                    file_data = file.read()
                    cn_doc_file = self.env['doc.file'].sudo().create(
                        {'file': base64.b64encode(file_data), 'msd_usr_id': t['msd_usr_id'],
                         'name': os.path.basename(t['cn']), 'lang': 2})

                tf = self.env['doc.translation.files'].sudo().create({'target': cn_doc_file.id, 'source': en_doc_file.id})
                en_doc_file.write({'doc_translation_files_id': tf.id})
                cn_doc_file.write({'doc_translation_files_id': tf.id})
            except Exception as e:
                fail_list.append(t)
                print(e)
        print("-----------------------------导入失败文件清单---------------------------------")
        print(fail_list)
        print("-----------------------------导入失败文件清单---------------------------------")

    def if_align_done(self, source_text, target_text):
        p = self.env['doc.translation.paragraphs'].sudo().search([('source_paragraph', '=', source_text), ('target_paragraph', '=', target_text)])
        if p:
            return True
        else:
            return False

    def get_technical_terms(self, source_lang, target_lang):
        terms = self.env['doc.translation.technical.terms'].search([('source_lang', '=', source_lang.id), ('target_lang', '=', target_lang.id)])
        target_technical_terms = [t.target_term for t in terms]
        return target_technical_terms

    def start_task(self):
        align_tasks = self.env["doc.quene.task"].sudo().search([("status", "=", "1")], order='create_date asc',
                                                               limit=20)
        processing_align_tasks = self.env["doc.quene.task"].sudo().search([("status", "=", "2")],
                                                                          order='create_date asc')

        # 没有进行中的任务则执行
        if not processing_align_tasks.ids:
            for rec in align_tasks:
                rec.status = '2'
                self.env.cr.commit()
                if rec.type == '对齐':
                    #目前只对齐标题和正文
                    target_list = rec.env['doc.paragraph'].sudo().search([('id', 'in', rec.target_align_paragraphs.ids), ('type', 'in', ('1', '2'))])
                    source_list = rec.env['doc.paragraph'].sudo().search([('id', 'in', rec.source_align_paragraphs.ids), ('type', 'in', ('1', '2'))])
                    text_dict = {
                        getLabel(rec.source_lang, 'name'): [{"id": p.id, "type": getLabel(p, 'type'), "text": p['text']}
                                                            for p in source_list],
                        getLabel(rec.target_lang, 'name'): [{"id": p.id, "type": getLabel(p, 'type'), "text": p['text']}
                                                            for p in target_list]
                    }
                    align_res = agent_align(text_dict)
                    if align_res:
                        print(align_res)
                        for item in align_res:
                            self.env['doc.translation.paragraphs'].sudo().create({'target': item[getLabel(rec.target_lang, 'name')]['id'], 'source': item[getLabel(rec.source_lang, 'name')]['id']})
                            source_paragraph = self.env['doc.paragraph'].sudo().search([('id', '=', item[getLabel(rec.source_lang, 'name')]['id'])])
                            msd_usr_id = source_paragraph.doc_file.msd_usr_id
                            data = {getLabel(rec.source_lang, 'name'): item[getLabel(rec.source_lang, 'name')]['text'], getLabel(rec.target_lang, 'name'): item[getLabel(rec.target_lang, 'name')]['text']}
                            # 判断没有对齐过的再添加至向量数据库
                            if not self.if_align_done(item[getLabel(rec.source_lang, 'name')]['text'], item[getLabel(rec.target_lang, 'name')]['text']):
                                add_data(data, msd_usr_id if msd_usr_id else None)
                        rec.status = '3'
                    else:
                        rec.status = '4'
                    break

                if rec.type == '翻译':
                    # 匹配专业词汇
                    # target_technical_terms = self.get_technical_terms(rec.source_lang, rec.target_lang)
                    # trans_technical_terms = []
                    # for t in target_technical_terms:
                    #     if t in rec.source_text:
                    #         trans_technical_terms.append(t)
                    trans_technical_terms = {}
                    # TODO 临时代码
                    temp_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
                    temp_file_path = os.path.join(temp_folder_path, "MeddraLLT2023SEP.xlsx")
                    df = pd.read_excel(temp_file_path)
                    for index, row in df.iterrows():
                        if row['English'] in rec.source_text:
                            trans_technical_terms[row['English']] = [row['中文']]

                    msd_usr_id = rec.source_file.msd_usr_id
                    agent_res = agent_translate(rec.source_text, getLabel(rec.source_lang, 'name'), getLabel(rec.target_lang, 'name'), trans_technical_terms, msd_usr_id if msd_usr_id else None)
                    rec.target_text = agent_res[0]
                    rec.score = agent_res[1]
                    rec.status = '3'
                    self.env.cr.commit()
                    # 判断是否全部翻译完,翻译完生成文件
                    doc_quene_tasks = self.env['doc.quene.task'].sudo().search([("source_file", "=", rec.source_file.id), ("status", "in", ("1", "2", "4"))])
                    if not doc_quene_tasks.ids:
                        print("-------生成文件-------")
                        rec.task_id.create_output()
