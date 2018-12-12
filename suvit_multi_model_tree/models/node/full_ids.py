# -*- coding: utf-8 -*-
import logging

from openerp import models, fields, api

logger = logging.getLogger(__name__)


class TreeNode(models.AbstractModel):
    _inherit = 'suvit.tree.node.mixin'
    _use_full_ids = True

    # API for full ids
    @api.multi
    def evaluate_ids(self):
        if not any(isinstance(id, basestring) for id in self.ids):
            return self.ids

        # logger.info('Node.evaluate_ids before %s', self.ids)
        new_ids = []
        for id in self.ids:
            new_ids.append(int(str(id).split('-')[-1]))

        return new_ids

    @api.multi
    def read(self, fields=None, *args, **kwargs):
        if not self._use_full_ids:
            return super(TreeNode, self).read(fields, *args, **kwargs)

        new_ids = self.evaluate_ids()
        real_recs = self.search([('id', 'in', new_ids)])
        res = super(TreeNode, real_recs).read(fields, *args, **kwargs)

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
                    new_children.append('%s-%s' % (row['id'],
                                                   child
                                                   if isinstance(child, int)
                                                   else child.id))
                row['tree_child_ids'] = new_children
        return res
