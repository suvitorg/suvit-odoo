# -*- coding: utf-8 -*-
from openerp import models, fields


class Currency_rate_update_service(models.Model):
    _inherit = 'currency.rate.update.service'

    service = fields.Selection(selection_add=[
        ('RU_CBRF_getter', 'The Central Bank of the Russia Federation'),
    ])
