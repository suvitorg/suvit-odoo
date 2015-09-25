# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MaterialTree(models.AbstractModel):
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
        for rec in self:
            for model in self.get_tree_ref_models():
                obj = self.env[model].search([(self.get_tree_field(), '=', rec.id)],
                                             limit=1)
                if obj:
                    rec.tree_obj_id = obj
                    break

    @api.multi
    def compute_name(self):
        for rec in self:
            if rec.tree_obj_id:
                rec.name = getattr(rec.tree_obj_id, rec.tree_obj_id._rec_name, False)

    @api.multi
    def compute_parent_id(self):
        tree_parent_field = self.get_tree_parent_field()
        for rec in self:
            rec_tree_parent_field = getattr(rec.tree_obj_id, tree_parent_field)
            if rec_tree_parent_field:
                rec.tree_parent_id = getattr(rec.tree_obj_id, rec_tree_parent_field).tree_id

    @api.model
    def search_parent_id(self, operator, value):
        if operator == '=' and value == False:
            operator = 'in'
        else:
            operator = 'not in'

        if type(value) == bool and self._tree_root_model:
            tree_field = self.get_tree_field()
            roots = self.env[self._tree_root_model].search_read([], [tree_field])
            value = [root[tree_field][0] for root in roots]

        return [('id', operator, value)]

    @api.multi
    def compute_child_ids(self):
        tree_childs_field = self.get_tree_childs_field()
        for rec in self:
            rec_tree_childs_field = getattr(rec.tree_obj_id, tree_childs_field)
            if rec_tree_childs_field:
                rec.tree_child_ids = [child.tree_id.id for child in getattr(rec.tree_obj_id, rec_tree_childs_field)]

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        res = super(MaterialTree, self).read(fields, load)

        tree_childs_field = self.get_tree_childs_field()
        if fields and tree_childs_field in fields:
            for vals in res:
                vals[tree_childs_field] = self.browse(vals['id']).tree_child_ids.ids

        return res
