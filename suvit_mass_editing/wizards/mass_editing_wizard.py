# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.osv import orm
from lxml import etree


class MassEditingWizard(models.TransientModel):
    _inherit = 'mass.editing.wizard'

    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):

        result = super(MassEditingWizard, self).fields_view_get(view_id, view_type, toolbar, submenu)

        if self.env.context.get('mass_editing_object'):
            for f_name in result['fields']:
                if f_name.startswith('selection__'):
                    f_type = result['fields'][f_name.replace('selection__', '')]['type']
                    if f_type == 'many2many':
                        selection = [('set', u'Установить'),
                                     ('remove_m2m', u'Удалить'),
                                     ('add', u'Добавить')]
                    else:
                        selection = [('set', u'Установить'),
                                     ('remove', u'Удалить')]
                    result['fields'][f_name]['selection'] = selection

            arch = etree.XML(result['arch'])
            attrs_fields = arch.xpath("//field[@attrs]")
            for field in attrs_fields:
                orm.setup_modifiers(field)
            result['arch'] = etree.tostring(arch, encoding='utf8')

        return result
