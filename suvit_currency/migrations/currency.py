# -*- coding: utf-8 -*-
from openerp import models, api, fields


class CurrencyMigration(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _0001_update_currency_rate(self):
        cur_rate_upd = self.env.registry.get('currency.rate.update.service')
        if not cur_rate_upd:
            return

        rub = self.search([('name', '=', 'RUB'), '|', ('active', '=', False), ('active', '=', True)], limit=1)
        comp = self.env['res.company'].search([('id', '=', 1)])
        rub.write({'active': True})
        if comp.currency_id != rub.id:
            comp.write({'currency_id': rub.id})

        if rub.rate != 1:
            self.env['res.currency.rate'].create(
                {'currency_id': rub.id,
                 'name': fields.Date.today(),
                 'rate': 1})

        comp.auto_currency_up = True

        service = self.env['currency.rate.update.service'].search([('service', '=', 'RU_CBRF')], limit=1)
        if not service:
            eur = self.search([('name', '=', 'EUR')], limit=1)
            usd = self.search([('name', '=', 'USD')], limit=1)
            self.env['currency.rate.update.service'].create(
                {'service': 'RU_CBRF',
                 'company_id': comp.id,
                 'currency_to_update': [(6, 0, [eur.id, usd.id])]})
