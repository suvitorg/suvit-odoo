# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TreeNode(models.AbstractModel):
    _name = 'suvit.tree.node.mixin'
    _description = u'Узел дерева'
    _order = 'parent_id,sequence,id'
    _use_full_ids = False
    _root_domain = [('parent_id', '=', False)]

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
    self_id = fields.Many2one(string="",
                              comodel_name=_name,
                              compute='compute_self')

    name = fields.Char(string=u'Наименование',
                       compute='compute_name',
                       store=True,
                       readonly=False)

    @api.model
    def create(self, vals):
        #print 'TreeNode.create', vals
        new_obj = super(TreeNode, self).create(vals)

        # XXX ugly hack to fixed depends override 
        if not new_obj.name and 'name' in vals:
            new_obj.name = vals['name']

        return new_obj

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
    def compute_self(self):
        for rec in self:
            self_id = rec
            if rec.shortcut_id:
                while self_id.shortcut_id:
                    self_id = self_id.shortcut_id

            rec.self_id = self_id

    @api.multi
    def action_remove(self):
        self.write({'parent_id': False})

    @api.multi
    def action_change_parent(self, new_parent_id):

        if new_parent_id:
            new_parent = self.browse(new_parent_id).self_id
            #new_parent_obj = new_parent.tree_obj_id
        else:
            new_parent = new_parent_obj = self

        old_parent_id = self.env.context.get('old_parent_id')
        if old_parent_id:
            old_parent = self.browse(old_parent_id).self_id
            #old_parent_obj = old_parent.tree_obj_id
        else:
            old_parent = old_parent_obj = self

        sequence = self.env.context.get('new_position')

        # print 'TreeNode.change_parent', old_parent, new_parent, sequence
        if old_parent != new_parent:
            self.write({'parent_id': new_parent.id})

        self.action_change_sequence(new_parent, sequence)

    @api.multi
    def action_change_sequence(self, new_parent, sequence):
        if sequence is None:
            return

        if new_parent:
            child_ids = new_parent.child_ids
        else:
            # Tree root objects
            child_ids = self.search(self._root_domain)

        # print 'change_sequence', [(c.id, c.sequence) for c in child_ids], sequence
        i = 0
        for child in child_ids:
            if child == self:
                continue

            # print 'change', obj, child, i, sequence
            if i < sequence:
                child.sequence = i
            else:
                child.sequence = i + 1
            i += 1

        self.sequence = sequence
        # print 'change_sequence_after', [(c.id, c.sequence) for c in child_ids]

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
