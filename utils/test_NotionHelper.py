import json
import os
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from utils.NotionHelper import NotionHelper


class TestNotionHelper():
    @pytest.fixture
    def resource_data(self):
        results = os.path.join(os.path.dirname(__file__), "..", "resources", "results.json")
        with open(results) as json_file:
            return json.load(json_file)
            
    @pytest.fixture
    def notion_helper(self):
        return NotionHelper("fake_token", "fake_database_id")

    @pytest.mark.parametrize("helper_index, expected_title", [
        (0, "Sample Two"),
        (1, "Sample One")
    ])
    def test_get_title(self, notion_helper, resource_data, helper_index, expected_title):
        properties = resource_data[helper_index].get("properties")
        assert notion_helper.get_title(properties, "Title") == expected_title

    def test_get_title_nonexistent(self, notion_helper, resource_data):
        properties = resource_data[0].get("properties")
        assert notion_helper.get_title(properties, "NonexistentTitle") == ""

    @pytest.mark.parametrize("helper_index, expected_body", [
        (0, "My Sample Body 2"),
        (1, "My Sample Body 1")
    ])
    def test_get_rich_text(self, notion_helper, resource_data, helper_index, expected_body):
        properties = resource_data[helper_index].get("properties")
        assert notion_helper.get_rich_text(properties, "Discription") == expected_body

    def test_get_rich_text_nonexistent(self, notion_helper, resource_data):
        properties = resource_data[0].get("properties")
        assert notion_helper.get_rich_text(properties, "NonexistentRichText") == ""

    @pytest.mark.parametrize("helper_index, expected_assignee, expected_label", [
        (0, [], ["bug"]),
        (1, ["martingrosche"], ["feature request"])
    ])
    def test_get_multi_select(self, notion_helper, resource_data, helper_index, expected_assignee, expected_label):
        properties = resource_data[helper_index].get("properties")
        assert notion_helper.get_multi_select(properties, "Assignees") == expected_assignee
        assert notion_helper.get_multi_select(properties, "Labels") == expected_label

    def test_get_multi_select_nonexistent(self, notion_helper, resource_data):
        properties = resource_data[0].get("properties")
        assert notion_helper.get_multi_select(properties, "NonexistentMultiSelect") == []

    @pytest.mark.parametrize("helper_index, expected_number", [
        (0, 'None'),
        (1, 1)
    ])
    def test_get_number(self, notion_helper, resource_data, helper_index, expected_number):
        properties = resource_data[helper_index].get("properties")
        assert notion_helper.get_number(properties, "ProjectNumber") == expected_number

    def test_get_number_nonexistent(self, notion_helper, resource_data):
        properties = resource_data[0].get("properties")
        assert notion_helper.get_number(properties, "NonexistentNumber") is None

    @patch('requests.post')
    def test_get_notion_issues(self, mock_post, notion_helper, resource_data):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": resource_data}
        mock_post.return_value = mock_response

        issues = notion_helper.get_notion_issues()

        assert len(issues) == 2
        assert issues[0]["title"] == "Sample One"
        assert issues[1]["title"] == "Sample Two"
        assert issues[0]["description"] == "My Sample Body 1"
        assert issues[1]["description"] == "My Sample Body 2"
        assert issues[0]["assignees"] == ["martingrosche"]
        assert issues[1]["assignees"] == []
        assert issues[0]["labels"] == ["feature request"]
        assert issues[1]["labels"] == ["bug"]
        assert issues[0]["project_number"] == 1
        assert issues[1]["project_number"] == 'None'
