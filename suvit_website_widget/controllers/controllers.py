# -*- coding: utf-8 -*-
from odoo import http


class SuvitWebsiteWidget(http.Controller):
    @http.route('/widgets/', auth='public', website=True)
    def index(self, **kw):
        WidgetGroups = http.request.env['odoo.suvit.web.ui.widget.group']
        return http.request.render('suvit_website_widget.index', {
            'widget_groups': WidgetGroups.search([])
        })

    @http.route('/widgets/<int:id>', auth='public', website=True)
    def widget(self, id):
        Widget = http.request.env['odoo.suvit.web.ui.widget']
        return http.request.render('suvit_website_widget.widget_page', {
            'widget': Widget.search([('id', '=', id)])
        })
