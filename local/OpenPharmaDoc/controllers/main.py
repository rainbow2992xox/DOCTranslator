from odoo import http
from odoo.http import request
import logging
import json
from ... import local_util
import os
import base64
import urllib.parse
from ..util.util import *
import pandas as pd

_logger = logging.getLogger(__name__)


class Main(http.Controller):
    # 对于auth = 'none'
    # 哪怕是已验证用户在访问路径时用户记录也是空的。使用这一个验证的场
    # 景是所响应的内容对用户不存在依赖，或者是在服务端模块中提供与数据库无关的功能。
    #
    # auth = 'public'的值将未验证用户设置为一个带有XML ID
    # base.public_user的特殊用户，已验证用户设置为用户自己的记录。
    # 对于所提供的功能同时针对未验证和已验证用户而已验证用户又具有一些
    # 额外的功能时应选择它，前面的代码中已经演示。
    #
    # 使用auth = 'user'
    # 来确保仅已验证用户才能访问所提供的内容。通过这个方法，我们可以确保
    # request.env.user指向已有用户。

    @http.route('/upload', type='http', auth="public")
    def upload(self, **kwargs):
        # folder_path = 'C:\\Users\\Rainbow\\Desktop\\Odoo\\DocTranslator\\data'
        folder_path = '/home'
        translation_files = import_corpus(folder_path)
        for t in translation_files:
            with open(t['en'], 'rb') as file:
                file_data = file.read()
                en_doc_file = request.env['doc.file'].sudo().create(
                    {'file': base64.b64encode(file_data), 'msd_usr_id': t['msd_usr_id'],
                     'name': os.path.basename(t['en']),'lang':1})

            with open(t['cn'], 'rb') as file:
                file_data = file.read()
                cn_doc_file = request.env['doc.file'].sudo().create(
                    {'file': base64.b64encode(file_data), 'msd_usr_id': t['msd_usr_id'],
                     'name': os.path.basename(t['cn']),'lang':2})

            tf = request.env['doc.translation.files'].sudo().create({'target': cn_doc_file.id, 'source': en_doc_file.id})
            en_doc_file.write({'doc_translation_files_id': tf.id})
            cn_doc_file.write({'doc_translation_files_id': tf.id})



    @http.route('/download/<int:record_id>', type='http', auth="public")
    def download_docx(self, record_id, **kwargs):
        record = request.env['doc.file'].sudo().browse(record_id)
        binary_data = base64.b64decode(record.file)
        encoded_file_name = urllib.parse.quote(record.name)
        if record:
            response = request.make_response(binary_data, [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                ('Content-Disposition', 'attachment; filename*=UTF-8\'\'{}'.format(encoded_file_name))
            ])
            return response
        else:
            return request.not_found()

    @http.route('/check_user', methods=['POST', 'OPTIONS'], type="json", auth='none', csrf=False, cors="*")
    def check_user(self, **kw):
        if request.env.user.name == "rainbow":
            return True
        else:
            return False

    @http.route('/get_graph_data', type="json", methods=['POST', 'OPTIONS'], auth='none', csrf=False, cors="*")
    def graph_data(self):
        c_list = [{'name': '文档'}]
        doc_ontology = request.env['doc.ontology'].sudo().search([])
        c_map = {
            "Doc": 0,
        }
        for o in doc_ontology:
            c_list.append({'name': o.name})
            c_map[o.name] = c_list.index({'name': o.name})

        n_list = []
        l_list = []
        doc_file = request.env['doc.file'].sudo().search([])
        for d in doc_file:
            doc_entity_attributes = d.doc_paragraphs.doc_entitys.doc_entity_attributes
            n_list.append(
                {'category': c_map['Doc'], 'id': 'd_' + str(d.id), 'value': 30, 'symbolSize': 30, 'name': d.name})
            if doc_entity_attributes.ids:
                for a in doc_entity_attributes:
                    n_list.append({'category': c_map[a.doc_entity.doc_ontology.name], 'id': 'a_' + str(a.id),
                                   'value': len(a.name), 'symbolSize': len(a.name), 'name': a.name})
                    l_list.append({'source': 'd_' + str(d.id), 'target': 'a_' + str(a.id)})

        return local_util.api_response("OK", data={'categories': c_list, 'nodes': n_list, 'links': l_list})
