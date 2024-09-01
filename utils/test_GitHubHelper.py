from unittest.mock import Mock, patch

import pytest
from github import GithubException
from github.Issue import Issue
from github.Repository import Repository

from utils.GitHubHelper import GitHubHelper, GraphQLHelper


class TestGitHubHelper:
    @pytest.fixture
    def mock_github(self):
        with patch('github.Github') as mock:
            yield mock

    @pytest.fixture
    def mock_repo(self):
        repo = Mock(spec=Repository)
        repo.full_name = "test-org/test-repo"
        return repo

    @pytest.fixture
    def github_helper(self, mock_github, mock_repo):
        mock_github.return_value.get_repo.return_value = mock_repo
        return GitHubHelper("fake_token", "test-org/test-repo")

    def test_init(self, github_helper):
        assert github_helper.org == "test-org"
        assert github_helper.project == "test-repo"

    def test_get_issues(self, github_helper, mock_repo):
        mock_issues = [Mock(spec=Issue), Mock(spec=Issue)]
        mock_repo.get_issues.return_value = mock_issues
        issues = github_helper.get_issues()
        assert issues == mock_issues

    def test_get_organization(self, github_helper):
        assert github_helper.get_organization() == "test-org"

    def test_get_project(self, github_helper):
        assert github_helper.get_project() == "test-repo"

    def test_create_issue_success(self, github_helper, mock_repo):
        mock_issue = Mock(spec=Issue)
        mock_repo.create_issue.return_value = mock_issue
        
        issue = github_helper.create_issue("Test Issue", "Test Body", ["assignee1"], ["label1"])
        
        assert issue == mock_issue
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Test Body",
            assignees=["assignee1"],
            labels=["label1"]
        )

    def test_create_issue_failure(self, github_helper, mock_repo):
        mock_repo.create_issue.side_effect = GithubException(status=422, data={})
        
        issue = github_helper.create_issue("Test Issue", "Test Body")
        
        assert issue is None
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Test Body",
            assignees=[],
            labels=[]
        )

class TestGraphQLHelper:
    @pytest.fixture
    def graphql_helper(self):
        return GraphQLHelper("fake_token", "test-org/test-repo")

    @pytest.fixture
    def mock_response(self):
        mock = Mock()
        mock.json.return_value = {
            "data": {
                "organization": {
                    "projectV2": {
                        "id": "proj_123",
                        "title": "Test Project"
                    }
                }
            }
        }
        return mock

    @patch('requests.post')
    def test_query_prj_success(self, mock_post, graphql_helper, mock_response):
        mock_post.return_value = mock_response
        
        result = graphql_helper.query_prj(1)
        
        assert result == {"id": "proj_123", "title": "Test Project"}
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_query_prj_failure(self, mock_post, graphql_helper):
        mock_post.return_value.json.return_value = {"data": {"organization": None}}
        
        result = graphql_helper.query_prj(1)
        
        assert result is None

    @patch('requests.post')
    def test_add_item_to_prj_success(self, mock_post, graphql_helper):
        mock_post.return_value.json.return_value = {
            "data": {
                "addProjectV2ItemById": {
                    "item": {
                        "id": "item_456"
                    }
                }
            }
        }
        
        result = graphql_helper.add_item_to_prj("proj_123", "issue_789")
        
        assert result == "item_456"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_add_item_to_prj_failure(self, mock_post, graphql_helper):
        mock_post.return_value.json.return_value = {"data": {"addProjectV2ItemById": None}}
        
        result = graphql_helper.add_item_to_prj("proj_123", "issue_789")
        
        assert result is None
        