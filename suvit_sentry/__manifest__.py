# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - Sentry connector
#
##############################################################################

{
    'name': 'Suvit. Odoo Sentry connector',
    'version': '0.1',
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'sequence': 4,
    'summary': 'Exceptions tracker',
    'description':
        """
Provide a pluggable base to connect Odoo with Sentry.
=======================================================

        """,
    'depends': ['web'],
    'installable': False,
    'auto_install': False,
    'application': True,
    "external_dependencies": {
        'python': ['raven',
                   'raven_sanitize_openerp',
                   ]
    },
    'qweb': [
        'static/src/xml/base.xml',
    ],
    'data': ['views/suvit_sentry.xml']
}
