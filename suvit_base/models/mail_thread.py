# -*- coding: utf-8 -*-
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _get_tracked_fields2(self, updated_fields):
        tracked_fields = super()._get_tracked_fields(updated_fields)
        tracked_fields_list = []
        for name, field in self._fields.items():
            default_track = 'onchange' if field.type not in ['one2many', 'many2many'] else False
            if getattr(field, 'track_visibility', default_track) and name not in tracked_fields:
                tracked_fields_list.append(name)

        if tracked_fields_list:
            tracked_fields.update(self.fields_get(tracked_fields_list))

        return tracked_fields

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
