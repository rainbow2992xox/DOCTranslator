from odoo import models, fields, api
import math


class doc_ontology(models.Model):
    _name = 'doc.ontology'
    name = fields.Char(string='Ontology Name')
    description = fields.Text(string='Description')
    doc_definition = fields.Many2one('doc.definition', string='PharmaDoc Type')
    doc_ontology_attributes = fields.One2many('doc.ontology.attribute', 'doc_ontology', string='Attributes')
