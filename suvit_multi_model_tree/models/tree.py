# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MultiTree(models.AbstractModel):
    _name = 'suvit.multi.model.tree'
    _rec_name = 'tree_name'

    _tree_root_model = None
    _tree_prefix = ''

    tree_name = fields.Char(string=u"Наим",
                            compute='compute_name',
                            )
    tree_obj_id = fields.Reference(string=u"Объект",
                                   selection=[],
                                   compute='compute_obj_id',
                                   )
    tree_parent_id = fields.Many2one(comodel_name='suvit.multi.model.tree',
                                     compute='compute_parent_id',
                                     search='search_parent_id',
                                     )
    tree_child_ids = fields.Many2many(comodel_name='suvit.multi.model.tree',
                                      compute='compute_child_ids',
                                      )

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
                    break

    @api.multi
    def compute_name(self):
        for rec in self:
            if rec.tree_obj_id:
                rec.tree_name = getattr(rec.tree_obj_id, rec.tree_obj_id._rec_name, False)

    @api.multi
    def compute_parent_id(self):
        tree_parent_field = self.get_tree_parent_field()
        tree_field = self.get_tree_field()
        for rec in self:
            rec_tree_parent_field = getattr(rec.tree_obj_id, tree_parent_field)
            if rec_tree_parent_field:
                rec.tree_parent_id = getattr(getattr(rec.tree_obj_id, rec_tree_parent_field), tree_field)

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
        for rec in self:
            rec_tree_childs_field = getattr(rec.tree_obj_id, tree_childs_field, None)
            if rec_tree_childs_field:
                rec.tree_child_ids = [getattr(child, tree_field).id for child in getattr(rec.tree_obj_id, rec_tree_childs_field)]

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        res = super(MultiTree, self).read(fields, load)

        tree_childs_field = self.get_tree_childs_field()
        if fields and tree_childs_field in fields:
            for vals in res:
                vals[tree_childs_field] = self.browse(vals['id']).tree_child_ids.ids

        return res

    @api.multi
    def get_formview_action(self):
        self.ensure_one()

        tree_obj = self.tree_obj_id
        if tree_obj and getattr(tree_obj, '%stree_form_action' % self._tree_prefix, True):
            act = tree_obj.get_formview_action()
            return act[0] if type(act) == list else act
        elif tree_obj:
            return False

        return super(MultiTree, self).get_formview_action()
