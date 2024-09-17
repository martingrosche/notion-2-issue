import os

from utils.GitHubHelper import GitHubHelper, GraphQLHelper
from utils.NotionHelper import NotionHelper


def sync_notion_to_github():
    # Extract input from environment
    notion_token = os.environ["INPUT_NOTIONTOKEN"]
    gh_token = os.environ["INPUT_GITHUBTOKEN"]
    database_id = os.environ["INPUT_NOTIONDATABASE"]
    repository = os.getenv("GITHUB_REPOSITORY")

    if not all([notion_token, gh_token, database_id, repository]):
        raise EnvironmentError("Missing required environment variables. Please check your .env file.")

    notion_helper = NotionHelper(notion_token, database_id)
    issues = notion_helper.get_notion_issues()

    gh_helper = GitHubHelper(gh_token, repository)
    gh_issues = gh_helper.get_issues()

    created_issue_numbers = []
    for new_issue in issues:
        if list(filter(lambda i: i.title == new_issue["title"], gh_issues)):
            print(f"Issue with the same title '{new_issue['title']}' already exists on GitHub.")
            continue
        
        issue = gh_helper.create_issue(
            new_issue["title"], 
            new_issue["description"], 
            new_issue["assignees"], 
            new_issue["labels"]
        )
        if not issue:
            continue

        created_issue_numbers.append(issue.number)

        if not new_issue["project_number"]:
            continue

        if not gh_helper.repo.has_projects:
            print(f"Current repository isn't linked to a project.")
            continue

        graphql_helper = GraphQLHelper(gh_token)
        prj = graphql_helper.query_prj(new_issue["project_number"]) or graphql_helper.query_prj(new_issue["project_number"], 'user')

        if not prj:
            print(f"Cannot find a linked project with number {new_issue['project_number']}. Please link the correct project manually.")
            continue

        prj_item = graphql_helper.add_item_to_prj(prj['id'], issue.raw_data['node_id'])
        if prj_item:
            print(f"Issue '{issue.title}' added to project '{prj['title']}' successfully.")
    
    if created_issue_numbers:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as gh_out_file:
            gh_out_file.write(f"issueNumbers={created_issue_numbers}")


if __name__ == '__main__':
    sync_notion_to_github()
