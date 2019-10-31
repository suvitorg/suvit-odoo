# -*- coding: utf-8 -*-
import odoo
from odoo import models, fields


class Activity(models.Model):
    _inherit = 'workflow.activity'

    x = fields.Integer()
    y = fields.Integer()
