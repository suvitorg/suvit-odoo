# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api

logger = logging.getLogger(__name__)

class Release(models.Model):
    _name = 'suvit.release'
    _description = u"Релиз"
    _inherit = 'mail.thread'
    
    name = fields.Integer(string=u"Номер релиза")
    description = fields.Text(string=u"Описание")
    
    @api.model
    def create(self, values):
        rec = super(Release, self).create(values)
        group = self.env.ref['group_suvit_release']
        group.message_post(body=values['description'])
        return rec
