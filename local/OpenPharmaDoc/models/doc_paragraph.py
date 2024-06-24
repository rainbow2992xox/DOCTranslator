from odoo import models, fields, api
import math


class doc_paragraph(models.Model):
    _name = 'doc.paragraph'

    title = fields.Char(string='Paragraph title')
    text = fields.Text(string='Content')
    type = fields.Selection([('1', 'Title'),
                             ('2', 'Text'),
                             ('3', 'Table'),
                             ('4', 'Image')], string='Type', readonly=True, default='2')

    paragraph_text_idx = fields.Char(string='Paragraph text idx', readonly=True)

    lang = fields.Many2one('doc.lang', 'Language', readonly=True)
    doc_entitys = fields.One2many('doc.entity', 'doc_paragraph', string='Entity', readonly=True)
    doc_file = fields.Many2one('doc.file', 'From', readonly=True)
    source_quene_task_id = fields.Many2one('doc.quene.task', 'Task', readonly=True)
    target_quene_task_id = fields.Many2one('doc.quene.task', 'Task', readonly=True)

    status = fields.Selection([('1', '未校对'), ('2', '已校对')], string='Status', default='1')

    def unlink(self):
        # 删除与当前记录关联的所有doc_entitys记录
        self.mapped('doc_entitys').unlink()
        return super(doc_paragraph, self).unlink()
