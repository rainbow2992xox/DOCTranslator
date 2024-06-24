from odoo import models, fields, api
import math
from ..util.util import *
from ..util.doc_util import *
from ..util.agent_util import *
import zipfile
import io
import base64
import json
import os
import sys



class doc_translation_files(models.Model):
    _name = 'doc.translation.files'
    target = fields.Many2one('doc.file', string='Target file', readonly=True)
    source = fields.Many2one('doc.file', string='Source file', readonly=True)
    target_file = fields.Binary(related='target.file', readonly=True, store=False)
    source_file = fields.Binary(related='source.file', readonly=True, store=False)
    queue_task_id = fields.One2many('doc.quene.task', 'translation_file_id', 'queue_task', readonly=True)
    status = fields.Selection(related='queue_task_id.status', string='Status', readonly=True)
    if_align = fields.Selection([('1', '未对齐'), ('2', '进行中'), ('3', '已对齐'), ('4', '对齐失败')], string='If align', default='1',
                                compute="_compute_if_align", readonly=True)
    source_msd_usr_id = fields.Char(related='source.msd_usr_id', string='Source msd_usr_id', readonly=True)
    @api.depends('status')
    def _compute_if_align(self):
        # 队列任务失败则对齐失败，队列任务成功则对齐成功
        for rec in self:
            if rec.queue_task_id:
                for task in rec.queue_task_id:
                    if task.status == '4':
                        rec.if_align = '4'

                if_done = True
                for task in rec.queue_task_id:
                    if task.status != '3':
                        if_done = False

                if if_done:
                    rec.if_align = '3'
                else:
                    rec.if_align = '2'
            else:
                rec.if_align = '1'
            # if rec.status:
            #     if rec.status == '3':
            #         rec.if_align = '3'
            #     elif rec.status in ['1', '2']:
            #         rec.if_align = '2'
            #     elif rec.status == '4':
            #         rec.if_align = '1'
            #         self.env['doc.paragraph'].sudo().search([('doc_file', '=', rec.source.id)]).unlink()
            #         self.env['doc.paragraph'].sudo().search([('doc_file', '=', rec.target.id)]).unlink()
            # else:
            #     rec.if_align = '1'

    def open_target_file_create_form(self):
        # 获取当前记录的 id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload target file',
            'res_model': 'doc.file',  # 替换为您的模型名称
            'view_mode': 'form',
            'view_id': self.env.ref('OpenPharmaDoc.doc_file_view_form').id,
            'target': 'new',
            'context': {'default_translation_files_id': self.id, 'default_type': 'target'},  # 将当前记录的 id 传递给新建记录的表单窗口
        }

    def open_source_file_create_form(self):
        # 获取当前记录的 id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload source file',
            'res_model': 'doc.file',  # 替换为您的模型名称
            'view_mode': 'form',
            'view_id': self.env.ref('OpenPharmaDoc.doc_file_view_form').id,
            'target': 'new',
            'context': {'default_translation_files_id': self.id, 'default_type': 'source'},  # 将当前记录的 id 传递给新建记录的表单窗口
        }

    def create_doc_file(self, file_path, usr_id, doc_definition_id, lang_id):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        vals = {
            'name': os.path.basename(file_path),
            'file': base64.b64encode(file_data),
            'lang': lang_id,
            'msd_usr_id': usr_id
        }
        doc_file = self.env['doc.file'].sudo().create(vals)
        return doc_file

    def if_align_done(self, source_text, target_text):
        p = self.env['doc.translation.paragraphs'].sudo().search([('source_paragraph', '=', source_text), ('target_paragraph', '=', target_text)])
        if p:
            return True
        else:
            return False


    def align(self):
        for rec in self:
            # 修改状态
            if rec.if_align == '1':
                rec.if_align = '2'

                # 先对其段落标题
                target_title_list = self.env['doc.paragraph'].sudo().search(
                    [('status', '=', '1'), ('lang', '=', getLabel(rec.target.lang, 'name')), ('type', '=', '1'),
                     ('doc_file', '=', rec.target.id)])
                tt_list = []
                for p in target_title_list:
                    if p['text']:
                        tt_list.append({"id": p.id, "type": getLabel(p, 'type'), "text": p['text']})

                source_title_list = self.env['doc.paragraph'].sudo().search(
                    [('status', '=', '1'), ('lang', '=', getLabel(rec.source.lang, 'name')), ('type', '=', '1'),
                     ('doc_file', '=', rec.source.id)])
                st_list = []
                for p in source_title_list:
                    if p['text']:
                        st_list.append({"id": p.id, "type": getLabel(p, 'type'), "text": p['text']})

                # 都是docx都有有标题，分标题对齐
                if tt_list and st_list:
                    title_text_dict = {
                        getLabel(rec.source.lang, 'name'): st_list,
                        getLabel(rec.target.lang, 'name'): tt_list
                    }

                    title_align_res = agent_align(title_text_dict)

                    target_title_list.write({'status': '2'})
                    source_title_list.write({'status': '2'})

                    print(title_align_res)

                    # 再按照段落添加对齐任务至任务队列
                    for item in title_align_res:
                        msd_usr_id = rec.source.msd_usr_id
                        # 对其的标题入库
                        self.env['doc.translation.paragraphs'].sudo().create(
                            {'target': item[getLabel(rec.target.lang, 'name')]['id'],
                             'source': item[getLabel(rec.source.lang, 'name')]['id'],
                             'score':item['score']})

                        # 判断没有对齐过的再添加至向量数据库
                        if not self.if_align_done(item[getLabel(rec.source.lang, 'name')]['text'], item[getLabel(rec.target.lang, 'name')]['text']):
                            add_data({getLabel(rec.source.lang, 'name'): item[getLabel(rec.source.lang, 'name')]['text'],
                                      getLabel(rec.target.lang, 'name'): item[getLabel(rec.target.lang, 'name')]['text']},
                                     msd_usr_id if msd_usr_id else None)

                        # 将相同标题下段落生成对齐任务
                        source_doc_file_id = self.env['doc.paragraph'].sudo().search(
                            [('id', '=', item[getLabel(rec.source.lang, 'name')]['id'])]).doc_file.id
                        target_doc_file_id = self.env['doc.paragraph'].sudo().search(
                            [('id', '=', item[getLabel(rec.target.lang, 'name')]['id'])]).doc_file.id

                        # 只要类型为文本的段落
                        target_list = self.env['doc.paragraph'].sudo().search([('doc_file', '=', target_doc_file_id), (
                            'title', '=', item[getLabel(rec.target.lang, 'name')]['text']), ('type', '=', '2')])
                        source_list = self.env['doc.paragraph'].sudo().search([('doc_file', '=', source_doc_file_id), (
                            'title', '=', item[getLabel(rec.source.lang, 'name')]['text']), ('type', '=', '2')])

                        target_text_list = []
                        source_text_list = []

                        # 排除纯数字字母符号段落,不生成重复对齐内容
                        if target_list or source_list:
                            doc_quene_task = self.env['doc.quene.task'].sudo().create(
                                {'type': '对齐', 'status': '1', 'target_lang': rec.target.lang.id,
                                 'source_lang': rec.source.lang.id, 'source_file': rec.source.id,
                                 'target_file': rec.target.id, 'translation_file_id': rec.id})

                            rec.queue_task_id = [(4, 0, doc_quene_task.ids)]
                            target_ids = []
                            source_ids = []

                            for tp in target_list:
                                if  is_corpus(tp.text.strip(' ')) and tp.text.strip(' ') not in target_text_list:
                                    target_ids.append(tp.id)
                                    target_text_list.append(tp.text.strip(' '))

                            for sp in source_list:
                                if  is_corpus(sp.text.strip(' ')) and sp.text.strip(' ') not in source_text_list:
                                    source_ids.append(sp.id)
                                    source_text_list.append(sp.text.strip(' '))

                            # 排除纯数字段落
                            doc_quene_task.target_align_paragraphs = [(6, 0, target_ids)]
                            doc_quene_task.source_align_paragraphs = [(6, 0, source_ids)]

                            self.env.cr.commit()
                            print(item)

                # PDF转换暂不分标题全段落对齐
                else:
                    target_list = self.env['doc.paragraph'].sudo().search([('doc_file', '=', rec.target.id), ('type', '=', '2')])
                    source_list = self.env['doc.paragraph'].sudo().search([('doc_file', '=', rec.source.id), ('type', '=', '2')])
                    target_text_list = []
                    source_text_list = []
                    if target_list or source_list:
                        doc_quene_task = self.env['doc.quene.task'].sudo().create(
                            {'type': '对齐', 'status': '1', 'target_lang': rec.target.lang.id,
                             'source_lang': rec.source.lang.id, 'source_file': rec.source.id,
                             'target_file': rec.target.id, 'translation_file_id': rec.id})

                        rec.queue_task_id = [(4, 0, doc_quene_task.ids)]

                        # 排除纯数字字母符号段落,不生成重复对齐内容
                        target_ids = []
                        source_ids = []

                        for tp in target_list:
                            if is_corpus(tp.text.strip(' ')) and tp.text.strip(' ') not in target_text_list:
                                target_ids.append(tp.id)
                                target_text_list.append(tp.text.strip(' '))

                        for sp in source_list:
                            if is_corpus(sp.text.strip(' ')) and sp.text.strip(' ') not in source_text_list:
                                source_ids.append(sp.id)
                                source_text_list.append(sp.text.strip(' '))

                        doc_quene_task.target_align_paragraphs = [(6, 0, target_ids)]
                        doc_quene_task.source_align_paragraphs = [(6, 0, source_ids)]

                        self.env.cr.commit()


