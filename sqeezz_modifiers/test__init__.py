# coding=utf-8
import unittest
from sqeezz_modifiers import *


class TestCallClass(unittest.TestCase):
    def test_call_class(self):
        def test_func(arg1, arg2):
            return arg1, arg2

        # Set default arguments, but override them when calling.
        test_call = Call(test_func, 1, arg2=2)
        test_data = test_call(3, 4)

        self.assertTupleEqual(test_data, (3, 4))

        # Call with no arguments, this would be your defaults for a function.
        test_data = test_call()

        self.assertTupleEqual(test_data, (1, 2))


class TestDataClass(unittest.TestCase):
    def test_error(self):
        self.fail()

    def test_exit(self):
        self.fail()


class TestFileClass(unittest.TestCase):
    def test_open(self):
        self.fail()


class TestStrictTypeDecorator(unittest.TestCase):
    def test_strict_type(self):
        self.fail()


if __name__ == '__main__':
    unittest.main()
