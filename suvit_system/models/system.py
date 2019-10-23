# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

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

    system_tree_can_create = fields.Boolean(string=u'Можно создавать')
    system_tree_can_edit = fields.Boolean(string=u'Можно редактировать',
                                          help=u'Редактировать, переименовывать')
    system_tree_can_copy = fields.Boolean(string=u'Можно копировать',
                                          help=u'Копировать, дубликаты')
    system_tree_can_delete = fields.Boolean(string=u'Можно удалять',
                                            help=u'Удалять, извлекать, отцеплять')
    system_tree_can_settings = fields.Boolean(string=u'Можно настраивать',
                                              default=True)

    system_tree_children_ids = fields.Many2many(string=u'Возможный состав',
                                                comodel_name='ir.model',
                                                domain=[('system_tree', '=', True)],
                                                relation="format_ir_model_system_children_rel",
                                                column1='from_id',
                                                column2='to_id',
                                                )

    # todo open action field
    #activate_action = fields.M2O

    @api.model
    def compute_selection_odoo_icon(self):
        # TODO cache
        return get_odoo_icons()

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
                # Odoo 11 activity
                # 'ir.needaction_mixin',
                ]
    _order = 'parent_id,sequence,id'
    parent_path = fields.Char(index=True)
    object_id = fields.Reference(selection='compute_selection_object_id',
                                 )

    @api.model
    def compute_selection_object_id(self):
        result = super(SystemNode, self).compute_selection_object_id()
        for model in self.env['ir.model'].search([('system_tree', '=', True)]):
            result.append([model.model, model.name])

        return result

    @api.onchange('object_id', 'shortcut_id')
    def compute_icon(self):
        for rec in self:
            super(SystemNode, rec).compute_icon()

            if not rec.icon and rec.object_id:
                model = self.env['ir.model'].search([('model', '=', rec.object_id._name)])
                icon = model.system_tree_odoo_icon
                rec.icon = icon

    @api.model
    def get_tree_config(self):
        result = OrderedDict()
        result[self._name] = dict(name=u'Группа',
                                  create=True,
                                  edit=True,
                                  copy=True,
                                  delete=True,
                                  settings=True)

        for tree_type in self.compute_selection_object_id():
            type_dict = result[tree_type[0]] = dict(name=tree_type[1])

            model = self.env['ir.model'].search([('model', '=', tree_type[0])])
            type_dict['create'] = model.system_tree_can_create
            type_dict['edit'] = model.system_tree_can_edit
            type_dict['copy'] = model.system_tree_can_copy
            type_dict['delete'] = model.system_tree_can_delete

            type_dict['valid_children'] = model.system_tree_children_ids.mapped('model')

        # In group may create all children
        result[self._name]['valid_children'] = result.keys()

        # Special key for root
        result['#'] = dict(valid_children=result.keys())

        return result
