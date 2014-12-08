"""
    yawndb.twisted
    ~~~~~~~~~~~~~~

    Twisted YAWNDB transport. Interact with YAWNDB in asynchronous way.
"""

from __future__ import absolute_import

import logging

from twisted.internet import defer, reactor
from twisted.internet.protocol import ReconnectingClientFactory, Protocol

from yawndb._base import _YAWNDBBase


_logger = logging.getLogger(__name__)


class YAWNDB(_YAWNDBBase, ReconnectingClientFactory):
    """YAWNDB factory which implements asynchronous data sending
    to YAWNDB via TCP socket. Based on the Twisted's reconnect
    factory so it will automatically bring up connection if it fails.
    TODO: Implement JSON interface.
    """

    noisy = False

    def __init__(self, *args, **kwargs):
        _YAWNDBBase.__init__(self, *args, **kwargs)
        # This deferred used for indication is factory currently
        # connected to host or not.
        self._deferred = defer.Deferred()

    def buildProtocol(self, addr):
        _logger.info('Connected')
        self.resetDelay()
        self._protocol = YAWNDBTCPProtocol()
        self._deferred.callback(None)
        return self._protocol

    def clientConnectionFailed(self, connector, reason):
        _logger.error('Connection failed')
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        _logger.error('Connection lost')
        self._deferred = defer.Deferred()
        ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason)

    def start(self):
        reactor.connectTCP(self._host, self._tcp_port, self)

    def stop(self):
        self.stopTrying()
        if self._deferred.called:
            self._protocol.loseConnection()

    @defer.inlineCallbacks
    def send(self, data):
        """Asynchronously send encoded data.
        Return :py:class:`defer.Deferred`.
        """
        if not self._deferred.called:
            yield self._deferred
        yield self._protocol.wait_for_connection()
        self._protocol.send(data)

    def send_msgs(self, msgs):
        """Asynchronously send messages.
        Return :py:class:`defer.Deferred`.
        """
        return super(YAWNDB, self).send_msgs(msgs)


class YAWNDBTCPProtocol(Protocol):
    """Simple binary protocol."""

    def __init__(self):
        # This deferred used for indicatation is protocol's transport
        # currently connected to host or not.
        self._deferred = defer.Deferred()

    def connectionMade(self):
        self._deferred.callback(None)

    def connectionLost(self, reason):
        self._deferred = defer.Deferred()

    def wait_for_connection(self):
        return self._deferred

    def send(self, data):
        """Send encoded data."""
        self.transport.write(data)
