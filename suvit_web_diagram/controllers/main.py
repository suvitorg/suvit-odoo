# -*- coding: utf-8 -*-
import odoo
from odoo.addons.web_diagram.controllers.main import DiagramView


class Controller(DiagramView):

    @odoo.http.route('/web_diagram/diagram/get_diagram_info', type='json', auth='user')
    def get_diagram_info(self, req, id, model, node, connector,
                         src_node, des_node, label, **kw):
        result = super(Controller, self).get_diagram_info(req, id, model, node, connector,
                                                          src_node, des_node, label, **kw)
        node_obj = req.env[node]
        for node_id, node_val in result['nodes'].items():
            node_rec = node_obj.browse(int(node_id))

            node_val['x'] = getattr(node_rec, 'x', node_val['x'])
            node_val['y'] = getattr(node_rec, 'y', node_val['y'])

        return result
