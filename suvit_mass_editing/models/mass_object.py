# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MassObjectRel(models.Model):
    _name = 'suvit.mass.field.rel'
    _order = 'sequence,id'

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
    field_name = fields.Char(string=u"Наим в коде",
                             related='field_id.name',
                             readonly=True,
                             )
    field_type = fields.Selection(string=u"Тип",
                                  related='field_id.ttype',
                                  readonly=True,
                                  )
    model_id = fields.Many2one(related='mass_id.model_id',
                               )
    model_ids = fields.Many2many(string=u'Список Моделей',
                                 comodel_name='ir.model',
                                 compute='compute_model_ids',
                                 )

    @api.onchange('model_id')
    def compute_model_ids(self):
        for rec in self:
            rec.model_ids = [int(id_str)
                             for id_str in (rec.mass_id.model_list or '').split(',')
                             if id_str]



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

    def compute_field_ids(self):
        for rec in self:
            rec.field_ids = [r.field_id.id for r in rec.field_rel_ids]
