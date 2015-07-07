# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - Sentry connector
#
##############################################################################

{
    'name': 'Odoo Sentry connector',
    'version': '0.1',
    'author': 'Suvit, LLC',
    'sequence': 4,
    'summary': 'Exceptions tracker',
    'description':
        """
Provide a pluggable base to connect Odoo with Sentry.
====================================================

        """,
    'depends': ['base'],
    'auto_install': False,
    'application': True,
}
