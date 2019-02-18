# -*- coding: utf-8 -*-
import logging

from odoo import api, _
from odoo.tools import config
from odoo.addons.base.module.module import Module, ACTION_DICT


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


@api.multi
def format_button_upgrade(self):
    if self.name in config['update_fast']:
        # remove module from config update_fast to use fast update just once when server started
        config.options['update_fast'].remove(self.name)
        return button_upgrade_fast(self)
    return orig_button_upgrade(self)

@api.multi
def button_upgrade_fast(self):
    self.update_list()
    self.write({'state': 'to upgrade'})
    return dict(ACTION_DICT, name=_('Apply Schedule Upgrade'))

orig_button_upgrade = Module.button_upgrade

Module.button_upgrade = format_button_upgrade
