# -*- coding: utf-8 -*-
from odoo import api, models


# TODO maybe this no needed
class IrModelField(models.Model):
    _inherit = 'ir.model.fields'

    def _reflect_field_params(self, field):
        vals = super(IrModelField, self)._reflect_field_params(field)
        vals['track_visibility'] = getattr(field, 'track_visibility', 'onchange')
        return vals

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelField, self)._instanciate_attrs(field_data)
        if attrs and 'track_visibility' not in field_data:
            attrs['track_visibility'] = 'onchange'
        return attrs
