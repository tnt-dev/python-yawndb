from yawndb._base import _YAWNDBBase
from tests import WithFixtures


class TestYAWNDBBase(WithFixtures):
    """Test base YAWNDB class."""

    _FIXTURE_TIMESTAMP = 1349695853

    @classmethod
    def setup_class(cls):
        super(TestYAWNDBBase, cls).setup_class()
        cls.yawndb = _YAWNDBBase('127.0.0.1')

    def test_init(self):
        yawndb = _YAWNDBBase('127.0.0.1', tcp_port=12345, json_port=8913)

    def fixture_encode_msg(self, key, input):
        """Got executed by :py:meth:`.test_fixtures`."""
        def is_special(value):
            """Return predifined is_special param for each value in
            tests.
            """
            if key == '1':
                return False
            elif key == '2':
                return bool(value % 2)
            else:
                raise NotImplementedError

        input = eval(input)
        result = [self.yawndb.encode_msg(path, value, is_special(value),
                                         self._FIXTURE_TIMESTAMP)
                  for path, value in input]
        return ''.join(result)
