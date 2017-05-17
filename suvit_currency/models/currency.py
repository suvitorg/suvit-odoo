# -*- coding: utf-8 -*-
from openerp import api, models, fields

import datetime

CURRENCY_DOMAIN = [('name', 'in', ['RUB', 'USD', 'EUR'])]


class Currency(models.Model):
    _inherit = 'res.currency'

    rub_currency_rate = fields.Float(string=u"Курс",
                                     compute='compute_rub_currency',
                                     digits=(12, 4),
                                     )

    rate_month = fields.Selection(string=u"Месяц",
                                  selection='get_rate_month_selection',
                                  compute='compute_rate_month_selection',
                                  )
    avg_rate = fields.Float(string=u"Средний курс за месяц",
                            compute='compute_avg_rate',
                            digits=(12, 4),
                            )

    @property
    def rub_id(self):
        return self.env.ref('base.RUB')

    @property
    def eur_id(self):
        return self.env.ref('base.EUR')

    @api.v8
    def compute_rub(self, from_amount, round=True):
        return self.compute(from_amount, self.rub_id, round)

    @api.v8
    def compute_eur(self, from_amount, round=True):
        return self.compute(from_amount, self.eur_id, round)

    @api.multi
    def compute_rub_currency(self):
        for rec in self:
            if rec.rate:
                rec.rub_currency_rate = 1. / rec.rate

    @api.model
    def get_rate_month_selection(self):
        """rate_start = fields.Date.from_string(self.env['res.currency.rate'].search([('currency_id.name', 'in', ['USD', 'EUR', 'RUB'])],
                                                                                  order='name', limit=1).name)"""
        end = datetime.date.today()
        rate_start = datetime.date(end.year - 1, end.month, 1)
        sel_month = datetime.date(rate_start.year, rate_start.month, 1)
        months_sel = []

        while sel_month <= end:
            if sel_month.month == 12:
                next_month = datetime.date(sel_month.year + 1, 1, 1)
            else:
                next_month = datetime.date(sel_month.year, sel_month.month + 1, 1)
            sel_val = '%s,%s' % (fields.Date.to_string(sel_month),
                                 fields.Date.to_string(next_month))
            months_sel.append((sel_val, sel_month.strftime('%Y.%m')))
            sel_month = next_month

        return months_sel

    @api.multi
    def compute_rate_month_selection(self):
        rate_month = self.get_rate_month_selection()[-1][0]
        for rec in self:
            rec.rate_month = rate_month

    @api.one
    @api.onchange('rate_month')
    def compute_avg_rate(self):
        if self.name == 'RUB':
            self.avg_rate = 1
        elif self.rate_month:
            start, end = self.rate_month.split(',')
            month_rates = self.env['res.currency.rate'].search(
                [('currency_id.name', '=', self.name),
                 ('name', '>=', start),
                 ('name', '<', end)])
            if month_rates:
                rates = [rate.rate for rate in month_rates]
                avg_rate = sum(rates) / float(len(rates))
                self.avg_rate = 1. / avg_rate
            else:
                self.avg_rate = 0


class Rate(models.Model):
    _inherit = "res.currency.rate"

    rub_currency_rate = fields.Float(string=u"Курс",
                                     compute='compute_rub_currency',
                                     digits=(12, 4),
                                     )

    @api.multi
    def compute_rub_currency(self):
        for rec in self:
            if rec.rate:
                rec.rub_currency_rate = 1. / rec.rate
