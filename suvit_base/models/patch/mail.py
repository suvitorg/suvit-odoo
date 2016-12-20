# -*- coding: utf-8 -*-
import logging

from openerp import api, models

_logger = logging.getLogger(__name__)


class PatchedMailThread(models.Model):
    _inherit = 'mail.thread'

    # TODO monkey patch odoo.mail.mail_thread to use unicode keys in selections
    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value.name_get()[0][1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection']).get(value, u'Неизвестно')
            return value

        def format_message(message_description, tracked_values):
            message = u''
            if message_description:
                message = u'<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += u'<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += u'%s &rarr; ' % change.get('old_value')
                message += u'%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        for browse_record in self.browse(cr, uid, ids, context=context):
            initial = initial_values[browse_record.id]
            changes = set()
            tracked_values = {}

            # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                field = self._fields[col_name]
                initial_value = initial[col_name]
                record_value = getattr(browse_record, col_name)

                try:
                    col_title = col_info['string'].decode('utf8')
                except UnicodeError:
                    col_title = col_info['string']

                if record_value == initial_value and getattr(field, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(
                        col_info=col_title,
                        new_value=convert_for_display(record_value, col_info),
                    )
                elif record_value != initial_value and (record_value or initial_value):  # because browse null != False
                    if getattr(field, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(
                            col_info=col_title,
                            old_value=convert_for_display(initial_value, col_info),
                            new_value=convert_for_display(record_value, col_info),
                        )
                    if col_name in tracked_fields:
                        changes.add(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            # By passing this key, that allows to let the subtype empty and so don't sent email because partners_to_notify from mail_message._notify will be empty
            if not context.get('mail_track_log_only'):
                for field, track_info in self._track.items():
                    if field not in changes:
                        continue
                    for subtype, method in track_info.items():
                        if method(self, cr, uid, browse_record, context):
                            subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                subtype_rec = self.pool.get('ir.model.data').xmlid_to_object(cr, uid, subtype, context=context)
                if not (subtype_rec and subtype_rec.exists()):
                    _logger.debug('subtype %s not found' % subtype)
                    continue
                message = format_message(subtype_rec.description if subtype_rec.description else subtype_rec.name, tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, subtype=subtype, context=context)
                posted = True
            if not posted:
                message = format_message('', tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, context=context)
        return True


class PatchedMailMessage(models.Model):
    _inherit = 'mail.message'

    # XXX no need invalidate all cache in message_track functionality
    @api.model
    def refresh(self):
        pass
