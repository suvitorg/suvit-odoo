# -*- coding: utf-8 -*-
{
    'name': "Runbot for bitbucket suvit",
    'version': '0.0.1',
    'description': """
        Расширение runbot для работы с bitbucket
    """,
    'author': "Suvit LLC",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',

    # any module necessary for this one to work correctly
    'depends': ['runbot'],

    # always loaded
    'data': [
        'views/repo.xml',
    ],
    'installable': False,
}
