import unittest


class TestCaseMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('__abstract_test__', False)
        return super(TestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)

    def __dir__(cls):
        attrs = super(TestCaseMetaclass, cls).__dir__()
        if cls.__abstract_test__:
            attrs = [name for name in attrs if not name.startswith('test')]
        return attrs


class TestCase(unittest.TestCase, metaclass=TestCaseMetaclass):

    pass

