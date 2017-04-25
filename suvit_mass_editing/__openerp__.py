# -*- coding: utf-8 -*-
{
    'name': 'СУВИТ. Mass Editing',
    'version': '0.0.1',
    'category': 'SUVIT',
    'complexity': 'easy',
    'description': """
СУВИТ. Mass Editing
=====================================

* Позволяет установить порядок полей в Mass Edit Wizard.

""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'mass_editing',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/mass_editing_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
