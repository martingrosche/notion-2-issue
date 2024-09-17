from typing import Any, List, Optional, Union

import requests


class NotionHelper:
    def __init__(self, notion_token: str, database_id: str):
        self.notion_token = notion_token
        self.database_id = database_id
        self.headers = {
            "Accept": "application/json",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.notion_token}"
        }
        self.url = f"https://api.notion.com/v1/databases/{self.database_id}/query"


    def _get_property(self, props: dict, name: str, prop_type: str) -> Optional[Any]:
        try:
            prop = props[name][prop_type]
            if prop_type in ["title", "rich_text"]:
                return prop[0]["plain_text"]
            return prop
        except (KeyError, IndexError):
            return None

    def get_title(self, props: dict, name: str) -> str:
        return self._get_property(props, name, "title") or ""

    def get_rich_text(self, props: dict, name: str) -> str:
        return self._get_property(props, name, "rich_text") or ""

    def get_number(self, props: dict, name: str) -> Optional[Union[int, float]]:
        return self._get_property(props, name, "number")

    def get_multi_select(self, props: dict, name: str) -> List[str]:
        try:
            return [item["name"] for item in props[name]["multi_select"]]
        except KeyError:
            return []

    def get_notion_issues(self) -> List[dict]:
        payload = {"page_size": 100}
        
        response = requests.post(self.url, json=payload, headers=self.headers)
        response_dict = response.json()
        notion_issues = response_dict["results"]

        issues = []
        for i in reversed(notion_issues):
            properties = i.get("properties")
            if properties is None:
                continue  # Skip this issue if properties are not found
            
            title = self.get_title(properties, "Title")
            if not title:
                continue  # Skip this issue if title is empty

            issue = {
                "title": title,
                "description": self.get_rich_text(properties, "Discription"),
                "assignees": self.get_multi_select(properties, "Assignees"),
                "labels": self.get_multi_select(properties, "Labels"),
                "project_number": self.get_number(properties, "ProjectNumber")
            }
            issues.append(issue)

        return issues
