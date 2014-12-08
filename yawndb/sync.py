"""
    yawndb.sync
    ~~~~~~~~~~~

    Sync YAWNDB transport. Use standart socket object methods.
"""

import time
import json
import socket
import urllib2
import logging
from collections import deque

from yawndb._base import _YAWNDBBase


_logger = logging.getLogger(__name__)


class YAWNDB(_YAWNDBBase):
    """Sync YAWNDB transport.
    Store not sent data in cache. Try to resend it on the next
    :py:meth:`.send_msgs` call or you can do it manually via
    :py:meth:`.send_cached` method.
    Try to reconnect if connection has lost on each :py:meth:`.send`
    and :py:meth:`.send_msgs` call.
    """

    def __init__(self, host, tcp_port=2011, json_port=8081, cache_size=100000):
        super(YAWNDB, self).__init__(host, tcp_port, json_port)
        self._socket = None
        self._disconnected = 0
        self._data_cache = deque([], cache_size)

    def slice(self, path, rule, from_t, to_t):
        url = 'http://{0}:{1}/paths/{2}/{3}/slice?from={4}&to={5}'.format(
            self._host, self._json_port, path, rule, from_t, to_t)
        return self._request(url)

    def last(self, path, rule, n):
        url = 'http://{0}:{1}/paths/{2}/{3}/last?n={4}'.format(
            self._host, self._json_port, path, rule, n)
        return self._request(url)

    def _request(self, url):
        try:
            res = urllib2.urlopen(url).read()
        except Exception:
            _logger.exception('JSON API IO error on %s', url)
            return []
        else:
            res = json.loads(res)
            if res['status'] != 'ok':
                _logger.error('JSON API error on %s: %s', url, res)
                return []
            if res['answer'] == 'empty':
                return []
            return res['answer']

    def start(self):
        try:
            self._socket = socket.socket()
            self._socket.settimeout(2)
            self._socket.connect((self._host, self._tcp_port))
        except IOError:
            _logger.error(
                'Couldn\'t to connect to YAWNDB at %s:%s',
                self._host, self._tcp_port)
            self.stop()

    def stop(self):
        if self._socket:
            try:
                self._socket.close()
            except IOError:
                pass
            self._disconnected = time.time()
        self._socket = None

    def _send(self, data):
        if not self._socket:
            return False
        try:
            self._socket.sendall(data)
            return True
        except IOError:
            _logger.error(
                'Couldn\'t send data to YAWNDB at %s:%s',
                self._host, self._tcp_port)
            self.stop()
            self._socket = None
            return False

    def send(self, data):
        if not self._send(data):
            self._data_cache.append(data)

    def send_msgs(self, msgs):
        super(YAWNDB, self).send_msgs(msgs)
        self.send_cached()

    def send_cached(self):
        """Try to re-send data that was failed to sent."""
        if not self._socket and time.time() - self._disconnected > 10:
            self.start()

        while True:
            if not self._socket:
                break
            try:
                data = self._data_cache.popleft()
            except IndexError:
                break
            if not self._send(data):
                self._data_cache.appendleft(data)
