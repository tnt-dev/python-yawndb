"""
    yawndb._base
    ~~~~~~~~~~~~

    Base YAWNDB class interface.
"""

import time
import struct


class _YAWNDBBase(object):
    """Base YAWNDB class interface which should be implemented
    in subclasses.
    """

    #: Protocol version.
    VERSION = 3

    def __init__(self, host, tcp_port=2011, json_port=8081):
        self._host = host
        self._tcp_port = tcp_port
        self._json_port = json_port

    def start(self):
        """Start TCP interface.
        Not neccessary if only get requests used.
        """
        raise NotImplementedError

    def stop(self):
        """Stop TCP interface."""
        raise NotImplementedError

    def slice(self, path, rule, from_t, to_t):
        """Do slice request to YAWNDB via HTTP JSON API.
        Return list of data from answer part of response or empty list
        on error.
        """
        raise NotImplementedError

    def last(self, path, rule, n):
        """Do last request to YAWNDB via HTTP JSON API.
        Return list of data from answer part of response or empty list
        on error.
        """
        raise NotImplementedError

    @classmethod
    def encode_msg(cls, path, value, is_special, timestamp):
        """Convert message to the internal YAWNDB format for sending
        it via TCP socket.
        """
        is_special_int = 1 if is_special else 0
        pck_tail = struct.pack(
            '>BBQQ', cls.VERSION, is_special_int, timestamp, value)
        pck_tail += path
        pck_head = struct.pack('>H', len(pck_tail))
        pck = pck_head + pck_tail
        return pck

    def send(self, data):
        """Send already encoded with :py:meth:`.encode_msg` data."""
        raise NotImplementedError

    def send_msgs(self, msgs):
        """Send list of messages to YAWNDB via TCP. Message format:

        (path, value)         # Common path/value pair
        or
        (path, value, True)   # Special value
        or
        (path, value, False)  # Common path/value pair

        Note that timestamp for each message will be generated
        automatically (current time). If it is not a case for you,
        you should encode and send messages by yourself via
        :py:meth:`.encode_msg` and :py:meth:`.send`.
        """
        if not msgs:
            return
        packets = []
        for msg in msgs:
            path, value = msg[:2]
            if len(msg) == 3:
                is_special = msg[2]
            else:
                is_special = False
            timestamp = int(time.time())
            packet = self.encode_msg(path, value, is_special, timestamp)
            packets.append(packet)
        data = ''.join(packets)
        return self.send(data)
