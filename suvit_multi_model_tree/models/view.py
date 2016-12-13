# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('js_node_tree', 'JS Node Tree')])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('js_node_tree', 'JS Node Tree')])
