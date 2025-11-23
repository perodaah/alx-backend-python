#!/usr/bin/env python3
"""
This module contains unit tests for the client module.
"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient

# Import fixtures
try:
    from fixtures import TEST_PAYLOAD
except ImportError:
    # Fallback if fixtures.py doesn't exist
    TEST_PAYLOAD = []


class TestGithubOrgClient(unittest.TestCase):
    """
    Test class for GithubOrgClient class.

    Contains test cases to verify correct behavior of the
    GithubOrgClient methods.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str,
                 mock_get_json: unittest.mock.Mock) -> None:
        """
        Test that GithubOrgClient.org returns the correct value.

        Args:
            org_name (str): The organization name to test
            mock_get_json (Mock): The mocked get_json function
        """
        # Set up the mock return value
        test_payload = {"login": org_name, "id": 123456}
        mock_get_json.return_value = test_payload

        # Create GithubOrgClient instance
        client = GithubOrgClient(org_name)

        # Call the org property (memoized - accessed as attribute, not method)
        result = client.org

        # Assert that get_json was called once with correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert that the result matches the test payload
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected value.

        Mocks the org property to return a known payload and verifies
        that _public_repos_url extracts the correct repos_url.
        """
        # Known payload to use for mocking
        test_payload = {
            "login": "test_org",
            "id": 123456,
            "repos_url": "https://api.github.com/orgs/test_org/repos"
        }

        # Patch the org property to return our test payload
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock,
                   return_value=test_payload):
            # Create GithubOrgClient instance
            client = GithubOrgClient("test_org")

            # Call the _public_repos_url property
            result = client._public_repos_url

            # Assert that the result matches the expected repos_url
            expected_url = "https://api.github.com/orgs/test_org/repos"
            self.assertEqual(result, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: unittest.mock.Mock) -> None:
        """
        Test that public_repos returns the expected list of repositories.

        Mocks get_json and _public_repos_url to test the public_repos method.
        """
        # Test payload for get_json mock
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = test_repos_payload

        # Expected list of repository names
        expected_repos = ["repo1", "repo2", "repo3"]

        # Mock _public_repos_url to return a test URL and track calls
        test_repos_url = "https://api.github.com/orgs/test_org/repos"
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value=test_repos_url) as mock_public_repos_url:
            # Create GithubOrgClient instance
            client = GithubOrgClient("test_org")

            # Call public_repos method
            result = client.public_repos()

            # Assert that the result matches expected repository names
            self.assertEqual(result, expected_repos)

            # Assert that _public_repos_url was accessed once
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the test repos URL
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str,
                         expected: bool) -> None:
        """
        Test that has_license returns the expected boolean value.

        Args:
            repo (dict): The repository dictionary to test
            license_key (str): The license key to check for
            expected (bool): The expected return value
        """
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)

        # Assert that the result matches the expected value
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0] if TEST_PAYLOAD else {},
        'repos_payload': TEST_PAYLOAD[0][1] if TEST_PAYLOAD else [],
        'expected_repos': (TEST_PAYLOAD[0][2]
                           if len(TEST_PAYLOAD) > 0
                           and len(TEST_PAYLOAD[0]) > 2
                           else []),
        'apache2_repos': (TEST_PAYLOAD[0][3]
                          if len(TEST_PAYLOAD) > 0 and len(TEST_PAYLOAD[0]) > 3
                          else []),
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for GithubOrgClient.

    Tests the public_repos method with actual method calls
    while only mocking external HTTP requests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class method for integration tests.

        Mocks requests.get to return fixture payloads based on URL.
        """
        # Define side_effect function to return different payloads based on URL
        def get_side_effect(url):
            """
            Side effect function to return appropriate payload based on URL.
            """
            class MockResponse:
                def __init__(self, json_data):
                    self.json_data = json_data

                def json(self):
                    return self.json_data

            if url == "https://api.github.com/orgs/google":
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload.get("repos_url", ""):
                return MockResponse(cls.repos_payload)
            else:
                return MockResponse({})

        # Start patcher for requests.get
        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down class method for integration tests.

        Stops the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test public_repos method without license filter.

        Verifies that the method returns the expected results
        based on the fixtures.
        """
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Test public_repos method with Apache 2.0 license filter.

        Verifies that the method returns the expected results
        when filtering for Apache 2.0 licensed repositories.
        """
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
