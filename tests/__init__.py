import os
import os.path as path


class WithFixtures(object):
    """Preload class fixtures (if any) on class initialization and
    check with special fixture tester function does the computed
    result equal precomputed output in fixture.
    Example of location:

    tests/
        test_serializers.py
        test_validators.py
        fixtures/
            XML2Config/        # <- class name (without Test prefix)
                config2dict.1  # <- will be stored in cls._fixtures as
                config2dict.2  # {'config2dict': {'1': (i, o), '2': (i, o)}}
            Config2XML/
                config2xml.1   # and so on...
                config2xml.2
                config2xml.3

    The example above will run
    :py:meth:`TestXML2Config.fixture_config2dict` with arguments
    '1', <input from fixture 1> and '2', <input from fixture 2> and
    compare the output of function and fixture output value.
    :py:meth:`TestConfig2XML.fixture_config2xml` will be run using
    the same schema.
    """

    _FIXTURE_SEPARATOR = '=================================================='

    @classmethod
    def setup_class(cls):
        cls._fixtures = {}

        base_dir = path.abspath(path.dirname(__file__))
        cls_dir = cls.__name__[4:]
        cls._fixtures_dir = path.join(base_dir, 'fixtures', cls_dir)
        try:
            filenames = os.listdir(cls._fixtures_dir)
        except OSError:
            return
        for filename in filenames:
            if filename.startswith('.'):
                continue
            fullname = path.join(cls._fixtures_dir, filename)
            func, key = filename.split('.')
            if func not in cls._fixtures:
                cls._fixtures[func] = {}
            input, output = open(fullname).read().split(
                cls._FIXTURE_SEPARATOR)
            cls._fixtures[func][key] = input.strip(), output.strip()

    def test_fixtures(self):
        for func in self._fixtures:
            tester_func = 'fixture_' + func
            if not hasattr(self, tester_func):
                continue
            tester = getattr(self, tester_func)
            for key, (input, output) in self._fixtures[func].iteritems():
                result = tester(key, input)
                assert result == output, self._fixture_error(func, key, result)

    def _fixture_error(self, func, key, result):
        return (
            'Input not equals output in `{0}/{1}.{2}\'! '
            'Output must be:\n\n{3}'.format(
                self._fixtures_dir, func, key, result))
