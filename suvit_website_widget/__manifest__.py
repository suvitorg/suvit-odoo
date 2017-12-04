# -*- coding: utf-8 -*-
{
    'name': "Сувит. Справочник виджетов",
    'category': 'UI',
    'summary': 'Веб-сайт со справочником виджетов',
    'website': 'https://suvit.ru',
    'author': 'Suvit LLC',
    'version': '1.0',
    'description': """
        Модель Виджета для Odoo
        ===========================
        Дерево виджетов

    """,
    # any module necessary for this one to work correctly
    'depends': ['base',
                'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
