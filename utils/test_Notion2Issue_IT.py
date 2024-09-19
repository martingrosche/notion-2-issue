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
        os.environ['GITHUB_OUTPUT'] = 'github_output.txt'
        os.environ['GITHUB_STEP_SUMMARY'] = 'github_step_summary.md'

    def tearDown(self):
        for key in ['INPUT_NOTIONTOKEN', 'INPUT_GITHUBTOKEN', 'INPUT_NOTIONDATABASE', 'GITHUB_REPOSITORY', 'GITHUB_OUTPUT', 'GITHUB_STEP_SUMMARY']:
            if key in os.environ:
                del os.environ[key]
        
        for file in ['github_output.txt', 'github_step_summary.md']:
            if os.path.exists(file):
                os.remove(file)

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
                "title": "Test Issue 1",
                "description": "Test Description 1",
                "assignees": ["TestUser1"],
                "labels": ["bug"],
                "project_number": 1
            },
            {
                "title": "Test Issue 2",
                "description": "Test Description 2",
                "assignees": ["TestUser2"],
                "labels": ["enhancement"],
                "project_number": 1
            }
        ]

        mock_github_helper = MockGitHubHelper.return_value
        mock_github_helper.get_issues.return_value = []
        mock_github_helper.create_job_summary.return_value = "Fake summary"
        mock_repo = MagicMock()
        mock_github_helper.repo = mock_repo
        mock_repo.has_projects = True
        
        mock_issue1 = MagicMock()
        mock_issue1.title = "Test Issue 1"
        mock_issue1.number = 1
        mock_issue1.raw_data = {"node_id": "fake_node_id_1"}
        
        mock_issue2 = MagicMock()
        mock_issue2.title = "Test Issue 2"
        mock_issue2.number = 2
        mock_issue2.raw_data = {"node_id": "fake_node_id_2"}
        
        mock_github_helper.create_issue.side_effect = [mock_issue1, mock_issue2]

        mock_graphql_helper = MockGraphQLHelper.return_value
        mock_graphql_helper.query_prj.return_value = {"id": "fake_project_id", "title": "Test Project"}
        mock_graphql_helper.add_item_to_prj.return_value = True

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Issue 'Test Issue 1' added to project 'Test Project' successfully.", output)
        self.assertIn("Issue 'Test Issue 2' added to project 'Test Project' successfully.", output)
        
        mock_github_helper.get_issues.assert_called_once()
        mock_github_helper.create_job_summary.assert_called_once()
        self.assertEqual(mock_github_helper.create_issue.call_count, 2)
        mock_github_helper.create_issue.assert_any_call(
            "Test Issue 1",
            "Test Description 1",
            ["TestUser1"],
            ["bug"]
        )
        mock_github_helper.create_issue.assert_any_call(
            "Test Issue 2",
            "Test Description 2",
            ["TestUser2"],
            ["enhancement"]
        )
        self.assertEqual(mock_graphql_helper.query_prj.call_count, 2)
        self.assertEqual(mock_graphql_helper.add_item_to_prj.call_count, 2)

        self.assertTrue(os.path.exists('github_output.txt'), "github_output.txt file was not created")
        self.assertTrue(os.path.exists('github_step_summary.md'), "github_step_summary.md file was not created")
        
        with open('github_output.txt', 'r') as f:
            github_output = f.read()
        self.assertEqual(github_output, "issueNumbers=[1, 2]")

        mock_github_helper.create_job_summary.assert_called_once()
        with open('github_step_summary.md', 'r') as f:
            summary_output = f.read()
        self.assertEqual(summary_output, "Fake summary")


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
        mock_github_helper.create_job_summary.return_value = "Fake summary"

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Issue with the same title 'Existing Issue' already exists on GitHub.", output)
        mock_github_helper.create_issue.assert_not_called()
        mock_github_helper.create_job_summary.assert_called_once()
        self.assertFalse(os.path.exists('github_output.txt'), "github_output.txt file was created")
        self.assertTrue(os.path.exists('github_step_summary.md'), "github_step_summary.md file was not created")


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
        mock_issue.number = 1
        mock_github_helper.create_issue.return_value = mock_issue
        mock_github_helper.create_job_summary.return_value = "Fake summary"

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Current repository isn't linked to a project.", output)
        mock_github_helper.create_issue.assert_called_once()
        mock_github_helper.create_job_summary.assert_called_once()
        
        self.assertTrue(os.path.exists('github_output.txt'), "github_output.txt file was not created")
        self.assertTrue(os.path.exists('github_step_summary.md'), "github_step_summary.md file was not created")

        with open('github_output.txt', 'r') as f:
            github_output = f.read()
        self.assertEqual(github_output, "issueNumbers=[1]")

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
        mock_issue.number = 1
        mock_github_helper.create_issue.return_value = mock_issue
        mock_github_helper.create_job_summary.return_value = "Fake summary"

        mock_graphql_helper = MockGraphQLHelper.return_value
        mock_graphql_helper.query_prj.return_value = None

        self.capture_output()
        sync_notion_to_github()
        output = self.release_output()

        self.assertIn("Cannot find a linked project with number 999. Please link the correct project manually.", output)
        mock_github_helper.create_issue.assert_called_once()
        mock_github_helper.create_job_summary.assert_called_once()

        self.assertTrue(os.path.exists('github_output.txt'), "github_output.txt file was not created")
        self.assertTrue(os.path.exists('github_step_summary.md'), "github_step_summary.md file was not created")

        
        with open('github_output.txt', 'r') as f:
            github_output = f.read()
        self.assertEqual(github_output, "issueNumbers=[1]")
