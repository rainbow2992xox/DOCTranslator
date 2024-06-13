from odoo import models, fields, api
import math


class doc_definition(models.Model):
    _name = 'doc.definition'
    name = fields.Char(string='PharmaDoc')
    doc_ontologys = fields.One2many('doc.ontology', 'doc_definition', string='Ontologys')




