# -*- coding: utf-8 -*-
import logging

from odoo import api, models, _, fields

_logger = logging.getLogger(__name__)


def convert_for_display(value, col_info):
    if col_info['type'] in ['one2many', 'many2many'] and isinstance(value, models.BaseModel):
        return u"<ul><li>%s</li></ul>" % (u"</li><li>".join([n[1] for n in value.name_get()])
                                          if value else u"Пусто")
    return value


class MailTracking(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info):
        if col_info['type'] in ['one2many', 'many2many']:
            values = {'field': col_name,
                      'field_desc': col_info['string'],
                      'field_type': col_info['type'],
                      'old_value_text': str(initial_value) or '',
                      'new_value_text': str(new_value) or '',
                      }
            return values
        return super(MailTracking, self).create_tracking_values(initial_value, new_value, col_name, col_info)

    @api.multi
    def get_display_value(self, type):
        result = super(MailTracking, self).get_display_value(type)
        for i, record in enumerate(self):#.filtered(lambda r: r.field_type in ['one2many', 'many2many']):
            if record.field_type in ['one2many', 'many2many']:
                result[i] = record['%s_value_text' % type]
        return result


class PatchedMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def get_track_initial_values(self, tracked_fields, vals):
        initial_values = {}
        for rec in self:
            rec_vals = {}
            for key, field in tracked_fields.items():
                val = getattr(rec, key)
                if field['type'] in ['one2many', 'many2many']:
                    val = convert_for_display(getattr(rec, key), field)
                rec_vals[key] = val
            initial_values[rec.id] = rec_vals
        return initial_values

    @api.multi
    def write(self, vals):
        if self._context.get('tracking_disable'):
            return super(PatchedMailThread, self).write(vals)
        # Track initial values of tracked fields
        track_ctx = dict(self._context)
        if 'lang' not in track_ctx:
            track_ctx['lang'] = self.env.user.lang

        tracked_fields = None
        if not track_ctx.get('mail_notrack'):
            tracked_fields = self._get_tracked_fields(vals.keys())

        if tracked_fields:
            initial_values = self.get_track_initial_values(tracked_fields, vals)

        result = super(PatchedMailThread, self.with_context(tracking_disable=True)).write(vals)

        if tracked_fields:
            self.message_track(tracked_fields, initial_values)

        #self.message_auto_subscribe(vals.keys(), values=vals)

        return result

    @api.multi
    def _message_track(self, tracked_fields, initial):
        """ For a given record, fields to check (tuple column name, column info)
        and initial values, return a structure that is a tuple containing :

         - a set of updated column names
         - a list of changes (initial value, new value, column name, column info) """
        self.ensure_one()
        changes = set()  # contains always and onchange tracked fields that changed
        displays = set()  # contains always tracked field that did not change but displayed for information
        tracking_value_ids = []
        display_values_ids = []

        # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
        for col_name, col_info in tracked_fields.items():
            track_visibility = getattr(self._fields[col_name], 'track_visibility', 'onchange')
            initial_value = initial[col_name]
            new_value = getattr(self, col_name)
            # recovered method for this 1 row
            new_value = convert_for_display(new_value, col_info)

            if new_value != initial_value and (new_value or initial_value):  # because browse null != False
                tracking = self.env['mail.tracking.value'].create_tracking_values(initial_value, new_value, col_name, col_info)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])

                if col_name in tracked_fields:
                    changes.add(col_name)
            # 'always' tracked fields in separate variable; added if other changes
            elif new_value == initial_value and track_visibility == 'always' and col_name in tracked_fields:
                tracking = self.env['mail.tracking.value'].create_tracking_values(initial_value, initial_value, col_name, col_info)
                if tracking:
                    display_values_ids.append([0, 0, tracking])
                    displays.add(col_name)

        if changes and displays:
            tracking_value_ids = display_values_ids + tracking_value_ids
        return changes, tracking_value_ids


class PatchedMailMessage(models.Model):
    _inherit = 'mail.message'

    # XXX no need invalidate all cache in message_track functionality
    @api.model
    def refresh(self):
        pass


class PatchedMailFollowers(models.Model):
    _inherit = 'mail.followers'

    res_id = fields.Integer(ondelete='cascade')
