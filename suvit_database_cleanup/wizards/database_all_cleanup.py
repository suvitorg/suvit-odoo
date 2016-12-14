# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CleanupPurgeWizardModule(models.TransientModel):
    _name = 'cleanup.purge.wizard.all'
    _cleanup_wizard_list = [
        'cleanup.purge.wizard.module',
        'cleanup.purge.wizard.model',
        'cleanup.purge.wizard.field',
        'cleanup.purge.wizard.table',
        'cleanup.purge.wizard.column',
    ]

    @api.model
    def cleanup_database_all(self):
        for wizard in self._cleanup_wizard_list:
            try:
                self.env[wizard].create({}).purge_all()
            except api.Warning:
                continue
