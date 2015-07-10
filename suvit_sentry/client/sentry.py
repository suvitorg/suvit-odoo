# -*- coding: utf-8 -*-


import logging

from raven.base import Client
from openerp.http import request

from openerp.modules.registry import RegistryManager
import openerp.tools.config as config


_logger = logging.getLogger(__name__)


class SentryClient(Client):

    def get_config(self):

        DB_NAME = config.get("database")

        registry = openerp.modules.registry.RegistryManager.get(DB_NAME)

        params = request.registry.get('ir.config_parameter')

        SENTRY_CLIENT_DSN = params.get_param(request.cr, openerp.SUPERUSER_ID, 'SENTRY_CLIENT_DSN')
        ENABLE_LOGGING = params.get_param(request.cr, openerp.SUPERUSER_ID, 'ENABLE_LOGGING')
        ALLOW_ORM_WARNING = params.get_param(request.cr, openerp.SUPERUSER_ID, 'ALLOW_ORM_WARNING')
        INCLUDE_USER_CONTEXT = params.get_param(request.cr, openerp.SUPERUSER_ID, 'INCLUDE_USER_CONTEXT')

        return {
            "SENTRY_CLIENT_DSN": SENTRY_CLIENT_DSN,
            "ENABLE_LOGGING": ENABLE_LOGGING,
            "ALLOW_ORM_WARNING": ALLOW_ORM_WARNING,
            "INCLUDE_USER_CONTEXT": INCLUDE_USER_CONTEXT
        }


