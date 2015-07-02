# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields


class Activity(models.Model):
    _inherit = 'workflow.activity'

    x = fields.Integer()
    y = fields.Integer()
