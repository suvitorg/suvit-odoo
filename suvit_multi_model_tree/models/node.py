# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TreeNode(models.AbstractModel):
    _name = 'suvit.tree.node.mixin'
    _description = u'Узел дерева'
    _order = 'parent_id,sequence,id'
    _use_full_ids = False

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
    @api.depends('shortcut_id', 'object_id')
    def compute_name(self):
        for rec in self:
            if rec.shortcut_id:
                rec.name = u'[Я] %s' % rec.shortcut_id.name
            elif rec.object_id:
                rec.name = getattr(rec.object_id, rec.object_id._rec_name or 'title', '-')

    @api.multi
    def action_remove(self):
        self.write({'parent_id': False})

    @api.model
    def change_parent(self):
        pass

    # API for full ids
    @api.multi
    def evaluate_ids(self):
        if not any(isinstance(id, basestring) for id in self.ids):
            return

        new_ids = []
        for id in self.ids:
            new_ids.append(int(str(id).split('-')[-1]))

        # XXX This is needed to clear cache string ids
        self.invalidate_cache()
        self._ids = new_ids

    @api.multi
    def read(self, fields=None, *args, **kwargs):
        if not self._use_full_ids:
            return super(TreeNode, self).read(fields, *args, **kwargs)

        self.evaluate_ids()

        res = super(TreeNode, self).read(fields, *args, **kwargs)

        parents = self.env.context.get('tree_parent_ids')
        if parents:
            parent_prefix = '-'.join(str(x) for x in parents)
        else:
            parent_prefix = None

        for row in res:
            if parent_prefix:
                row['real_id'] = row['id']
                row['id'] = '%s-%s' % (parent_prefix, row['id'])

            if 'tree_child_ids' in row:
                new_children = []
                for child in row['tree_child_ids']:
                    new_children.append('%s-%s' % (row['id'], child if isinstance(child, int) else child.id))
                row['tree_child_ids'] = new_children
        return res
