# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNode(TransactionCase):
    def test_config(self):
        Node = self.env['suvit.system.node']

        config = Node.get_tree_config()

        self.assertTrue('#' in config)
        self.assertTrue(Node._name in config)
