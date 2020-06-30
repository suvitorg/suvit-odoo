# -*- coding: utf-8 -*-

import datetime
import logging
import socket
import os

from odoo import _, api, models, fields, exceptions
from odoo.tools.translate import _

# from ..services.currency_getter import Currency_getter_factory
from ..services.update_service_RU_CBRF import RU_CBRF_getter

_logger = logging.getLogger(__name__)
CURRENCY_DOMAIN = [('name', 'in', ['RUB', 'USD', 'EUR'])]


class Currency(models.Model):
    _inherit = 'res.currency'

    # Перекрыто число знаков после запятой
    rate = fields.Float(digits=(12, 8))
    rub_currency_rate = fields.Float(string=u"Курс",
                                     compute='compute_rub_currency',
                                     digits=(12, 8),
                                     )

    rate_month = fields.Selection(string=u"Месяц",
                                  selection='get_rate_month_selection',
                                  compute='compute_rate_month_selection',
                                  )
    avg_rate = fields.Float(string=u"Средний курс за месяц",
                            compute='compute_avg_rate',
                            digits=(12, 4),
                            )

    from_date = fields.Date(string=u'От даты',
                            default=datetime.date(datetime.date.today().year, 1, 1))

    force_refresh = fields.Boolean(string=u'Принудительно')

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
        current_service = 'RU_CBRF'

        if self.name == 'RUB':
            raise exceptions.Warning(
                'Данная валюта не поддерживается: RUB')

        # factory = Currency_getter_factory()
        # getter = factory.register(current_service)
        getter = RU_CBRF_getter()

        today = datetime.date.today()
        date = fields.Date.from_string(self.from_date)
        if self.force_refresh:
            rec_dates = set()
        else:
            rec_dates = set(self.env['res.currency.rate'].search(
                [('currency_id', '=', self.id),
                 ('name', '>=', fields.Datetime.to_string(date))]).mapped('name'))

        all_dates = set()
        while date <= today:
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
                rec = self.env['res.currency.rate'].search([('currency_id', '=', self.id),
                                                            ('name', '=', d)], limit=1)
                if rec:
                    rec.write({'rate': res[self.name]})
                else:
                    self.env['res.currency.rate'].create(vals)
            except Exception as exc:
                _logger.info(repr(exc))
                rec = self.env['currency.rate.update.service'].search(
                    [('service', '=', current_service)],
                    limit=1)
                if rec:
                    error_msg = '\n%s ERROR : %s %s' % (
                        fields.Datetime.to_string(datetime.datetime.today()),
                        repr(exc), '')
                    #rec.write({'note': error_msg})

    @api.model
    def check_rates(self):
        default_param = 3
        try:
            currency_days_with_not_rates = int(self.env['ir.config_parameter'].get_param('currency_days_with_not_rates', default_param))
        except ValueError:
            currency_days_with_not_rates = default_param
        today = datetime.date.today()
        date = today - datetime.timedelta(currency_days_with_not_rates)
        admin = self.env['res.users'].browse(1)
        Mail = self.env['mail.mail']

        domain = CURRENCY_DOMAIN + [('name', '!=', 'RUB')]
        for cur in self.search(domain):
            _logger.info('Begin update for currency {}'.format(cur.name))
            recs = self.env['res.currency.rate'].search(
                [('currency_id', '=', cur.id),
                 ('name', '>=', fields.Datetime.to_string(date))])
            if recs:
                continue
            cron_currency_update_id = self.env.ref('currency_rate_update.ir_cron_currency_update_every_day')
            last_run_date = fields.Datetime.from_string(cron_currency_update_id.nextcall) - datetime.timedelta(days=1)
            hostname = socket.gethostname()
            work_dir = os.path.abspath(__file__)

            message = u'<div>Валюта {} не обновлялась c {}.</div>'\
                      u'<div>Последний запуск обновления: {}</div>'\
                      u'<div>Следующий запуск обновления: {}</div>'\
                      u'<div>Хост: {}</div>'\
                      u'<div>Директория: {}</div>'.format(cur.name, date.strftime('%d-%m-%Y'),
                                                          last_run_date.strftime('%d-%m-%Y'),
                                                          cron_currency_update_id.nextcall,
                                                          hostname, work_dir)

            mess = Mail.create({
                'email_to': admin.email,
                'subject': u'Нет обновления валюты {}!'.format(cur.name),
                'body_html': message})
            mess.send()
            _logger.info('Letter sent about currency {} update.'.format(cur.name))

class Rate(models.Model):
    _inherit = "res.currency.rate"

    rub_currency_rate = fields.Float(string=u"Курс",
                                     compute='compute_rub_currency',
                                     inverse='inverse_rub_currency',
                                     digits=(12, 8),
                                     )

    # Перекрыто число после запятой
    rate = fields.Float(digits=(12, 8))

    @api.multi
    def compute_rub_currency(self):
        for rec in self:
            if rec.rate:
                rec.rub_currency_rate = 1. / rec.rate

    @api.multi
    def inverse_rub_currency(self):
        for rec in self:
            if rec.rub_currency_rate:
                rec.rate = 1. / rec.rub_currency_rate
