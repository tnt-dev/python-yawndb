import time

from mock import Mock

from yawndb.sync import YAWNDB


class SocketMock(Mock):
    """Socket object emulator."""

    def __init__(self, *args, **kwargs):
        super(SocketMock, self).__init__(*args, **kwargs)
        self._data = []
        self.enable()

    def sendall(self, data):
        if self._enabled:
            self._data.append(data)
        else:
            raise IOError

    @property
    def data(self):
        return list(self._data)

    def clear(self):
        self._data = []

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False


class TestYAWNDBSync(object):
    """Test sync YAWNDB transport."""

    @classmethod
    def setup_class(cls):
        cls.yawndb = YAWNDB('127.0.0.1')
        cls.socket = SocketMock()
        cls.yawndb._socket = cls.socket

    def test_send(self):
        self.yawndb.send('test123')
        assert self.socket.data == ['test123']
        self.yawndb.send('some new data')
        assert self.socket.data == ['test123', 'some new data']

    def test_send_msgs(self):
        self.socket.clear()
        enc1 = self.yawndb.encode_msg('1-2-3', 100500, False, time.time())
        self.yawndb.send_msgs([('1-2-3', 100500)])
        assert self.socket.data == [enc1]

        self.socket.clear()
        self.yawndb.send_msgs([])
        assert self.socket.data == []

        self.socket.clear()
        enc2 = (
            self.yawndb.encode_msg('3-4-5', 0, False, time.time()) +
            self.yawndb.encode_msg('aaaaa', 111111, True, time.time()))
        self.yawndb.send_msgs([('3-4-5', 0, False), ('aaaaa', 111111, True)])
        assert self.socket.data == [enc2]

    def test_send_cached(self):
        self.socket.clear()
        self.socket.disable()
        enc1 = self.yawndb.encode_msg('test-path', 1555, True, time.time())
        self.yawndb.send_msgs([('test-path', 1555, True)])
        assert self.socket.data == []

        self.yawndb.send_cached()
        assert self.socket.data == []

        enc2 = self.yawndb.encode_msg('ttest-path', 189, False, time.time())
        self.yawndb.send_msgs([('ttest-path', 189)])
        assert self.socket.data == []

        self.socket.enable()
        self.yawndb._socket = self.socket
        self.yawndb.send_cached()
        assert self.socket.data == [enc1, enc2]
