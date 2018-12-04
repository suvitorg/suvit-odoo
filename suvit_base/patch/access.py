# -*- coding: utf-8 -*-
import logging

import openerp
from openerp import api, models
from openerp.modules.loading import load_modules as oe_load_modules

_logger = logging.getLogger(__name__)


class PatchedAccessImport(models.Model):
    _inherit = 'ir.model.access'

    # monkey patch import data to remove comments in Access cvs files
    @api.model
    def load(self, fields, datas):
        new_datas = []
        for row in datas:
            if not row[0]: # missing id. Access comment
                continue
            new_datas.append(row)

        return super(PatchedAccessImport, self).load(fields, new_datas)


def format_load_modules(db, force_demo=False, status=None, update_module=False):
    oe_load_modules(db, force_demo, status, update_module)

    cr = db.cursor()
    registry = openerp.registry(cr.dbname)

    err = []
    cr.execute("""select model,name from ir_model where id NOT IN (select distinct model_id from ir_model_access)""")
    for (model, name) in cr.fetchall():
        if model in registry and not registry[model].is_transient() and not isinstance(registry[model], openerp.osv.orm.AbstractModel):
            err.append('The model %s has no access rules, consider adding one. E.g. access_%s,access_%s,model_%s,,1,0,0,0' %
                       (model, model.replace('.', '_'), model.replace('.', '_'), model.replace('.', '_')))
    cr.close()
    if err:
        raise Exception("\n".join(err))
