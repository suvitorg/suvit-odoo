# -*- coding: utf-8 -*-
import urllib.parse

from openerp import api, fields, models


class WidgetType(models.Model):
    _name = 'suvit.ir.ui.widget.type'
    _description = u'Шаблон Виджета'
    _inherit = 'suvit.ui.widget.base'

    name = fields.Char(string=u'Наименование')

    code = fields.Char(string=u'Код')

    view_type = fields.Selection(string=u'Тип вида',
                                 selection=[('form', u'Карточка'),
                                            ('list', u'Ведомость'),
                                            ('tree', u'Дерево'),
                                            ('kanbab', u'Таблица карточек (Канбан)'),
                                            ('calendar', u'Календарь'),
                                 ])

    # only for form view
    mode = fields.Selection(string=u'Режим',
                            selection=[('read', u'Чтение'),
                                       ('write', u'Запись')], # only form
                            default='read')
    type = fields.Selection(string=u'Тип',
                            selection=[('field', u'Поле'),
                                       ('group', u'Группа полей'),
                                       ('area', u'Область')])

    description = fields.Text(string=u'Описание')

    # TODO list of attrs
    options = fields.Text(string=u'Настройки')

    parent_id = fields.Many2one(string=u'Принадлежность',
                                comodel_name=_name)
    child_ids = fields.One2many(string=u'Состав',
                                comodel_name=_name,
                                inverse_name='parent_id')

class WidgetTree(models.Model):
    _name = 'suvit.node.ui.widget.type'
    _description = u'Узел дерева виджетов'
    _inherit = 'suvit.tree.node.mixin'

    _tree_icon_map = {
        None: 'gtk-directory',  # node without object_id
        'suvit.ir.ui.widget.type': 'gtk-info',
    }

    # XXX. restore
    _order = 'parent_id,sequence,id'


    image_read = fields.Binary(string=u"Изображение",
                               compute='compute_image_read')

    image_html = fields.Html(string=u'Изображение',
                             compute='compute_image_read')

    #@api.model
    #def create(self):
    #    pass


    @api.model
    def get_tree_config(self):
        return {'#': {
                   'valid_children': [self._name],
                },
                self._name: {
                        'name': u'Группа',
                        'create': True,
                        'edit': True,
                        'copy': True,
                        'delete': True,
                        'settings': True,
                        'valid_children': [self._name,
                                           'suvit.ir.ui.widget.type']
                },
                'suvit.ir.ui.widget.type': {
                    'name': u'Виджет',
                    'create': True,
                    'edit': True,
                    'copy': True,
                    'delete': True,
                    'settings': True,
                    'valid_children': [self._name,
                                       'suvit.ir.ui.widget.type']
                }
               }

    @api.model
    def compute_selection_object_id(self):
        return [
                ('suvit.ir.ui.widget.type', u'Виджет'),
                ]

    @api.multi
    def get_image_url(self, img_field_name='image', type='saveas'):
        self.ensure_one()
        query_dict = {'model': self._name,
                      'id': self.id,
                      'field': img_field_name}
        if img_field_name == 'image':
            query_dict['filename_field'] = 'image_fname'
        query = urllib.parse.urlencode(query_dict)
        image_url = '/web/binary/%s?' % type + query

        return image_url

    @api.multi
    def compute_image_read(self):
        for rec in self:
            if not rec.object_id:
                continue
            rec.image_read = rec.object_id.image_read
            if not rec.image_read:
                continue

            rec.image_html = '<a href="%s" target="_blank"><img src="%s"/></a>' % \
                                 (rec.get_image_url(img_field_name='image_read', type='image'),
                                  rec.get_image_url(img_field_name='image_read'))


class Widget(models.Model):
    _name = 'suvit.ir.ui.widget'
    _description = u'Виджет'

    view_id = fields.Many2one(string=u'Вид',
                              comodel_name='ir.ui.view')

    widget_type_id = fields.Many2one(string=u'Шаблон виджета',
                                     comodel_name='suvit.ir.ui.widget.type')

    # attrs
