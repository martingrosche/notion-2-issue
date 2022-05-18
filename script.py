
import os
from logging import warning
from sqlite3 import DatabaseError

import github
import requests

from utils.NotionHelper import NotionHelper

# extracting all the input from environments
notion_token = os.environ["INPUT_NOTIONTOKEN"]
gh_token = os.environ["INPUT_GITHUBTOKEN"]
database_id = os.environ["INPUT_NOTIONDATABASE"]

# notion
url = "https://api.notion.com/v1/databases/{}/query".format(database_id)

payload = {"page_size": 100}
headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(notion_token)
}

response = requests.post(url, json=payload, headers=headers)
response_dict = response.json()
notion_issues = response_dict["results"]

issues = []
for i in reversed(notion_issues):
    properties = i.get("properties")
    if properties is None:
        raise DatabaseError("'properties' not found.")
    notionHelper = NotionHelper(properties)
    title = notionHelper.get_title("Title") # page linked
    if title == "":
        warning("'Title' property must not be empty.")
        continue
    notion_issue = {}
    notion_issue["title"] = title

    notion_issue["description"] = notionHelper.get_rich_text("Discription")
    notion_issue["assignees"] = notionHelper.get_multi_select("Assignees")
    notion_issue["labels"] = notionHelper.get_multi_select("Labels")

    issues.append(notion_issue)

# github
git = github.Github(gh_token)
repo = git.get_repo(os.environ["GITHUB_REPOSITORY"])
gh_issues = repo.get_issues()

for new_issue in issues:
    # do not create issues with the same title
    if list(filter(lambda i: i.title == new_issue["title"], gh_issues)):
        print("Issue with the same title '{}' allready exists on github.".format(new_issue["title"]))
        continue

    issue = repo.create_issue(
        title = new_issue["title"],
        body = new_issue["description"],
        assignees = new_issue["assignees"],
        labels = new_issue["labels"]
    )
    if issue:
        print("Create issue '{}'".format(new_issue["title"]))
    else:
        print("Failed to create issue '{}'".format(new_issue["title"]))

