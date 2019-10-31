# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestNode(TransactionCase):
    def test_migration(self):
        Migration = self.env['suvit.migration']

        migration = Migration.create({'name': 'Тест',
                                      'method': 'read'})

        migration.run()

        self.assertTrue(migration.implemented)
