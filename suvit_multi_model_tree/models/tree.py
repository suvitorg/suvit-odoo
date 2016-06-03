# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MultiTree(models.AbstractModel):
    _name = 'suvit.multi.model.tree'
    _rec_name = 'tree_name'

    _tree_root_model = None
    _tree_prefix = ''
    _use_full_ids = False

    tree_name = fields.Char(string=u"Наим",
                            compute='compute_name',
                            inverse='inverse_name',
                            )
    tree_obj_id = fields.Reference(string=u"Объект",
                                   selection=[],
                                   compute='compute_obj_id',
                                   )
    tree_obj_real_id = fields.Integer(string=u"Ид объекта",
                                      compute='compute_obj_id')
    tree_type = fields.Char(string=u'Тип',
                            compute='compute_type',
                            help=u'Название модели')

    tree_parent_id = fields.Many2one(comodel_name='suvit.multi.model.tree',
                                     compute='compute_parent_id',
                                     search='search_parent_id',
                                     )
    tree_child_ids = fields.Many2many(comodel_name='suvit.multi.model.tree',
                                      compute='compute_child_ids',
                                      )

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
            return super(MultiTree, self).read(fields, *args, **kwargs)

        self.evaluate_ids()

        res = super(MultiTree, self).read(fields, *args, **kwargs)

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

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.tree_obj_id:
                rec.tree_obj_id.unlink()

    @api.model
    def get_tree_parent_field(self):
        return self._tree_prefix + 'tree_parent_field'

    @api.model
    def get_tree_childs_field(self):
        return self._tree_prefix + 'tree_childs_field'

    @api.model
    def get_tree_field(self):
        return self._tree_prefix + 'tree_id'

    @api.model
    def get_tree_ref_models(self):
        return [model[0] for model in self._fields['tree_obj_id'].selection]

    @api.multi
    def compute_obj_id(self):
        tree_field = self.get_tree_field()
        tree_models = self.get_tree_ref_models()

        for rec in self:
            for model in tree_models:
                obj = self.env[model].search([(tree_field, '=', rec.id)],
                                             limit=1)
                if obj:
                    rec.tree_obj_id = obj
                    rec.tree_obj_real_id = obj.id
                    break

    @api.multi
    def compute_name(self):
        for rec in self:
            if rec.tree_obj_id:
                rec.tree_name = getattr(rec.tree_obj_id, rec.tree_obj_id._rec_name, False)

    @api.multi
    def inverse_name(self):
        for rec in self:
            if rec.tree_obj_id:
                setattr(rec.tree_obj_id, rec.tree_obj_id._rec_name, rec.tree_name)

    @api.multi
    def compute_type(self):
        for rec in self:
            if rec.tree_obj_id:
                rec.tree_type = rec.tree_obj_id._name

    @api.multi
    def compute_parent_id(self):
        tree_parent_field = self.get_tree_parent_field()
        tree_field = self.get_tree_field()
        for rec in self:
            rec_tree_parent_field = getattr(rec.tree_obj_id, tree_parent_field, False)
            if rec_tree_parent_field:
                rec.tree_parent_id = getattr(getattr(rec.tree_obj_id, rec_tree_parent_field), tree_field, False)

    @api.model
    def search_parent_id(self, operator, value):
        if operator == '=' and value == False:
            operator = 'in'
        else:
            operator = 'not in'

        if type(value) == bool and self._tree_root_model:
            tree_field = self.get_tree_field()
            roots = self.env[self._tree_root_model].search_read([], [tree_field])
            value = [root[tree_field][0] for root in roots if root[tree_field]]

        return [('id', operator, value)]

    @api.multi
    def compute_child_ids(self):
        tree_field = self.get_tree_field()
        tree_childs_field = self.get_tree_childs_field()

        def get_tree_id(obj):
            if obj._name == self._name:
                return obj.id
            else:
                return getattr(obj, tree_field).id
        for rec in self:
            rec_tree_childs_field = getattr(rec.tree_obj_id, tree_childs_field, None)
            if rec_tree_childs_field:
                rec.tree_child_ids = [get_tree_id(child)
                                      for child in getattr(rec.tree_obj_id,
                                                           rec_tree_childs_field)]

    #@api.multi
    #def read(self, fields=None, load='_classic_read'):
    #    res = super(MultiTree, self).read(fields, load)
    #
    #    tree_childs_field = self.get_tree_childs_field()
    #    if fields and tree_childs_field in fields:
    #        for vals in res:
    #            vals[tree_childs_field] = self.browse(vals['id']).tree_child_ids.ids
    #
    #    return res

    @api.multi
    def change_parent(self, new_parent_id):
        new_parent = self.browse(new_parent_id)
        print 'CHANGE PARENT', self, new_parent

    @api.multi
    def get_formview_action(self):
        self.ensure_one()

        tree_obj = self.tree_obj_id
        if tree_obj and getattr(tree_obj, '%stree_form_action' % self._tree_prefix, True):
            act = tree_obj.get_formview_action()
            return act[0] if type(act) == list else act
        elif tree_obj:
            act = super(models.Model, tree_obj).get_formview_action()
            return act[0] if type(act) == list else act
        else:
            return False

        # return super(MultiTree, self).get_formview_action()
