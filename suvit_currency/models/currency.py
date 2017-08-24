# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp import exceptions

from ..services.currency_getter import Currency_getter_factory

import datetime
import logging

_logger = logging.getLogger(__name__)
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

    @property
    def usd_id(self):
        return self.env.ref('base.USD')

    @api.v8
    def compute_rub(self, from_amount, round=True):
        return self.compute(from_amount, self.rub_id, round)

    @api.v8
    def compute_eur(self, from_amount, round=True):
        return self.compute(from_amount, self.eur_id, round)

    @api.v8
    def compute_usd(self, from_amount, round=True):
        return self.compute(from_amount, self.usd_id, round)

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

    @api.one
    def refrech_empty_date_rates(self):
        # from ..services import update_service_RU_CBRF
        current_service = 'RU_CBRF_getter'

        if self.name == 'RUB':
            raise exceptions.Warning(
                'Данная валюта не поддерживается: {}'.format(currency))

        factory = Currency_getter_factory()
        getter = factory.register(current_service)

        date = datetime.date(today.year, 1, 1)
        rec_dates = set(self.env['res.currency.rate'].search(
            [('currency_id', '=', self.id),
             ('name', '>=', fields.Datetime.to_string(date))]).mapped('name'))

        all_dates = set()
        today = datetime.date.today()
        while date < today:
            all_dates.add(fields.Datetime.to_string(date))
            date += datetime.timedelta(1)

        dates = all_dates - rec_dates
        for d in sorted(dates):
            try:
                date_req = datetime.datetime.strptime(
                    d[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                res, log_info = getter.get_updated_currency(
                    [self.name],
                    None,
                    None,
                    date_req=date_req)
                vals = {
                    'currency_id': self.id,
                    'rate': res[self.name],
                    'name': d
                }
                self.env['res.currency.rate'].create(vals)
            except Exception as exc:
                _logger.info(repr(exc))
                rec = self.env['currency.rate.update.service'].search(
                    [('service', '=', current_service)],
                    limit=1)
                if rec:
                    error_msg = '\n%s ERROR : %s %s' % (
                        fields.Datetime.to_string(datetime.datetime.today()),
                        repr(exc), rec.note or '')
                    rec.write({'note': error_msg})

    @api.model
    def check_rates(self):
        default_param = 3
        try:
            currency_days_with_not_rates = int(self.env['ir.config_parameter'].get_param('currency_days_with_not_rates', default_param))
        except ValueError:
            currency_days_with_not_rates = default_param
        today = datetime.date.today()
        date = today - datetime.timedelta(currency_days_with_not_rates)
        recs = self.env['res.currency.rate'].search(
            [('name', '>=', fields.Datetime.to_string(date))])
        if not recs:
            admin = self.env['res.users'].browse(1)
            mail = self.env['mail.mail']
            message = 'Валюты не обновлялись c {}'.format(date.strftime('%d-%m-%Y'))
            mess = mail.create({
                'email_to': admin.email,
                'subject': 'Валюта',
                'body_html': message})
            mess.send()


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
