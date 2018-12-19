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
        for rec in Followers.search([]):
            if not self.env[rec.res_model].browse(rec.res_id):
                _logger.debug("Delete mail followers record with id: %d related to res_model: %s, res_id: %d" % (
                    rec.id, rec.res_model, rec.res_id))
                rec.unlink()

        Messages = self.env['mail.message']
        cr = Messages._cr
        res_models_to_remove = list(set(Messages.search([('model', 'not in', self.env.keys())]).mapped('model')))
        if False in res_models_to_remove:
            res_models_to_remove[res_models_to_remove.index(False)] = u''
        if res_models_to_remove:
            query_delete_records(cr, res_models_to_remove, "model", "mail_message")
        Messages.search([('model', '=', False)]).unlink()
        for rec in Messages.search([]):
            if not self.env[rec.model].browse(rec.res_id):
                _logger.debug("Delete mail message record with id: %d related to model: %s, res_id: %d" % (
                    rec.id, rec.model, rec.res_id))
                rec.unlink()
