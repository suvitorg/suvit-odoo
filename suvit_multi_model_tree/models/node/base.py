# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TreeNode(models.AbstractModel):
    _name = 'suvit.tree.node.mixin'
    _description = u'Узел дерева'
    # _order = 'parent_id,sequence,id'
    _parent_store = True
    _parent_order = 'sequence,id'
    _order = 'parent_left'
    _use_full_ids = True
    _root_domain = [('parent_id', '=', False)]
    _copy_suffix = u'Копия'
    _duplicate_prefix = u'D_'
    _tree_icon_map = {
        None: 'gtk-directory',  # node without object_id
    }

    parent_id = fields.Many2one(string=u'Принадлежность',
                                comodel_name=_name,
                                ondelete='cascade',
                                index=True,
                                track_visibility='onchange')
    parent_left = fields.Integer(string=u'Left Parent',
                                 index=True)
    parent_right = fields.Integer(string=u'Right Parent',
                                  index=True)

    child_ids = fields.One2many(string=u'Состав',
                                comodel_name=_name,
                                inverse_name='parent_id')
    tree_child_ids = fields.One2many(comodel_name=_name,
                                     compute='compute_tree_child_ids')

    sequence = fields.Integer(string=u'Порядок',
                              default=99)

    object_id = fields.Reference(string=u'Связь',
                                 selection='compute_selection_object_id',
                                 index=True,
                                 track_visibility='onchange'
                                 )

    # Link
    shortcut_id = fields.Many2one(string="Дубль к",
                                  comodel_name=_name,
                                  ondelete='cascade',
                                  track_visibility='onchange')
    duplicate_ids = fields.One2many(string=u'Дубли',
                                    comodel_name=_name,
                                    inverse_name='shortcut_id')
    self_id = fields.Many2one(string="Связь",
                              comodel_name=_name,
                              compute='compute_self')

    name = fields.Char(string=u'Наименование',
                       compute='compute_name',
                       store=True,
                       copy=True,
                       readonly=False,
                       track_visibility='onchange')
    full_name = fields.Char(string=u'Полный путь',
                            compute='compute_full_name',
                            help=u'Имя узла вместе с родителями')

    title = fields.Char(string=u'Подсказка',
                        compute='compute_title')
    icon = fields.Char(string=u'Иконка',
                       compute='compute_icon')
    tree_type = fields.Char(string=u'Тип',
                            compute='compute_tree_type',
                            store=True)

    all_child_ids = fields.Many2many(string=u"Все Дети",
                                     comodel_name=_name,
                                     compute='compute_all_child_ids')
    all_parent_ids = fields.Many2many(string=u"Все Родители",
                                      comodel_name=_name,
                                      compute='compute_all_parent_ids')

    @api.multi
    def compute_all_child_ids(self):
        for rec in self:
            straight_child_ids = self.search(
                [('parent_left', '>', rec.self_id.parent_left),
                 ('parent_right', '<', rec.self_id.parent_right)])
            # XXX need to get correct childs all_child_ids from child.self_id
            rec.all_child_ids = straight_child_ids + straight_child_ids.mapped('shortcut_id.all_child_ids')

    @api.multi
    def compute_all_parent_ids(self):
        for rec in self:
            rec.all_parent_ids = self.search(
                [('parent_left', '<', rec.parent_left),
                 ('parent_right', '>', rec.parent_right)],
                order='parent_left')

    @api.multi
    @api.onchange('object_id', 'shortcut_id')
    def compute_icon(self):
        for rec in self:
            if rec.shortcut_id:
                rec.self_id.compute_icon()
                icon = rec.self_id.icon
            else:
                icon = self._tree_icon_map.get(rec.object_id._name
                                               if rec.object_id else None)

            rec.icon = icon

    @api.model
    def compute_selection_object_id(self):
        result = []
        return result

    @api.multi
    @api.depends('object_id', 'shortcut_id')
    def compute_tree_type(self):
        for rec in self:
            main_obj = rec.self_id.object_id
            rec.tree_type = main_obj._name if main_obj else self._name

    # low level
    @classmethod
    def _add_field(cls, name, field):
        super(TreeNode, cls)._add_field(name, field)

        if isinstance(field, fields._Relational):
            if field.comodel_name == 'suvit.tree.node.mixin':
                field.comodel_name = cls.__name__

            # print 'TreeNode._add_field', cls.__name__, name, field.comodel_name

    @api.one
    @api.constrains('parent_id')
    def check_recursion(self):
        super(TreeNode, self)._check_recursion()

    @api.model
    def create(self, vals):
        # print 'TreeNode.create', vals
        new_obj = super(TreeNode, self).create(vals)

        # when node create from python code without name, compute name
        if not vals.get('name'):
            new_obj.compute_name()

        return new_obj

    @api.multi
    def write(self, vals):
        # print 'TreeNode.write', self, vals
        res = super(TreeNode, self).write(vals)
        if 'name' not in vals and \
           ('shortcut_id' in vals or 'object_id' in vals):
            self.compute_name()
            self.mapped('shortcut_id').compute_name()

        return res

    @api.multi
    @api.onchange('shortcut_id', 'object_id', 'duplicate_ids')
    # api.depends('shortcut_id.name', 'object_id', 'duplicate_ids')
    def compute_name(self):
        for rec in self:
            if not rec.object_id and not rec.shortcut_id:
                continue
            elif rec.shortcut_id:
                name = rec.shortcut_id.name
            else:
                name = getattr(rec.object_id,
                               rec.object_id._rec_name or u'title', u'-')
            rec.name = name

    @api.multi
    def compute_full_name(self):
        for rec in self:
            # use TreeNode._order = 'parent_left' instead of .sorted()
            rec.full_name = u' / '.join(part or '-'
                                        for part in (rec.all_parent_ids
                                            + rec).mapped('name'))

    @api.model
    def root_child_ids(self):
        return self.search(self._root_domain)

    @api.multi
    def compute_tree_child_ids(self):
        for rec in self:
            if rec.shortcut_id:
                childs = rec.shortcut_id.child_ids
            else:
                childs = rec.child_ids

            rec.tree_child_ids = childs

    @api.multi
    def compute_title(self):
        for rec in self:
            tooltip = getattr(rec.object_id, 'tooltip', None)
            if not tooltip:
                tooltip = getattr(rec.object_id, 'title', rec.name)
            rec.title = tooltip

    @api.multi
    def compute_self(self):
        for rec in self:
            self_id = rec
            if rec.shortcut_id:
                while self_id.shortcut_id:
                    self_id = self_id.shortcut_id

            rec.self_id = self_id

    @api.multi
    def action_change_parent(self):
        new_parent_id = self.env.context.get('new_parent_id')
        if new_parent_id:
            new_parent = self.browse(new_parent_id).self_id
        else:
            new_parent = self.browse()

        old_parent_id = self.env.context.get('old_parent_id')
        if old_parent_id:
            old_parent = self.browse(old_parent_id).self_id
        else:
            old_parent = self.browse()

        sequence = self.env.context.get('new_position')

        # print 'TreeNode.change_parent', old_parent,
        # print new_parent, sequence, self.env.context
        if old_parent != new_parent:
            self.write({'parent_id': new_parent.id})

        self.action_change_sequence(new_parent, sequence)

    @api.multi
    def action_change_sequence(self, new_parent, sequence):
        if sequence is None:
            return

        # print 'change_sequence for', new_parent, self._root_domain
        if new_parent:
            child_ids = new_parent.child_ids
        else:
            child_ids = self.root_child_ids()

        # print 'change_sequence', self,
        # print [(c.id, c.sequence) for c in child_ids], sequence
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

        # print 'change_sequence_after', self,
        # print [(c.id, c.sequence) for c in child_ids]

        # Temp comment update of parent_left, pright because of slow update
        return

        # XXX try to recalc parent_left, pright find more correct solution
        if new_parent:
            child_ids.write({'parent_id': False})
            child_ids.write({'parent_id': new_parent})
        else:
            # XXX recalc whole tree
            self._parent_store_compute()

    @api.multi
    def get_formview_action(self):
        self.ensure_one()

        obj = self.self_id
        if 'node_settings_form' not in self.env.context:
            obj = obj.object_id or obj

        if isinstance(obj, TreeNode):
            obj = super(TreeNode, obj)

        act = obj.get_formview_action()
        return act[0] if type(act) == list else act

    @api.multi
    def get_origin_duplicate_ids(self):
        orig_ids = self.filtered(lambda r: not r.shortcut_id)
        return orig_ids, self - orig_ids

    @api.multi
    def fix_copy_name(self):
        for rec in self:
            if rec.name and not rec.name.endswith(rec._copy_suffix):
                rec.name = u"%s %s" % (rec.name, rec._copy_suffix)

    @api.multi
    def fix_duplicate_name(self):
        for rec in self:
            if rec.name and not rec.name.startswith(rec._duplicate_prefix):
                rec.name = u"%s%s" % (rec._duplicate_prefix, rec.name)

    @api.multi
    def unlink(self):
        orig_ids, dupl_ids = self.get_origin_duplicate_ids()
        self = orig_ids + dupl_ids.mapped('shortcut_id')
        return super(TreeNode, self).unlink()

    @api.multi
    def action_remove(self):
        orig_ids, dupl_ids = self.get_origin_duplicate_ids()
        orig_ids.write({'parent_id': False})
        dupl_ids.write({'shortcut_id': False})
        dupl_ids.unlink()

    @api.multi
    def action_exclude(self):
        orig_ids, dupl_ids = self.get_origin_duplicate_ids()
        if dupl_ids:
            raise api.Warning(u"Нельзя исключать Дубликаты")
        for rec in self:
            rec.self_id.child_ids.write({'parent_id': rec.parent_id.id})
            rec.unlink()

    @api.multi
    def action_copy(self, default=None):
        for rec in self:
            rec = rec.self_id
            copy = rec.copy(default=default)
            copy.fix_copy_name()
            for child in rec.child_ids:
                default = {'parent_id': copy.id}
                child.action_copy(default)

    @api.multi
    def action_duplicate(self):
        for rec in self:
            copy = rec.copy(default={'shortcut_id': rec.self_id.id})
            (copy + rec).fix_duplicate_name()
