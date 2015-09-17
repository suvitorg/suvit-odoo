# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class Migration(models.Model):
    _inherit = 'suvit.migration'

    @api.model
    def _0000_test(self):
        print '_0000_test', self.search([])
