# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNode(TransactionCase):
    def test_node_crud(self):
        Node = self.env['suvit.system.node']

        root = Node.create({'name': u'Root1'})

        ch1 = Node.create({'name': u'Ch1', 'parent_id': root.id})
        ch2 = Node.create({'name': u'Ch3', 'parent_id': root.id})
        ch3 = Node.create({'name': u'Ch2', 'parent_id': root.id})

        ch2.write({'name': u'Ch3-last', 'sequence': 1000})

        self.assertEqual(len(root.child_ids), 3)
        self.assertEqual(root.child_ids.mapped('name'), [u'Ch1', u'Ch2', u'Ch3-last'])

        ch3.unlink()

        # create duplicate to ch2
        ch2.action_duplicate()

        # add children for ch2
        ch2_1 = Node.create({'name': u'Ch2-1', 'parent_id': ch2.id})
        ch2_2 = Node.create({'name': u'Ch2-2', 'parent_id': ch2.id})

