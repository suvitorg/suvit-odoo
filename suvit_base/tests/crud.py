# -*- coding: utf-8 -*-
from lxml import etree


from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval as eval


class CRUDCase(TransactionCase):

    def crud(self, model, create_vals={}, write_vals={}, check_vals={}, view_id=None):
        arch = model.fields_view_get(view_id=view_id, view_type='form', toolbar=True)
        data = model.default_get(arch['fields'].keys())
        self.assertTrue(arch['toolbar'])

        obj = model.create(create_vals)

        self.assertTrue(obj.exists())

        obj = model.browse(obj.id)
        self.assertTrue(obj)

        data = obj.read(arch['fields'].keys())

        arch = model.fields_view_get(view_type='tree')
        data = obj.read(arch['fields'].keys())

        obj.write(write_vals)
        for k, v in write_vals.items():
            if type(obj[k]) != type(v) and isinstance(v, int):
                self.assertEqual(obj[k].id, v)
            else:
                self.assertEqual(obj[k], v)

        for k, v in check_vals.items():
            self.assertEqual(obj[k], v)

        arch = model.fields_view_get(view_type='tree', toolbar=True)
        self.assertTrue(arch['toolbar'])

        arch = model.fields_view_get(view_type='search')
        self.assertTrue(arch)
        nodes = etree.XML(arch['arch']).xpath("/search/group/filter")
        if not nodes:
            nodes = etree.XML(arch['arch']).xpath("/search/filter")
        groups = []
        fields = []
        for node in nodes:
            node = eval(node.get('context'))
            if 'group_by' not in node:
                continue
            node = node.get('group_by').decode('utf-8', 'ignore')
            groups.append(node)
            fields.append(node.split(":")[0])
        fields = list(set(fields))
        if groups:
            field_names = self.env['ir.model.fields'].search([
                ('model', '=', model._name), ('name', 'in', fields)]).mapped('name')
            self.assertEqual(len(fields), len(field_names))
            res = model.read_group(domain=[], fields=fields, groupby=groups, lazy=True)
            self.assertTrue(res)

        obj.unlink()
        self.assertFalse(obj.exists())
