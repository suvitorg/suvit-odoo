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
* Дабавляет удаление старых записей по крону

""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'database_cleanup',  # oca/server-tools
    ],
    'data': [
        'wizards/views/purge_fields.xml',
        'wizards/views/menu.xml',

        'data/cron.xml'
    ],
    'installable': True,
    'auto_install': False,
}
