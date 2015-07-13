# -*- coding: utf-8 -*-

import logging
import openerp
import psycopg2
import sys

from openerp import models
from openerp.http import request
from openerp.http import to_jsonable
from openerp.tools import config
from openerp.tools.translate import _
from openerp.tools import ustr

from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

logger = logging.getLogger(__name__)


def get_user_context():
    '''
        get the current user context, if possible
    '''
    cxt = {}
    if not request:
        return cxt
    session = getattr(request, 'session', {})
    cxt.update({
        'session': {
            'context': session.get('context', {}),
            'db': session.get('db', None),
            'login': session.get('login', None),
            'password': session.get('uid', None),
        },
    })
    return cxt


class ContextSentryHandler(SentryHandler):

    '''
        extends SentryHandler, to capture logs only if
        `sentry_enable_logging` config options set to true
    '''

    def __init__(self, client, db_name, **kwargs):
        self._client = client
        self.db_name = db_name
        super(ContextSentryHandler, self).__init__(**kwargs)


    def emit(self, rec):
        if self.db_name != rec.dbname:
            return
        self._client.extra_context(get_user_context())
        self._client.captureException(rec.exc_info)


class SentrySetup(models.AbstractModel):
    """This is sentry logging setup or as it known -
    module raven implementation for OpenERP.
    """
    _name = 'sentry.setup'

    def __init__(self, pool, cr, *args, **kwargs):

        registries = openerp.modules.registry.RegistryManager.registries

        params = pool['ir.config_parameter']
        for db_name, _ in registries.iteritems():
            db = openerp.sql_db.db_connect(db_name)
            cr = db.cursor()
            res = []
            try:
                select = "select key, value from ir_config_parameter where key = 'SENTRY_CLIENT_DSN'"
                cr.execute(select)
                res = cr.fetchall()
            except psycopg2.ProgrammingError, e:
                if e.pgcode == '42P01':
                    # Class 42 — Syntax Error or Access Rule Violation; 42P01: undefined_table
                    # The table ir_config_parameter does not exist; this is probably not an OpenERP database.
                    _logger.warning('Tried to poll an undefined table on database %s.', db_name)
                    continue
                else:
                    raise

            if not res:
                continue

            SENTRY_CLIENT_DSN = res[0][1]

            processors = (
                'raven.processors.SanitizePasswordsProcessor',
                'raven_sanitize_openerp.OpenerpPasswordsProcessor'
            )
            client = Client(
                dsn=SENTRY_CLIENT_DSN,
                processors=processors,
            )
            handler = ContextSentryHandler(
                client,
                db_name=db_name,
                level=getattr(logging, config.get('sentry_level', 'WARN')),
            )
            setup_logging(handler)

        super(SentrySetup, self).__init__(pool, cr, *args, **kwargs)


def serialize_exception(e):

    tmp = {}

    if isinstance(e, openerp.osv.osv.except_osv):
        tmp["exception_type"] = "except_osv"
    elif isinstance(e, openerp.exceptions.Warning):
        tmp["exception_type"] = "warning"
    elif isinstance(e, openerp.exceptions.AccessError):
        tmp["exception_type"] = "access_error"
    elif isinstance(e, openerp.exceptions.AccessDenied):
        tmp["exception_type"] = "access_denied"

    t = sys.exc_info()

    if "exception_type" not in tmp:
        debug = u"Ошибка отправлена разработчикам, они занимаются устранением проблемы"
    else:
        debug = t

    tmp.update({
        "name": type(e).__module__ + "." + type(e).__name__ if type(e).__module__ else type(e).__name__,
        "debug": debug,
        "message": ustr(e),
        "arguments": to_jsonable(e.args),
    })

    return tmp

openerp.http.serialize_exception = serialize_exception
