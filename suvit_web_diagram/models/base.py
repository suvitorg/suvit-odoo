# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields


class Diagram(models.AbstractModel):
    _name = 'suvit.web.diagram'

    x = fields.Integer()
    y = fields.Integer()
