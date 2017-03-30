# coding=utf-8
import unittest
from utils import FuncUtils


class TestFuncUtilsClass(unittest.TestCase):
    def test_remove_invalid_kwargs(self):
        def test_func(arg1, arg2):
            pass

        # Two arguments and a keyword argument, should remove the keyword
        # argument since it is redefining the first argument.
        args = (1, 2)
        kwargs = {'arg1': 3}

        FuncUtils.remove_invalid_kwargs(test_func, args, kwargs)

        self.assertTupleEqual(args, (1, 2))
        self.assertDictEqual(kwargs, {})

        # One keyword argument and one keyword argument, should not remove
        # anything since they are defining two different arguments.
        args = (1, )
        kwargs = {'arg2': 2}

        FuncUtils.remove_invalid_kwargs(test_func, args, kwargs)

        self.assertTupleEqual(args, (1, ))
        self.assertDictEqual(kwargs, {'arg2': 2})

    def test_create_args_dict(self):
        def test_func(arg1, arg2):
            pass

        mapped_args = FuncUtils.create_args_dict(test_func, (1, 2))

        self.assertDictEqual(mapped_args, {'arg1': 1, 'arg2': 2})


if __name__ == '__main__':
    unittest.main()
