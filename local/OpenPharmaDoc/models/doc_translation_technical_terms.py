from odoo import models, fields, api
import math
import zipfile
import io
import base64
import json
import os
# import sys
#
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)
# import translator.Translator_main as ts

class doc_translation_technical_terms(models.Model):
    _name = 'doc.translation.technical.terms'
    source = fields.Many2one('doc.entity.attribute', string='Source term', readonly=True)
    target = fields.Many2one('doc.entity.attribute', string='Target term', readonly=True)

    source_entity_type = fields.Char(related='source.doc_entity.doc_ontology.name', string='Entity', readonly=True, store=False)
    target_entity_type = fields.Char(related='target.doc_entity.doc_ontology.name', string='Entity', readonly=True, store=False)

    source_term = fields.Char(related='source.name', string='Source term')
    target_term = fields.Char(related='target.name', string='Target term')

    source_lang = fields.Many2one(related='source.lang', string='Source lang')
    target_lang = fields.Many2one(related='target.lang', string='Target lang')

    source_term_attribute_name = fields.Char(related='source.doc_ontology_attribute.name', string='Attribute', readonly=True, store=False)
    target_term_attribute_name = fields.Char(related='source.doc_ontology_attribute.name', string='Attribute', readonly=True, store=False)

    status = fields.Selection([('1', '未校对'), ('2', '已校对')], string='Status', default='1')

    def action_accept(self):
        for rec in self:
            rec.status = '2'