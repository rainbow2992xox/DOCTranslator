from odoo import models, fields, api
import math


class doc_entity_attribute(models.Model):
    _name = 'doc.entity.attribute'
    name = fields.Char(string='Value')
    doc_entity = fields.Many2one('doc.entity', string='Entity', readonly=True)
    doc_ontology_attribute = fields.Many2one('doc.ontology.attribute', string='Type', readonly=True)
    lang = fields.Many2one('doc.lang', 'Language', readonly=True)
    status = fields.Selection([('1', '未校对'), ('2', '已校对')], string='Status', default='1')


    def action_accept(self):
        for rec in self:
            rec.status = '2'
