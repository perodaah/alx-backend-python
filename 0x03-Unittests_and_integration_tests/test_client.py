#!/usr/bin/env python3

"""
Unit tests for GithubOrgClient class in client.py.
"""

import unittest
from unittest.mock import Mock, patch, PropertyMock
from parameterized import parameterized, parameterized_class
from requests import HTTPError

from client import GithubOrgClient
import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """
    Test cases for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns the correct data.

        Ensures get_json is called once with the expected URL and
        that no real HTTP requests are made.
        """
        expected_data = {
            "name": f"{org_name.capitalize()} Org",
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }

        mock_get_json.return_value = expected_data

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_data)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """
        Test that _public_repos_url returns the correct value
        based on the mocked org payload.
        """
        expected_url = "https://api.github.com/orgs/test_org/repos"
        mock_org_payload = {
            "repos_url": expected_url
        }

        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = mock_org_payload

            client = GithubOrgClient("test_org")
            result = client._public_repos_url

            self.assertEqual(result, expected_url)

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns the correct data.
        """
        expected_data = {
            "name": f"{org_name}-org",
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = expected_data
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_data)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """
        Test _public_repos_url returns correct repos_url.
        """
        expected_url = "https://api.github.com/orgs/test_org/repos"
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": expected_url}
            client = GithubOrgClient("test_org")
            self.assertEqual(client._public_repos_url, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        Test public_repos returns expected repo names.
        """
        mock_repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]
        mock_get_json.return_value = mock_repos_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = (
                "https://api.github.com/orgs/test_org/repos"
            )
            client = GithubOrgClient("test_org")
            self.assertEqual(client.public_repos(), ["repo1", "repo2"])

            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/test_org/repos"
            )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test has_license returns expected result.
        """
        client = GithubOrgClient("test_org")
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class([
    {
        "org_payload": fixtures.TEST_PAYLOAD[0][0],
        "repos_payload": fixtures.TEST_PAYLOAD[0][1],
        "expected_repos": fixtures.TEST_PAYLOAD[0][2],
        "apache2_repos": fixtures.TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for the GithubOrgClient using actual data fixtures."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get with URL-based mock responses."""
        # Important: Add `repos_url` to the org payload to avoid KeyError
        cls.org_payload["repos_url"] = "" \
            "https://api.github.com/orgs/google/repos"

        route_payload = {
            "https://api.github.com/orgs/google": cls.org_payload,
            "https://api.github.com/orgs/google/repos": cls.repos_payload,
        }

        def get_payload(url):
            if url in route_payload:
                return Mock(**{"json.return_value": route_payload[url]})
            raise HTTPError(f"URL {url} not mocked")

        cls.get_patcher = patch("requests.get", side_effect=get_payload)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Stop the patched requests.get.
        Removes the class fixtures after running all tests.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns all repository names."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos filters repositories by license key."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
