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

        def delete_unexisted_records(recordset, model_field, id_field, message):
            _logger.debug(message)
            res_models = list(set(recordset.search([]).mapped(model_field)))
            for model in res_models:
                _logger.debug(u"Search unexisted records in model: %s" % model)
                ids_to_delete = recordset.search(
                    [(model_field, '=', model), (id_field, 'not in', self.env[model].search([]).ids)])
                _logger.debug(u"Deleting next ids: %s" % u", ".join(str(ident) for id in ids_to_delete.ids))
                ids_to_delete.unlink()

        Followers = self.env['mail.followers']
        cr = Followers._cr
        res_models_to_remove = list(set(Followers.search([('res_model', 'not in', self.env.keys())]).mapped('res_model')))
        if res_models_to_remove:
            query_delete_records(cr, res_models_to_remove, "res_model", "mail_followers")
        delete_unexisted_records(Followers, 'res_model', 'res_id', u'Start checking mail.followers')

        Messages = self.env['mail.message']
        cr = Messages._cr
        res_models_to_remove = list(set(Messages.search([('model', 'not in', self.env.keys())]).mapped('model')))
        if False in res_models_to_remove:
            res_models_to_remove[res_models_to_remove.index(False)] = u''
        if res_models_to_remove:
            query_delete_records(cr, res_models_to_remove, "model", "mail_message")
        Messages.search([('model', '=', False)]).unlink()
        delete_unexisted_records(Messages, 'model', 'res_id', u'Start checking mail.message')
