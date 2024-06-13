from odoo import models, fields, api
import math


class language(models.Model):
    _name = 'doc.lang'

    name = fields.Selection([('en', 'en'),
                             ('cn', 'cn')], string='Language', required=True)
