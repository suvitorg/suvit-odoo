# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('js_node_tree', 'JS Node Tree')])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('js_node_tree', 'JS Node Tree')])

models.BaseModel._get_default_js_node_tree_view = models.BaseModel._get_default_tree_view
