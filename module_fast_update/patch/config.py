# -*- coding: utf-8 -*-
import logging

from odoo import api, _
from odoo.tools import config
from odoo.addons.base.module.module import Module, ACTION_DICT, assert_log_admin_access
from odoo.modules.graph import Node


def add_child(self, name, info):
    node = Node(name, self.graph, info)
    node.depth = self.depth + 1
    if node not in self.children:
        self.children.append(node)
    for attr in ('init', 'update', 'demo'):
        if attr == 'update' and self.name in config.options.get('update_fast_module_run', []):
            continue
        if hasattr(self, attr):
            setattr(node, attr, True)
    self.children.sort(key=lambda x: x.name)
    return node

Node.add_child = add_child


def format_parse_config():
    config.options.setdefault('update_fast', [])
    for k, v in config.options['update'].items():
        if k.endswith(':fast'):
            del config.options['update'][k]
            new_k = k.split(':')[0]
            config.options['update'][new_k] = v
            if v:
                config.options['update_fast'].append(new_k)

format_parse_config()

@assert_log_admin_access
@api.multi
def format_button_upgrade(self):
    fast = []
    orig = []
    config.options['update_fast_module_run'] = []
    for module in self:
        if module.name in config['update_fast']:
            # remove module from config update_fast to use fast update just once when server started
            config.options['update_fast'].remove(module.name)
            config.options['update_fast_module_run'].append(module.name)
            fast.append(module.id)
        else:
            orig.append(module.id)
    if fast:
        button_upgrade_fast(self.browse(fast))
    if orig:
        orig_button_upgrade(self.browse(orig))
    return dict(ACTION_DICT, name=_('Apply Schedule Upgrade'))

@api.multi
def button_upgrade_fast(self):
    self.update_list()
    self.write({'state': 'to upgrade'})
    return dict(ACTION_DICT, name=_('Apply Schedule Upgrade'))

orig_button_upgrade = Module.button_upgrade

Module.button_upgrade = format_button_upgrade
