import glob
import json
import logging
import os
import select
import subprocess
import time
import threading
import errno
from datetime import datetime, timedelta

import openerp

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='myapp.log',
                    filemode='w'
                    )

_logger = logging.getLogger(__name__)

PORT = 8068
get_db_name = lambda: '8-format-rt'


class PhantomCase(object):

    def __init__(self):
        self.session = openerp.http.root.session_store.new()
        self.session_id = self.session.sid
        self.session.db = get_db_name()

    def phantom_poll(self, phantom, timeout):
        """ Phantomjs Test protocol.

        Use console.log in phantomjs to output test results:

        - for a success: console.log("ok")
        - for an error:  console.log("error")

        Other lines are relayed to the test log.

        """
        t0 = datetime.now()
        td = timedelta(seconds=timeout)
        buf = bytearray()
        while True:
            # timeout
            if datetime.now() - t0 > td:
                raise Exception("PhantomJS tests should take less than %s seconds" % timeout)

            # read a byte
            try:
                ready, _, _ = select.select([phantom.stdout], [], [], 0.5)
            except select.error, e:
                # In Python 2, select.error has no relation to IOError or
                # OSError, and no errno/strerror/filename, only a pair of
                # unnamed arguments (matching errno and strerror)
                err, _ = e.args
                if err == errno.EINTR:
                    continue
                if err == 10038 and os.name == 'nt':
                    ready = 1
                else:
                    raise

            if ready:
                s = phantom.stdout.read(1)
                #_logger.debug('--- %s' % s)
                if not s:
                    break
                buf.append(s)

            # process lines
            if os.linesep in buf:
                line, buf = buf.split(os.linesep, 1)
                line = str(line).strip()

                # relay everything from console.log, even 'ok' or 'error...' lines
                _logger.info("phantomjs: %s", line)

                print `line`
                if line == "ok":
                    break
                if line.startswith("error"):
                    line_ = line[6:]
                    # when error occurs the execution stack may be sent as as JSON
                    try:
                        line_ = json.loads(line_)
                    except ValueError: 
                        pass
                    self.fail(line_ or "phantomjs test failed")

    def phantom_run(self, cmd, timeout):
        _logger.info('phantom_run executing %s', ' '.join(cmd))

        ls_glob = os.path.expanduser('~/.qws/share/data/Ofi Labs/PhantomJS/http_localhost_%s.*'%PORT)
        for i in glob.glob(ls_glob):
            _logger.info('phantomjs unlink localstorage %s', i)
            os.unlink(i)
        try:
            phantom = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
        except OSError:
            raise unittest2.SkipTest("PhantomJS not found")
        try:
            self.phantom_poll(phantom, timeout)
        finally:
            # kill phantomjs if phantom.exit() wasn't called in the test
            if phantom.poll() is None:
                phantom.terminate()
                phantom.wait()
            self._wait_remaining_requests()
            _logger.info("phantom_run execution finished")

    def _wait_remaining_requests(self):
        t0 = int(time.time())
        for thread in threading.enumerate():
            if thread.name.startswith('openerp.service.http.request.'):
                while thread.isAlive():
                    # Need a busyloop here as thread.join() masks signals
                    # and would prevent the forced shutdown.
                    thread.join(0.05)
                    time.sleep(0.05)
                    t1 = int(time.time())
                    if t0 != t1:
                        _logger.info('remaining requests')
                        openerp.tools.misc.dumpstacks(tid=thread.ident)
                        t0 = t1

    def phantom_jsfile(self, jsfile, timeout=60, **kw):
        options = {
            'timeout' : timeout,
            'port': PORT,
            'db': get_db_name(),
            'session_id': self.session_id,
        }
        options.update(kw)
        phantomtest = os.path.join(os.path.dirname(__file__), 'phantomtest.js')
        # phantom.args[0] == phantomtest path
        # phantom.args[1] == options
        cmd = [
            'phantomjs',
            jsfile, phantomtest, json.dumps(options)
        ]
        self.phantom_run(cmd, timeout)

    def phantom_js(self, url_path, code, ready="window", login=None, timeout=60, **kw):
        """ Test js code running in the browser
        - optionnally log as 'login'
        - load page given by url_path
        - wait for ready object to be available
        - eval(code) inside the page

        To signal success test do:
        console.log('ok')

        To signal failure do:
        console.log('error')

        If neither are done before timeout test fails.
        """
        options = {
            'port': PORT,
            'db': get_db_name(),
            'url_path': url_path,
            'code': code,
            'ready': ready,
            'timeout' : timeout,
            'login' : login,
            'session_id': self.session_id,
        }
        options.update(kw)
        options.setdefault('password', options.get('login'))
        phantomtest = os.path.join(os.path.dirname(__file__), 'phantomtest.js')
        cmd = ['phantomjs', phantomtest, json.dumps(options)]
        self.phantom_run(cmd, timeout)


    def test_phantom(self):
        self.phantom_js("/", "console.log('ok');", 'openerp', login='admin')


if __name__ == '__main__':
    PhantomCase().test_phantom()
