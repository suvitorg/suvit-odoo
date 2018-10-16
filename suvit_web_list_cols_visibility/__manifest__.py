{
    'name': 'СУВИТ. Добавление классов к cell в o2m, m2m fields',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющие добавить class из view к ячейкам списка',
    'version': '1.0',
    'description': """
Добавление классов к cell в o2m, m2m fields (используется для oe_read_only, oe_edit_only)
""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'web',
    ],
    'installable': True,
    'auto_install': False,
    'data': [
    ],
    'qweb': [
        "static/src/xml/widget.xml",
    ],
}
