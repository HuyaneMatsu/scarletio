import vampytest

from ..field_factories import proxy_method_factory
from ..proxy_base import ProxyBase


def test__proxy_method_factory__method_call():
    """
    Tests whether `proxy_method_factory` method call works as intended.
    """
    class TestedType:
        def do_things(self, value):
            return value * 2
    
    class TestType(ProxyBase):
        do_things = proxy_method_factory('do_things')
    
    
    value = TestedType()
    instance = TestType(value)
    passed_value = 7
    expected_output = 14
    
    vampytest.assert_eq(instance.do_things(passed_value), expected_output)


def test__proxy_method_factory__function_call():
    """
    Tests whether `proxy_method_factory` function call works as intended.
    """
    class TestedType:
        def do_things(self, value):
            return value * 2
    
    class TestType(ProxyBase):
        do_things = proxy_method_factory('do_things')
    
    
    value = TestedType()
    instance = TestType(value)
    passed_value = 7
    expected_output = 14
    
    vampytest.assert_eq(TestType.do_things(instance, passed_value), expected_output)
