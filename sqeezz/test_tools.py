import unittest

from tools import FuncTools


class TestFuncToolsClass(unittest.TestCase):
    def test_remove_dup_args(self):
        def test_func(arg1, arg2):
            pass

        # Two arguments and a keyword argument,
        # should remove the keyword argument since it is redefining the first argument.
        args = (1, 2)
        kwargs = {'arg1': 3}

        FuncTools.remove_dup_kwargs(test_func, args, kwargs)

        self.assertEqual(args, (1, 2))
        self.assertDictEqual(kwargs, {})

        # One keyword argument and one keyword argument,
        # should not remove anything since they are defining two different arguments
        args = (1, )
        kwargs = {'arg2': 2}

        FuncTools.remove_dup_kwargs(test_func, args, kwargs)

        self.assertEqual(args, (1, ))
        self.assertDictEqual(kwargs, {'arg2': 2})

    def test_create_args_dict(self):
        def test_func(arg1, arg2):
            pass

        args = FuncTools.create_args_dict(test_func, (1, 2))

        self.assertDictEqual(args, {'arg1': 1, 'arg2': 2})


if __name__ == '__main__':
    unittest.main()