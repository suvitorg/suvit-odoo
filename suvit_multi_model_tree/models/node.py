# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TreeNode(models.AbstractModel):
    _name = 'suvit.tree.node.mixin'
    _description = u'Узел дерева'
    _order = 'parent_id,sequence,id'

    parent_id = fields.Many2one(string=u'Принадлежность',
                                comodel_name=_name)

    child_ids = fields.One2many(string=u'Состав',
                                comodel_name=_name,
                                inverse_name='parent_id')

    sequence = fields.Integer(string=u'Порядок',
                              default=99)

    object_id = fields.Reference(string=u'Связь',
                                 selection=[],
                                 )

    # Link
    shortcut_id = fields.Many2one(string="Ярлык",
                                  comodel_name=_name)

    name = fields.Char(string=u'Наименование',
                       compute='compute_name',
                       store=True,
                       readonly=False)

    @api.multi
    @api.onchange('shortcut_id', 'object_id')
    def compute_name(self):
        for rec in self:
            if rec.shortcut_id:
                rec.name = u'[Я] %s' % rec.shortcut_id.name
            elif rec.object_id:
                rec.name = getattr(rec.object_id, rec.object_id._rec_name or 'title', '-')

    @api.model
    def change_parent(self):
        pass
