# -*- coding: utf-8 -*-
{
    'name': 'СУВИТ. Дерево',
    'version': '0.1.2',
    'category': 'SUVIT',
    'complexity': 'easy',
    'description': """
СУВИТ. Дерево из разных моделей
=====================================

* Позволяет собрать деревянную структуру из разных моделей.
* Можно использовать TreeView для их отображения

""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'web',
    ],
    'data': [
        'views/assets.xml',
        'views/node.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}
