from odoo import models, fields, api
import math


class doc_ontology_attribute(models.Model):
    _name = 'doc.ontology.attribute'
    name = fields.Char(string='Attribute name')
    description = fields.Text(string='Description')
    doc_ontology = fields.Many2one('doc.ontology', string='Ontology', readonly=True)
