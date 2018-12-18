# -*- coding: utf-8 -*-
import logging

from odoo import models, api, exceptions

_logger = logging.getLogger(__name__)


class CurrencyMigration(models.Model):
    _inherit = 'suvit.migration'

    @api.model
    def remove_unrelated_mail_records(self):

        def query_delete_records(cr, models_to_remove, field, model):
            query = """ DELETE FROM %s
                        WHERE %s in (%s)
                    """ % (model, field, (u"'" + u"', '".join(models_to_remove) + u"'"))
            cr.execute(query, tuple(res_models_to_remove))
            cr.commit()

        Followers = self.env['mail.followers']
        cr = Followers._cr
        res_models_to_remove = list(set(Followers.search([('res_model', 'not in', self.env.keys())]).mapped('res_model')))
        if res_models_to_remove:
            query_delete_records(cr, res_models_to_remove, "res_model", "mail_followers")
        Followers.search([('res_id', '=', False)]).unlink()

        Messages = self.env['mail.message']
        cr = Messages._cr
        res_models_to_remove = list(set(Messages.search([('model', 'not in', self.env.keys())]).mapped('model')))
        res_models_to_remove.remove(False)  # Выяснилось, что в сообщениях есть записи с пустым model.
        if res_models_to_remove:
            query_delete_records(cr, res_models_to_remove, "model", "mail_message")
        Messages.search([('res_id', '=', False)]).unlink()
