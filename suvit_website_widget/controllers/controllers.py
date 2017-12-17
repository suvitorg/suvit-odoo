# -*- coding: utf-8 -*-
from odoo import http


class SuvitWebsiteWidget(http.Controller):
    @http.route('/widgets/', auth='public', website=True)
    def index(self, **kw):
        WidgetGroups = http.request.env['odoo.suvit.web.ui.widget.group']
        return http.request.render('suvit_website_widget.index', {
            'widget_groups': WidgetGroups.search([])
        })

    @http.route('/widgets/<model("odoo.suvit.web.ui.widget"):w_id>', auth='public', website=True)
    def widget(self, w_id):
        WidgetGroups = http.request.env['odoo.suvit.web.ui.widget.group']
        Widget = http.request.env['odoo.suvit.web.ui.widget']
        FeaturesGroups = http.request.env['odoo.suvit.web.ui.widget.features.group']
        return http.request.render('suvit_website_widget.widget_page', {
            'widget_groups_ids': WidgetGroups.search([]),
            'widget_id': Widget.search([('display_name', '=', w_id.display_name)]),
            'features_groups_ids': FeaturesGroups.search([])
        })
