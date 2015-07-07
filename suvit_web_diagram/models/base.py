# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields


class Diagram(models.AbstractModel):
    _name = 'diagram.node.position'

    x = fields.Integer()
    y = fields.Integer()
