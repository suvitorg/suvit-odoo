# -*- coding: utf-8 -*-
import logging
import psycopg2
import threading

from openerp import api, exceptions, models, SUPERUSER_ID
from openerp.http import request
from openerp.tools import config

from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
try:
    from raven.utils.compat import urlparse as _urlparse
except ImportError:
    from raven.utils.compat import _urlparse
from raven.utils.wsgi import get_headers, get_environ

from werkzeug.exceptions import ClientDisconnected

logger = logging.getLogger(__name__)

db2max_time = {}


def patch_json_request_dispatch():
    from odoo.http import JsonRequest

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
            db = config['db_name']
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
        bad_logger = record.name.startswith(('odoo.sql_db',))
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


class Model(models.Model):
    """This is sentry logging setup or as it known -
    module raven implementation for Odoo.
    """
    _inherit = 'ir.model'

    def _register_hook(self):
        res =  super(Model, self)._register_hook()

        Param = self.env['ir.config_parameter']
        dsn = Param.get_param('SENTRY_CLIENT_DSN')
        if not dsn:
            return res

        processors = (
            'raven.processors.SanitizePasswordsProcessor',
            'raven_sanitize_openerp.OpenerpPasswordsProcessor'
        )
        client = Client(
            dsn=dsn,
            processors=processors,
            auto_log_stacks=True,
            include_paths=['odoo',]
        )
        handler = ContextSentryHandler(
            client,
            db_name=self._cr.dbname,
            level=getattr(logging, config.get('sentry_level', 'ERROR')),
        )
        setup_logging(handler)

        try:
            max_response_time = int(Param.get_param('SENTRY_CLIENT_MAX_RESPONSE_TIME'))
        except ValueError:
            return res

        if not max_response_time:
            return res

        db2max_time[self._cr.dbname] = max_response_time

        logger.info('Patching JsonRequest.dispatch: %s', db2max_time)
        patch_json_request_dispatch()

        return res


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_param_sentry_client_js_dsn(self):
        return self.sudo().get_param('SENTRY_CLIENT_JS_DSN', False)
