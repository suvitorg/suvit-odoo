# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MassObjectRel(models.Model):
    _name = 'suvit.mass.field.rel'
    _order = 'sequence'

    sequence = fields.Integer(string=u"Порядок",
                              required=True,
                              default=99,
                              )
    mass_id = fields.Many2one(string=u"Mass Object",
                              comodel_name='mass.object',
                              required=True,
                              ondelete='cascade',
                              )
    field_id = fields.Many2one(string=u"Поле",
                               comodel_name='ir.model.fields',
                               required=True,
                               ondelete='cascade',
                               )
    model_id = fields.Many2one(related='mass_id.model_id',
                               )
    model_ids = fields.Many2many(string=u'Список Моделей',
                                 comodel_name='ir.model',
                                 compute='compute_model_ids',
                                 )

    @api.multi
    @api.onchange('model_id')
    def compute_model_ids(self):
        for rec in self:
            rec.model_ids = rec.mass_id.onchange_model_id(rec.model_id.id)['value']['model_ids']


class MassObject(models.Model):
    _inherit = 'mass.object'

    field_rel_ids = fields.One2many(string=u"Поля",
                                    comodel_name='suvit.mass.field.rel',
                                    inverse_name='mass_id',
                                    )
    field_ids = fields.One2many(string=u"Поля",
                                comodel_name='ir.model.fields',
                                compute='compute_field_ids',
                                )

    @api.multi
    def compute_field_ids(self):
        for rec in self:
            rec.field_ids = rec.field_rel_ids.mapped('field_id')
