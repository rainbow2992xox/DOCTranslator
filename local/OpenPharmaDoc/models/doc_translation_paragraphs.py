from odoo import models, fields, api
import math
from ..util.util import *
from ..util.agent_util import *
from ..util.doc_util import *
import os

# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)
# import translator.Translator_main as ts

# from ..util.translator.Translator_main import *
import zipfile
import io
import base64
import json


class doc_translation_paragraphs(models.Model):
    _name = 'doc.translation.paragraphs'
    target = fields.Many2one('doc.paragraph', string='Target paragraph', readonly=True)
    source = fields.Many2one('doc.paragraph', string='Source paragraph', readonly=True)
    target_paragraph = fields.Text(related='target.text', string='Target content')
    source_paragraph = fields.Text(related='source.text', string='Source content')

    @api.model
    def web_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        return super(doc_translation_paragraphs, self).web_search_read(domain, fields, offset, limit, order)

    def action_extract(self):
        doc_definition = self.source.doc_file.doc_definition
        doc_ontologys = doc_definition.doc_ontologys
        for o in doc_ontologys:
            print(o.name)
            doc_ontology_attributes = o.doc_ontology_attributes
            s_text =  self.source_paragraph
            t_text =  self.target_paragraph
            input_dict = {
                getLabel(self.source.lang, 'name'): s_text,
                getLabel(self.target.lang, 'name'): t_text,
                "a_list": [{"a_id": a.id, "name": a.name} for a in doc_ontology_attributes]
            }
            print(input_dict)
            source_entity_dict = {
                "doc_paragraph": self.source.id,
                "doc_ontology": doc_definition.id,
                "lang": self.source.lang.id,
                "status": '1'
            }

            target_entity_dict = {
                "doc_paragraph": self.target.id,
                "doc_ontology": doc_definition.id,
                "lang": self.target.lang.id,
                "status": '1'
            }
            # TODO: agent_extract
            # doc_entity = ts.agent_extract(ts.init(), input_dict)
            doc_entity = agent_extract(input_dict)
            print(doc_entity)
            if doc_entity:
                for d in doc_entity:
                    print(d)
                    source_entity = self.env['doc.entity'].sudo().create(source_entity_dict)
                    target_entity = self.env['doc.entity'].sudo().create(target_entity_dict)

                    source_doc_entity_attributes = []
                    target_doc_entity_attributes = []
                    doc_translation_technical_terms = []
                    for a in d:
                        print(a)
                        source_a_attribute = a[getLabel(self.source.lang, 'name')]
                        target_a_attribute = a[getLabel(self.target.lang, 'name')]
                        if source_a_attribute['value'] in s_text and target_a_attribute['value'] in t_text:
                            source_a_attribute_dict = {
                                "name": source_a_attribute['value'],
                                "doc_entity": source_entity.id,
                                "doc_ontology_attribute": source_a_attribute['a_id'],
                                "lang": self.source.lang.id,
                                "status": '1',
                            }
                            target_a_attribute_dict = {
                                "name": target_a_attribute['value'],
                                "doc_entity": target_entity.id,
                                "doc_ontology_attribute": target_a_attribute['a_id'],
                                "lang": self.target.lang.id,
                                "status": '1',
                            }

                            source_a_attribute = self.env['doc.entity.attribute'].sudo().create(source_a_attribute_dict)
                            target_a_attribute = self.env['doc.entity.attribute'].sudo().create(target_a_attribute_dict)

                            source_doc_entity_attributes.append(source_a_attribute)
                            target_doc_entity_attributes.append(target_a_attribute)

                            doc_translation_technical_terms.append({
                                "source": source_a_attribute.id,
                                "target": target_a_attribute.id,
                                "status": '1'
                            })
                        else:
                            print('--------Attribute not in text-------')

                    doc_translation_technical_terms = self.env['doc.translation.technical.terms'].sudo().create(doc_translation_technical_terms)
                    source_entity.doc_entity_attributes = [(6, 0, [a.id for a in source_doc_entity_attributes])]
                    target_entity.doc_entity_attributes = [(6, 0, [a.id for a in target_doc_entity_attributes])]
