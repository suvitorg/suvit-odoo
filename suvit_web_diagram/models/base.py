# -*- coding: utf-8 -*-
import odoo
from odoo import models, fields


class Diagram(models.AbstractModel):
    _name = 'diagram.node.position'

    x = fields.Integer()
    y = fields.Integer()
