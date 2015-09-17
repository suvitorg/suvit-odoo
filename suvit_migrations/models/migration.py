# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class Migration(models.Model):
    _name = 'suvit.migration'
    _description = u"Миграция"

    name = fields.Char(string=u"Название",
                       required=True,
                       )
    description = fields.Text(string=u"Описание",
                              )
    implemented = fields.Boolean(string=u"Выполнена",
                                 default=False,
                                 )
    module_id = fields.Many2one(string=u"Модуль",
                                comodel_name='ir.module.module',
                                compute='compute_model_data',
                                )
    ext_id = fields.Char(string=u"Метод",
                         compute='compute_model_data',
                         )

    @api.multi
    def compute_model_data(self):
        data_obj = self.env['ir.model.data']
        module_obj = self.env['ir.module.module']
        for rec in self:
            data = data_obj.search([('model', '=', rec._name),
                                    ('res_id', '=', rec.id)],
                                   limit=1)
            if data:
                rec.ext_id = data.name
                rec.module_id = module_obj.search([('name', '=', data.module)],
                                                  limit=1)

    @api.model
    def run_all(self):
        self.search([('implemented', '=', False)]).run()

    @api.multi
    def run(self):
        for rec in self.filtered(lambda r: r.ext_id):
            if not hasattr(rec, rec.ext_id):
                exceptions.Warning(u"Миграция %s не работает" % rec.name)
            getattr(rec, rec.ext_id)()
            rec.implemented = True

    @api.model
    def create(self, values):
        rec = super(Migration, self).create(values)
        if not rec.implemented:
            rec.run()

        return rec

    @api.multi
    def write(self, values):
        res = super(Migration, self).write(values)
        for rec in self:
            if not rec.implemented:
                rec.run()

        return res
