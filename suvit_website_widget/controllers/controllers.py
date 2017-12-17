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

    @http.route('/widgets/modules/', auth='public', website=True)
    def modules(self, **kw):
        Modules = http.request.env['ir.module.module']
        return http.request.render('suvit_website_widget.modules', {
            'modules': Modules.search([])
        })

    @http.route('/widgets/modules/<name>', auth='public', website=True)
    def module(self, name):
        module_id = http.request.env['ir.module.module'].search([('name', '=', name)])
        widget_ids = http.request.env['odoo.suvit.web.ui.widget.feature'].\
            search([('system_module_id', '=', module_id.id)]).mapped('widget_id')
        return http.request.render('suvit_website_widget.module', {
            'widget_ids': widget_ids,
            'shortdesc': module_id.shortdesc
        })
