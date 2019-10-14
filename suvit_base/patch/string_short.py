# -*- coding: utf-8 -*-
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


def get_description_selectable(self, env):
    return getattr(self, 'selectable', None)

from operator import attrgetter
for field_type in fields.MetaField.by_type.values():
    field_type._description_string_short = property(lambda s: getattr(s, 'string_short', None))
    field_type.description_attrs.append(('string_short', '_description_string_short'))

    field_type._description_width_chars = property(lambda s: getattr(s, 'width_chars', None))
    field_type.description_attrs.append(('width_chars', '_description_width_chars'))

    field_type._description_selectable = lambda s, env: get_description_selectable(s, env)
    field_type.description_attrs.append(('selectable', '_description_selectable'))


class ViewStringShort(models.Model):
    _inherit = 'ir.ui.view'

    def postprocess_and_fields1(self, model, node, view_id):
        arch, fields = super(ViewStringShort, self).postprocess_and_fields(model, node, view_id)
        if node.tag == 'tree':
            for vals in fields.values():
                if 'string_short' in vals:
                    vals['title'] = vals['string']
                    vals['string'] = vals['string_short']

        return arch, fields
