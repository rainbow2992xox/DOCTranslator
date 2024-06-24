{
    'name': 'doc',
    'version': '1.0.0',
    'depends': ['base'],
    'data': [
        'data/doc_translation_files_muti_align_data.xml',
        'data/lang_data.xml',
        'views/doc_definition.xml',
        'views/doc_file.xml',
        'views/doc_ontology.xml',
        'views/doc_translation_corpus_entity.xml',
        'views/doc_translation_corpus_paragraph.xml',
        'views/quene_task.xml',
        'views/doc_translation_files.xml',
        'views/doc_translation_paragraphs.xml',
        'views/doc_translation_technical_terms.xml',
        'views/task.xml',
        'views/language.xml',
        'views/menu.xml',
        'security/doc_security.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            # 'OpenPharmaDoc/static/src/**/*'
        ],
        'web.assets_frontend': [
            # 'OpenPharmaDoc/static/src/**/*'
        ],
        'web.assets_qweb': [
        ],

    }
}
