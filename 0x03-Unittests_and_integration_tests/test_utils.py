#!/usr/bin/env python3
"""Unit tests for utils module."""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Test access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test successful access of nested map."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that KeyError is raised for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Test get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json returns expected payload."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        # Patch requests.get in a PEP8-compliant way
        with patch(
            "utils.requests.get",
            return_value=mock_response
        ) as mock_get:
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test memoize decorator."""

    def test_memoize(self):
        """Test memoize caches method result."""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        obj = TestClass()

        with patch.object(
            TestClass,
            "a_method",
            return_value=42
        ) as mock_method:
            first = obj.a_property
            second = obj.a_property
            self.assertEqual(first, 42)
            self.assertEqual(second, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
