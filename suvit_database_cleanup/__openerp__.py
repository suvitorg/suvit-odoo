# -*- coding: utf-8 -*-
{
    'name': 'Suvit Database cleanup',
    'version': '0.0.1',
    'category': 'SUVIT',
    'complexity': 'easy',
    'description': """
СУВИТ. Очистка БД
=====================================

* Добавляет Мастер очистки старых Полей.

""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'database_cleanup',
    ],
    'data': [
        'wizards/views/purge_fields.xml',
        'wizards/views/menu.xml',
        'wizards/data/cron.xml'
    ],
    'installable': True,
    'auto_install': False,
}
