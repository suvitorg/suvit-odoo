# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)


class Release(models.Model):
    _name = 'suvit.release'
    _description = u"Релиз"
    _inherit = 'mail.thread'
    _order = 'create_date desc'

    name = fields.Char(string=u"Номер релиза")

    description = fields.Text(string=u"Описание",
                              required=True)

    # Возможно заменить на обновление текущего модуля?
    modules_to_update = fields.Char(string=u'Модули для обновления',
                                    help=u'Перечисленные через запятую тех. имена модулей, пример suvit_base,suvit_core')

    module_ids = fields.One2many(string=u'Модули',
                                 comodel_name='ir.module.module',
                                 compute='compute_module_ids')

    # Создана в модуле
    # module_id = fields.Many2one(comodel_name='ir.module.module')

    @api.model
    def create(self, values):
        rec = super(Release, self).create(values)
        channel = self.env.ref('suvit_release.mail_channel_suvit_release')
        channel.message_post(body=values['description'],
                             subtype='mail.mt_comment')
        return rec

    @api.multi
    def compute_module_ids(self):
        for rec in self:
            modules = [module.strip() for module in rec.modules_to_update.split(',')]
            rec.module_ids = self.env['ir.module.module'].search([('module', 'in', modules)])
