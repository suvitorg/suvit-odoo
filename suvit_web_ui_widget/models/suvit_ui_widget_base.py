# -*- coding: utf-8 -*-
import logging
import urllib.parse

from openerp import api, fields, models


class SuvitWidgetBase(models.AbstractModel):
    _name = 'suvit.ui.widget.base'
    _description = u"Базовая модель для хранения информации о виджетах"

    name = fields.Char(string=u'Наименование')

    image_read = fields.Binary(string=u"Изображение",
                               )
    image_read_html = fields.Html(string=u'Скачать изображение',
                                  compute='compute_image_read')

    image_write = fields.Binary(string=u"Изображение. режим запись",)
    image_write_html = fields.Html(string=u'Скачать изображение',
                                   compute='compute_image_read')

    @api.multi
    def compute_image_read(self):
        for rec in self:
            if rec.image_read:
                rec.image_read_html = '<a href="%s" target="_blank"><img style="max-height: 200px" src="%s"/></a>' % \
                                      (rec.get_image_url(img_field_name='image_read', type='image'),
                                       rec.get_image_url(img_field_name='image_read'))

            if rec.image_write:
                rec.image_write_html = '<a href="%s" target="_blank"><img style="max-height: 200px" src="%s"/></a>' % \
                                       (rec.get_image_url(img_field_name='image_write', type='image'),
                                        rec.get_image_url(img_field_name='image_write'))

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
