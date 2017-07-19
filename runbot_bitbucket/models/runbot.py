# -*- coding: utf-8 -*-
import re

from openerp import api, models, fields

class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    uses_bitbucket = fields.Boolean(string='Use BitBucket')

class RunbotBrunch(models.Model):
    _inherit = 'runbot.branch'

    branch_url = fields.Char(compute='compute_branch_url')

    @api.multi
    def compute_branch_url(self):
        for branch in self:
            if branch.repo_id.uses_bitbucket:
                if re.match('^[0-9]+$', branch.branch_name):
                    branch.branch_url = "https://%s/pull-requests/%s" % (branch.repo_id.base, branch.branch_name)
                else:
                    branch.branch_url = "https://%s/branch/%s" % (branch.repo_id.base, branch.branch_name)
            else:
                res = branch._get_branch_url('branch_url', [])
                branch.branch_url = res.values()[0]
        return
