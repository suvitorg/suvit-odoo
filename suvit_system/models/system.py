# -*- coding: utf-8 -*-
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)

def get_odoo_icons():
    result = []
    for filename in os.listdir(os.path.join(web.__path__[0], 'static', 'src', 'img', 'icons')):
        icon_name = os.path.splitext(filename)[0]
        result.append([icon_name, icon_name])
    return result


class OdooModel(models.Model):
    _inherit = 'ir.model'

    system_tree = fields.Boolean(string=u'Используется в дереве Системы')

    system_tree_odoo_icon = fields.Selection(string=u'ИД Иконки',
                                             selection=lambda s: s.compute_selection_odoo_icon(),
                                             help=u'Стандартные иконки Odoo')
    #system_tree_path_icon
    #system_tree_file_icon

    system_tree_icon_display = fields.Html(string=u'Иконка',
                                           compute='compute_tree_icon_display')

    # ability to set root types
    # ability to set child types

    # todo open action field
    #activate_action = fields.M2O

    @api.model
    def compute_selection_odoo_icon(self):
        # TODO cache
        return get_odoo_icons()

    @api.multi
    @api.onchange('system_tree_odoo_icon')
    def compute_tree_icon_display(self):
        for rec in self:
            if rec.system_tree_odoo_icon:
                path = '/web/static/src/img/icons/%s.png' % rec.system_tree_odoo_icon
                img = '<image src="%s" title="%s" alt="%s"/>' % (path,
                                                                 rec.system_tree_odoo_icon,
                                                                 rec.system_tree_odoo_icon)
                rec.system_tree_icon_display = img


class SystemNode(models.Model):
    _name = 'suvit.system.node'
    _description = u'Узел дерева системы'
    _inherit = ['suvit.tree.node.mixin',
                'mail.thread',
                'ir.needaction_mixin',
                ]

    object_id = fields.Reference(selection='compute_selection_object_id',
                                 )

    @api.model
    def compute_selection_object_id(self):
        result = super(SystemNode, self).compute_selection_object_id()
        for model in self.env['ir.model'].search([('system_tree', '=', True)]):
            result.append([model.model, model.name])

        return result

    @api.multi
    @api.onchange('object_id', 'shortcut_id')
    def compute_icon(self):
        for rec in self:
            super(SystemNode, rec).compute_icon()

            if not rec.icon and rec.object_id:
                model = self.env['ir.model'].search([('model', '=', rec.object_id._name)])
                icon = model.system_tree_odoo_icon
                rec.icon = icon

    @api.model
    def get_tree_types(self):
        result = {}
        for tree_type in self.compute_selection_object_id():
            type_dict = result[tree_type[0]] = dict(name=tree_type[1])
            # TODO. set perms
            # TODO. set valid_children
        return types
