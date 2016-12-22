# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNode(TransactionCase):
    def test_node_crud(self):
        Node = self.env['suvit.system.node']

        root = Node.create({'name': 'Root1'})

        ch1 = Node.create({'name': 'Ch1', 'parent_id': root.id})
        ch2 = Node.create({'name': 'Ch3', 'parent_id': root.id})
        ch3 = Node.create({'name': 'Ch2', 'parent_id': root.id})

        ch2.write({'name': 'Ch3-last', 'sequence': 1000})

        self.assertEqual(len(root.child_ids), 3)
        # test change name and order of children
        self.assertEqual(root.child_ids.mapped('name'),
                         ['Ch1', 'Ch2', 'Ch3-last'])

        ch3.unlink()

        # create duplicate to ch2
        ch2.action_duplicate()

        # add children for ch2
        ch2_1 = Node.create({'name': 'Ch2-1', 'parent_id': ch2.id})
        ch2_2 = Node.create({'name': 'Ch2-2', 'parent_id': ch2.id})

        # add children for ch2_1
        ch2_1_1 = Node.create({'name': 'Ch2-1-1', 'parent_id': ch2_1.id})
        ch2_1_2 = Node.create({'name': 'Ch2-2-2', 'parent_id': ch2_1.id})

        ch2.invalidate_cache()
        self.assertEqual(len(ch2.all_child_ids), 4)
        self.assertEqual(ch2_1_1.all_parent_ids, [ch2, ch2_1])

    def test_copy_duplicate():
        Node = self.env['suvit.system.node']

        root = Node.create({'name': 'Root1'})

        root.action_duplicate()

        duplicate = Node.search([('name', 'like', Node._duplicate_prefix)])
        self.assertEqual(len(duplicate), 1)
        self.assertEqual(duplicate.name, 'D_Root1')
        self.assertEqual(duplicate.shortcut_id, root)
        self.assertEqual(duplicate.self_id, root)
        self.assertEqual(root.self_id, root)

        # test copy of duplicate is a copy of original
        duplicate.action_copy()

        # root has one duplicate
        self.assertEqual(root.duplicate_ids.ids, [duplicate.id])
        self.assertEqual(Node.search([], count=True), 3)

        copy = Node.search([('name', 'like', Node._copy_suffix)])
        self.assertEqual(len(copy), 1)
        self.assertEqual(duplicate.name, u'D_Root1 Копия')
        self.assertEqual(copy.shortcut_id, False)
        self.assertEqual(copy.self_id, copy)
