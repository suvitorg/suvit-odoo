# -*- coding: utf-8 -*-
import logging
import cStringIO
import csv
import os

import odoo
import openerp
from openerp import models
from openerp.modules.loading import load_modules as oe_load_modules
from odoo.tools.convert import convert_csv_import
from odoo import SUPERUSER_ID, _
from odoo.tools.misc import ustr

_logger = logging.getLogger(__name__)


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
        pass
        # raise Exception("\n".join(err))

openerp.modules.load_modules = format_load_modules

def format_convert_csv_import(cr, module, fname, csvcontent, idref=None, mode='init',
        noupdate=False):
    '''Import csv file :
        quote: "
        delimiter: ,
        encoding: utf-8'''
    if not idref:
        idref={}
    model = ('.'.join(fname.split('.')[:-1]).split('-'))[0]
    #remove folder path from model
    head, model = os.path.split(model)

    input = cStringIO.StringIO(csvcontent) #FIXME
    reader = csv.reader(input, quotechar='"', delimiter=',')
    fields = reader.next()

    if not (mode == 'init' or 'id' in fields):
        _logger.error("Import specification does not contain 'id' and we are in init mode, Cannot continue.")
        return

    datas = []
    for line in reader:
        if not (line and any(line)):
            continue
        if not line[0]:
            continue
        try:
            datas.append(map(ustr, line))
        except Exception:
            _logger.error("Cannot import the line: %s", line)

    context = {
        'mode': mode,
        'module': module,
        'noupdate': noupdate,
    }
    env = odoo.api.Environment(cr, SUPERUSER_ID, context)
    result = env[model].load(fields, datas)
    if any(msg['type'] == 'error' for msg in result['messages']):
        # Report failed import and abort module install
        warning_msg = "\n".join(msg['message'] for msg in result['messages'])
        raise Exception(_('Module loading %s failed: file %s could not be processed:\n %s') % (module, fname, warning_msg))

odoo.tools.convert.convert_csv_import = format_convert_csv_import
