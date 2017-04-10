# -*- coding: utf-8 -*-
import logging
import openerp
import psycopg2
import threading

from openerp import SUPERUSER_ID, models, exceptions
from openerp.http import request

from openerp.tools import config

from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven.utils.compat import _urlparse
from raven.utils.wsgi import get_headers, get_environ

from werkzeug.exceptions import ClientDisconnected

logger = logging.getLogger(__name__)

db2max_time = {}


def patch_json_request_dispatch():
    from openerp.http import JsonRequest

    if getattr(JsonRequest.dispatch, 'source', None):
        return

    import time

    def new_dispatch(self):
        MAX_RESPONSE_TIME = db2max_time.get(self.db, 0)
        if MAX_RESPONSE_TIME == 0:
            return new_dispatch.source(self)

        start_time = time.time()
        try:
            return new_dispatch.source(self)
        finally:
            work_time = time.time() - start_time

            if work_time > MAX_RESPONSE_TIME:

                endpoint = self.endpoint.method.__name__
                model = self.params.get('model')
                method = self.params.get('method')

                if endpoint not in ['poll',  # do not log longpolling/poll
                                    ]:

                    msg_preffix = '%s/%s.%s' % (endpoint, model, method)
                    # we use error for notify sentry
                    logger.error(msg_preffix + u': Slow response time %.2f',
                                 work_time)

    new_dispatch.source = JsonRequest.dispatch
    JsonRequest.dispatch = new_dispatch


class ContextSentryHandler(SentryHandler):

    '''
        extends SentryHandler, to capture logs only if
        `sentry_enable_logging` config options set to true
    '''

    def __init__(self, client, db_name, **kwargs):
        self.db_name = db_name
        super(ContextSentryHandler, self).__init__(client, **kwargs)

    def get_user(self, request):
        try:
            user = request.env.user
            user.login
        except psycopg2.IntegrityError:
            # transaction aborted
            # rollbacked and try again
            request.cr.rollback()
            user = request.registry['res.users'].browse(request.cr, SUPERUSER_ID, request.uid)

        return user

    def get_user_info(self):
        global request

        cxt = {}
        if not request:
            return cxt

        user_info = {}
        user_info['id'] = request.uid

        if request.uid:
            user_info['is_authenticated'] = True

            user = self.get_user(request)
            user_info['login'] = user.login
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
        global request

        cxt = {}
        if not request:
            return cxt

        if request._request_type == 'json':
            retriever = self.get_json_data
        else:
            retriever = self.get_form_data
        return self.get_http_info_with_retriever(request, retriever)

    def get_form_data(self, request):
        return request.httprequest.form

    def get_json_data(self, request):
        return getattr(request, 'jsonrequest', None) or request.httprequest.data

    def get_http_info_with_retriever(self, odoo_request, retriever=None):
        """
        Exact method for getting http_info but with form data work around.
        """
        request = odoo_request.httprequest
        if retriever is None:
            retriever = self.get_form_data

        urlparts = _urlparse.urlsplit(request.url)

        try:
            data = retriever(odoo_request)
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
        global request

        if request:
            db = request.db
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
        '''
            get extra context, if possible
        '''
        global request

        context = {
            "db": self.get_db_name()
        }

        if request:
            context['session_context'] = request.context

            user = self.get_user(request)
            if user:
                groups = dict((str(group.id), group.name) for group in user.groups_id)
                context['access_groups'] = groups
        return context

    def can_record(self, record):
        res = super(ContextSentryHandler, self).can_record(record)
        if not res:
            return res
        bad_db = self.db_name != record.dbname
        bad_logger = record.name.startswith(('openerp.sql_db',))
        if record.exc_info and all(record.exc_info):
            bad_exc = issubclass(record.exc_info[0], (exceptions.ValidationError,
                                                      exceptions.Warning,
                                                      exceptions.RedirectWarning,
                                                      exceptions.except_orm)
                                )

            if issubclass(record.exc_info[0], (exceptions.AccessDenied,
                                               exceptions.AccessError)):
                # we need to watch access errors
                bad_exc = False

        else:
            bad_exc = False
        return not (bad_db or bad_logger or bad_exc)

    def _emit(self, rec, **kwargs):
        # must be _emit, after can_record
        self.client.user_context(self.get_user_info())
        self.client.http_context(self.get_http_info())
        self.client.extra_context(self.get_extra_info())
        super(ContextSentryHandler, self)._emit(rec, **kwargs)


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
                select = "select key, value from ir_config_parameter where key = 'SENTRY_CLIENT_MAX_RESPONSE_TIME'"
                cr.execute(select)
                res2 = cr.fetchall()
            except psycopg2.ProgrammingError, e:
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
                level=getattr(logging, config.get('sentry_level', 'ERROR')),
            )
            setup_logging(handler)

            if not res2:
                continue
            try:
                MAX_RESPONSE_TIME = int(res2[0][1])
            except:
                continue

            if not MAX_RESPONSE_TIME:
                continue

            db2max_time[db_name] = MAX_RESPONSE_TIME

        if db2max_time:
            print 'Patching JsonRequest.dispatch', db2max_time
            patch_json_request_dispatch()

        super(SentrySetup, self).__init__(pool, cr, *args, **kwargs)
