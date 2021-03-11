import unittest
from multimethod import multimethod

class MultiMethodTestCase(unittest.TestCase):
    def test_multi_method_for_global_func(self):

        @multimethod
        def a(a:int):
            return 'int'
        @multimethod
        def a(s:str):
            return 'str'

        self.assertEqual(a(1), 'int')
        self.assertEqual(a('s'), 'str')

        pass

    def test_class_method_for_class_member(self):
        class TestClass:
            @multimethod
            def a(self, a:int):
                return 'int'
            @multimethod
            def a(self, s:str):
                return 'str'
        tc=TestClass();

        self.assertEqual(tc.a(1), 'int')
        self.assertEqual(tc.a('s'), 'str')
        pass

    pass