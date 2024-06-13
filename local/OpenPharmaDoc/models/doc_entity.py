from odoo import models, fields, api
import math


class doc_entity(models.Model):
    _name = 'doc.entity'
    doc_paragraph = fields.Many2one('doc.paragraph', 'From', readonly=True)
    doc_paragraph_text = fields.Text(related='doc_paragraph.text', string='From')
    doc_ontology = fields.Many2one('doc.ontology', string='Ontology', readonly=True)
    doc_entity_attributes = fields.One2many('doc.entity.attribute','doc_entity',string='Entity attributes')
    lang = fields.Many2one('doc.lang', 'Language', readonly=True)
    status = fields.Selection([('1', '未校对'), ('2', '已校对')], string='Status', default='1')

    def unlink(self):
        # 删除与当前记录关联的所有doc_entitys记录
        self.mapped('doc_entity_attributes').unlink()
        return super(doc_entity, self).unlink()