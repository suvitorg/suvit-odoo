{
    'name': 'СУВИТ. Добавление классов к cell в o2m, m2m fields',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющие добавить class из view к ячейкам списка',
    'website': 'https://suvit.ru',
    'version': '1.0',
    'description': """
Добавление классов к cell в o2m, m2m fields (используется для oe_read_only, oe_edit_only)
""",
    'author': 'Suvit LLC',
    'depends': ['web',
                'web_tree_dynamic_colored_field'],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/web/assets.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
}
