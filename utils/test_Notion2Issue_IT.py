import io
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from script import sync_notion_to_github


class TestNotionToGitHubSync(unittest.TestCase):
    def setUp(self):
        os.environ['INPUT_NOTIONTOKEN'] = 'fake_notion_token'
        os.environ['INPUT_GITHUBTOKEN'] = 'fake_github_token'
        os.environ['INPUT_NOTIONDATABASE'] = 'fake_database_id'
        os.environ['GITHUB_REPOSITORY'] = 'fake_owner/fake_repo'

    def capture_output(self):
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    def release_output(self):
        sys.stdout = sys.__stdout__
        return self.captured_output.getvalue()

    @patch('script.NotionHelper')
    @patch('script.GitHubHelper')
    @patch('script.GraphQLHelper')
    def test_sync_successfully(self, MockGraphQLHelper, MockGitHubHelper, MockNotionHelper):
        mock_notion_helper = MockNotionHelper.return_value
        mock_notion_helper.get_notion_issues.return_value = [
            {
                "title": "Test Issue",
                "description": "Test Description",
                "assignees": ["TestUser"],
                "labels": ["bug"],
                "project_number": 1
            }
        ]

        mock_github_helper = MockGitHubHelper.return_value
        mock_github_helper.get_issues.return_value = []
        mock_repo = MagicMock()
        mock_github_helper.repo = mock_repo
        mock_repo.has_projects = True
        mock_issue = MagicMock()
        mock_issue.title = "Test Issue"
        mock_issue.raw_data = {"node_id": "fake_node_id"}
        mock_github_helper.create_issue.return_value = mock_issue

        mock_graphql_helper = MockGraphQLHelper.return_value
        mock_graphql_helper.query_prj.return_value = {"id": "fake_project_id", "title": "Test Project"}
        mock_graphql_helper.add_item_to_prj.return_value = True

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Issue 'Test Issue' added to project 'Test Project' successfully.", output)
        
        mock_github_helper.get_issues.assert_called_once()
        mock_github_helper.create_issue.assert_called_once_with(
            "Test Issue",
            "Test Description",
            ["TestUser"],
            ["bug"]
        )
        mock_graphql_helper.query_prj.assert_called_once_with(1)
        mock_graphql_helper.add_item_to_prj.assert_called_once_with("fake_project_id", "fake_node_id")

    @patch('script.NotionHelper')
    @patch('script.GitHubHelper')
    def test_existing_issue(self, MockGitHubHelper, MockNotionHelper):
        mock_notion_helper = MockNotionHelper.return_value
        mock_notion_helper.get_notion_issues.return_value = [
            {
                "title": "Existing Issue",
                "description": "Test Description",
                "assignees": ["TestUser"],
                "labels": ["bug"],
                "project_number": 1
            }
        ]

        mock_github_helper = MockGitHubHelper.return_value
        existing_issue = MagicMock()
        existing_issue.title = "Existing Issue"
        mock_github_helper.get_issues.return_value = [existing_issue]

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Issue with the same title 'Existing Issue' already exists on GitHub.", output)
        mock_github_helper.create_issue.assert_not_called()

    @patch('script.NotionHelper')
    @patch('script.GitHubHelper')
    @patch('script.GraphQLHelper')
    def test_no_project_linked(self, MockGraphQLHelper, MockGitHubHelper, MockNotionHelper):
        mock_notion_helper = MockNotionHelper.return_value
        mock_notion_helper.get_notion_issues.return_value = [
            {
                "title": "Test Issue",
                "description": "Test Description",
                "assignees": ["TestUser"],
                "labels": ["bug"],
                "project_number": 1
            }
        ]

        mock_github_helper = MockGitHubHelper.return_value
        mock_github_helper.get_issues.return_value = []
        mock_repo = MagicMock()
        mock_github_helper.repo = mock_repo
        mock_repo.has_projects = False
        mock_issue = MagicMock()
        mock_issue.title = "Test Issue"
        mock_github_helper.create_issue.return_value = mock_issue

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Current repository isn't linked to a project.", output)
        mock_github_helper.create_issue.assert_called_once()

    @patch('script.NotionHelper')
    @patch('script.GitHubHelper')
    @patch('script.GraphQLHelper')
    def test_project_not_found(self, MockGraphQLHelper, MockGitHubHelper, MockNotionHelper):
        mock_notion_helper = MockNotionHelper.return_value
        mock_notion_helper.get_notion_issues.return_value = [
            {
                "title": "Test Issue",
                "description": "Test Description",
                "assignees": ["TestUser"],
                "labels": ["bug"],
                "project_number": 999
            }
        ]

        mock_github_helper = MockGitHubHelper.return_value
        mock_github_helper.get_issues.return_value = []
        mock_repo = MagicMock()
        mock_github_helper.repo = mock_repo
        mock_repo.has_projects = True
        mock_issue = MagicMock()
        mock_issue.title = "Test Issue"
        mock_github_helper.create_issue.return_value = mock_issue

        mock_graphql_helper = MockGraphQLHelper.return_value
        mock_graphql_helper.query_prj.return_value = None

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Cannot find a linked project with number 999. Please link the correct project manually.", output)
        mock_github_helper.create_issue.assert_called_once()
