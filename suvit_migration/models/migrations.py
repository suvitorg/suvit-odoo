# -*- coding: utf-8 -*-
import os
import logging

from odoo import models, fields, api, exceptions
import odoo.tools as tools

logger = logging.getLogger(__name__)


class Migration(models.Model):
    _name = 'suvit.migration'
    _description = u"Миграция"
    _order = 'create_date desc'

    name = fields.Char(string=u"Название",
                       required=True,
                       )
    description = fields.Text(string=u"Описание",
                              )

    state = fields.Selection(string=u'Состояниe',
                             selection=[('new', u'Получена'),
                                        ('run', u'Выполняется'),
                                        ('done', u'Выполнена'),
                                        ('error', u'Ошибка'),
                                        ('cancel', u'Отменена')],
                             default='new')
    implemented = fields.Boolean(string=u"Выполнена",
                                 compute='compute_implemented',
                                 )

    module_id = fields.Many2one(string=u"Модуль",
                                comodel_name='ir.module.module',
                                compute='compute_model_data',
                                )
    method = fields.Char(string=u"Метод",
                         required=True,
                         )
    date_done = fields.Date(string=u"Дата выполнения",
                            )

    @api.multi
    def compute_implemented(self):
        for rec in self:
            rec.implemented = rec.state == 'done'

    @api.one
    @api.constrains('method')
    def check_method(self):
        if not hasattr(self, self.method):
            exceptions.ValidationError(u"Миграция %s не найдена" % self.method)

    @api.multi
    def compute_model_data(self):
        data_obj = self.env['ir.model.data']
        module_obj = self.env['ir.module.module']
        for rec in self:
            data = data_obj.search([('model', '=', rec._name),
                                    ('res_id', '=', rec.id)],
                                   limit=1)
            if data:
                rec.module_id = module_obj.search([('name', '=', data.module)],
                                                  limit=1)

    @api.model
    def run_all(self):
        self.search([('state', '=', 'new')]).run()

    @api.multi
    def run(self):
        now = fields.Date.today()
        if tools.config.options['test_enable'] or os.environ.get('GITLAB_CI', False):
            self.write({'state': 'done'})
            return

        # all migration must be called by SUPERUSER_ID and do not check active
        for rec in self.sudo().with_context(active_test=False)\
                       .filtered(lambda r: not r.implemented):
            migration_name = rec.method
            logger.info('start migration "%s"', migration_name)
            try:
                getattr(rec, migration_name)()
            except:
                logger.exception('Exception in migration "%s"', migration_name)
                rec.state = 'error'
            else:
                rec.state = 'done'
                rec.date_done = now
                logger.info('finish migration "%s"', migration_name)

    @api.model
    def create(self, values):
        rec = super(Migration, self).create(values)
        if not (rec.state == 'done' or tools.config.options['test_enable']):
            rec.run()

        return rec

    @api.multi
    def write(self, values):
        res = super(Migration, self).write(values)
        if list(values.keys()) == ['state'] or list(values.keys()) == ['date_done']:
            return res

        self.run()
        return res
