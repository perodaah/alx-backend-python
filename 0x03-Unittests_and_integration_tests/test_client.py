#!/usr/bin/env python3
"""Unit tests for GithubOrgClient.

Covers:
- org property retrieval (memoized)
- _public_repos_url property derivation
- public_repos list extraction and filtering logic
"""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
import requests


class TestGithubOrgClient(unittest.TestCase):
    """Test suite for GithubOrgClient focusing on repo/org metadata."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Verify org returns expected payload and single get_json call."""
        expected = {
            "name": org_name,
            "repos_url": (
                f"https://api.github.com/orgs/{org_name}/repos"
            ),
        }
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self):
        """Ensure _public_repos_url pulls repos_url from mocked org payload."""
        org_payload = {
            "repos_url": "https://api.github.com/orgs/example/repos"
        }
        with patch.object(GithubOrgClient, 'org', return_value=org_payload):
            client = GithubOrgClient("example")
            self.assertEqual(
                client._public_repos_url,
                org_payload["repos_url"],
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Verify public_repos returns repo names; mocks called once."""
        repos_payload = [
            {
                "name": "repo1",
                "license": {"key": "mit"},
            },
            {
                "name": "repo2",
                "license": {"key": "apache-2.0"},
            },
            {
                "name": "repo3",
                "license": {"key": "mit"},
            },
        ]
        mock_get_json.return_value = repos_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                "http://example.com/org/repos"
            )
            client = GithubOrgClient("example")
            self.assertEqual(
                client.public_repos(),
                ["repo1", "repo2", "repo3"],
            )
            mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with("http://example.com/org/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method with varied license keys."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class(
    [
        {
            "org_payload": TEST_PAYLOAD[0][0],
            "repos_payload": TEST_PAYLOAD[0][1],
            "expected_repos": TEST_PAYLOAD[0][2],
            "apache2_repos": TEST_PAYLOAD[0][3],
        }
    ]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls) -> None:
        """Start patching requests.get and configure side_effect
        to return fixture payloads."""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            response = MagicMock()
            if url.endswith("/repos"):
                response.json.return_value = cls.repos_payload
            else:
                response.json.return_value = cls.org_payload
            return response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test that public_repos returns expected repo names
        from fixture payload."""
        client = GithubOrgClient("testorg")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test that public_repos filters repos by 'apache-2.0'
        license using fixture payload."""
        client = GithubOrgClient("testorg")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
