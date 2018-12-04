# -*- coding: utf-8 -*-
{
    'name': 'СУВИТ. Система',
    'version': '0.0.1',
    'category': 'SUVIT',
    'complexity': 'easy',
    'description': """
СУВИТ. Cистемное Дерево
=====================================

* Позволяет собрать деревянную структуру системы из разных моделей.

""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'suvit_base',
        'suvit_multi_model_tree',
    ],
    'data': [
        # 'views/assets.xml',
        # 'views/node.xml',
    ],
    'qweb' : [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}
