# -*- coding: utf-8 -*-
from openerp import api, models, fields, exceptions


class SuvitWebUiWidgetGroup(models.Model):
    _name = 'odoo.suvit.web.ui.widget.group'
    _description = u"Группа виджетов по назначению"

    name = fields.Char(string=u"Наименование группы", )

    widget_ids = fields.One2many(string=u"Виджеты",
                                 comodel_name='odoo.suvit.web.ui.widget',
                                 inverse_name='group_id', )


class SuvitWebUiWidget(models.Model):
    _name = 'odoo.suvit.web.ui.widget'
    _description = u"Виджет"

    name = fields.Char(string=u"Наименование виджета", )

    group_id = fields.Many2one(string=u"Группа",
                               comodel_name='odoo.suvit.web.ui.widget.group', )

    features_group_ids = fields.One2many(string=u"Группы свойств виджета",
                                         comodel_name='odoo.suvit.web.ui.widget.features.group',
                                         inverse_name='widget_id', )

    text = fields.Text(string=u"Описание виджета")


class SuvitWebUiWidgetFaturesGroup(models.Model):
    _name = 'odoo.suvit.web.ui.widget.features.group'
    _description = u"Группа свойств виджета"

    name = fields.Char(string=u"Группа свойств виджета", )

    widget_id = fields.Many2one(string=u"Виджет",
                                comodel_name='odoo.suvit.web.ui.widget', )

    feature_ids = fields.One2many(string=u"Группы свойств виджета",
                                  comodel_name='odoo.suvit.web.ui.widget.feature',
                                  inverse_name='group_id', )


class SuvitWebUiWidgetFature(models.Model):
    _name = 'odoo.suvit.web.ui.widget.feature'
    _description = u"Свойство виджета"

    name = fields.Char(string=u"Свойство виджета", )

    group_id = fields.Many2one(string=u"Группа свойств виджета",
                               comodel_name='odoo.suvit.web.ui.widget.features.group', )

    widget_id = fields.Many2one(string=u"Виджет",
                                related='group_id.widget_id',
                                store=True, )

    text = fields.Text(string=u"Описание свойства")
