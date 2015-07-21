# -*- coding: utf-8 -*-

import logging
import openerp
import psycopg2
import sys
import threading

from openerp import models
from openerp.http import request
from openerp.http import to_jsonable
from openerp.http import JsonRequest, HttpRequest

from openerp.tools import config
from openerp.tools.translate import _
from openerp.tools import ustr

from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven.utils.compat import _urlparse
from raven.utils.wsgi import get_headers, get_environ

from werkzeug.exceptions import ClientDisconnected


logger = logging.getLogger(__name__)

class ContextSentryHandler(SentryHandler):

    '''
        extends SentryHandler, to capture logs only if
        `sentry_enable_logging` config options set to true
    '''

    def __init__(self, client, db_name, **kwargs):
        self.db_name = db_name
        super(ContextSentryHandler, self).__init__(client, **kwargs)

    def get_user_info(self):

        from openerp.http import request

        cxt = {}
        if not request:
            return cxt

        user = request.env.user
        user_info = {}

        if user:
            user_info['is_authenticated'] = True
            user_info['id'] = user.id
            try:
                user_info['login']= user.login
            except:
                # TODO. bad cursor
                pass
            """
            if 'SENTRY_USER_ATTRS' in current_app.config:
                for attr in current_app.config['SENTRY_USER_ATTRS']:
                    if hasattr(current_user, attr):
                        user_info[attr] = getattr(current_user, attr)
            """
        else:
            user_info['is_authenticated'] = False

        return user_info

    def get_http_info(self):
        """
        Determine how to retrieve actual data by using request.mimetype.
        """
        from openerp.http import request

        cxt = {}
        if not request:
            return cxt

        if isinstance(request, JsonRequest):
            retriever = self.get_json_data
        else:
            retriever = self.get_form_data
        request = request.httprequest
        return self.get_http_info_with_retriever(request, retriever)

    def get_form_data(self, request):
        return request.form

    def get_json_data(self, request):
        return request.data

    def get_http_info_with_retriever(self, request, retriever=None):
        """
        Exact method for getting http_info but with form data work around.
        """
        if retriever is None:
            retriever = self.get_form_data

        urlparts = _urlparse.urlsplit(request.url)

        try:
            data = retriever(request)
        except ClientDisconnected:
            data = {}

        return {
            'url': '%s://%s%s' % (urlparts.scheme, urlparts.netloc, urlparts.path),
            'query_string': urlparts.query,
            'method': request.method,
            'data': data,
            'headers': dict(get_headers(request.environ)),
            'env': dict(get_environ(request.environ)),
        }

    def get_db_name(self):

        from openerp.http import request

        if request:
            session = getattr(request, 'session', {})
            db = session.get('db', None)
        else:
            db = openerp.tools.config['db_name']
            # If the database name is not provided on the command-line,
            # use the one on the thread (which means if it is provided on
            # the command-line, this will break when installing another
            # database from XML-RPC).
            if not db and hasattr(threading.current_thread(), 'dbname'):
                return threading.current_thread().dbname
        return db

    def get_extra_info(self):

        from openerp.http import request

        '''
            get extra context, if possible
        '''
        context = {
            "db": self.get_db_name()
        }

        if request:
            session = getattr(request, 'session', {})
            context['session_context'] = session.get('context', {})
            user = request.env.user
            if user:
                context['access_groups'] = dict((str(group.id), group.name) for group in user.groups_id)

        return context

    def emit(self, rec):
        if self.db_name != rec.dbname:
            return
        self.client.user_context(self.get_user_info())
        self.client.http_context(self.get_http_info())
        self.client.extra_context(self.get_extra_info())

        super(ContextSentryHandler, self).emit(rec)


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
                cr.close()
                if e.pgcode == '42P01':
                    # Class 42 — Syntax Error or Access Rule Violation; 42P01: undefined_table
                    # The table ir_config_parameter does not exist; this is probably not an OpenERP database.
                    _logger.warning('Tried to poll an undefined table on database %s.', db_name)
                    continue

            finally:
                cr.close()

            if not res:
                continue

            SENTRY_CLIENT_DSN = res[0][1]

            if not SENTRY_CLIENT_DSN:
                continue

            processors = (
                'raven.processors.SanitizePasswordsProcessor',
                'raven_sanitize_openerp.OpenerpPasswordsProcessor'
            )
            client = Client(
                dsn=SENTRY_CLIENT_DSN,
                processors=processors,
                auto_log_stacks=True,
                include_paths=['openerp',]
            )
            handler = ContextSentryHandler(
                client,
                db_name=db_name,
                level=getattr(logging, config.get('sentry_level', 'WARN')),
            )
            setup_logging(handler)

        super(SentrySetup, self).__init__(pool, cr, *args, **kwargs)
