# -*- coding: utf-8 -*-
from odoo import http


class SuvitWebsiteWidget(http.Controller):
    @http.route('/suvit_website_widget/main/', auth='public', website=True)
    def index(self, **kw):
        WidgetGroups = http.request.env['odoo.suvit.web.ui.widget.group']
        return http.request.render('suvit_website_widget.index', {
            'widget_groups': WidgetGroups.search([])
        })

    @http.route('/suvit_website_widget/<int:id>', auth='public', website=True)
    def widget(self, id):
        Widget = http.request.env['odoo.suvit.web.ui.widget']
        return http.request.render('suvit_website_widget.widget_page', {
            'widget': Widget.search([('id', '=', id)])
        })

#     @http.route('/suvit_website_widget/suvit_website_widget/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('suvit_website_widget.listing', {
#             'root': '/suvit_website_widget/suvit_website_widget',
#             'objects': http.request.env['suvit_website_widget.suvit_website_widget'].search([]),
#         })

#     @http.route('/suvit_website_widget/suvit_website_widget/objects/<model("suvit_website_widget.suvit_website_widget"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('suvit_website_widget.object', {
#             'object': obj
#         })
