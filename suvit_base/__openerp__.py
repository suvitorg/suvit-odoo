# -*- coding: utf-8 -*-
{
    'name': 'СУВИТ. Ядро',
    'version': '0.0.1',
    'category': 'SUVIT',
    'complexity': 'easy',
    'description': """
СУВИТ. Ядро
============

Базовые вещи нужные во всех проектах:

   * Убирает плашки регистрации
   * Возможности модуля support_branding
   * Возможности модуля web_debranding

TODO
""",
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': ['web',  # odoo/core
                'disable_openerp_online',  # github/oca/server_tools
                # 1. support_branding - С предустановленными полями
                # 2. web_debranding -C предустановленными полями
                # 3. support_debranding
                # 4. hide_db_manager_link oca/server_tools
                'suvit_sentry',
                ],
    'data': [
    ],
    'js': [
    ],
    'installable': True,
    'auto_install': False,
}
