import os
from typing import Dict, List, Optional

import github
import requests
from github.Issue import Issue
from github.PaginatedList import PaginatedList


class GitHubHelper:
    def __init__(self, auth_token: str, repo_name: str = os.environ.get("GITHUB_REPOSITORY")):
        self.git = github.Github(auth_token)
        self.repo = self.git.get_repo(repo_name)
        self.org, self.project = self.repo.full_name.split('/')

    def get_issues(self) -> PaginatedList[Issue]:
        return self.repo.get_issues()
    
    def get_organization(self) -> str:
        return self.org
    
    def get_project(self) -> str:
        return self.project
    
    def create_issue(self, title: str, body: str, assignees: List[str] = [], labels: List[str] = []) -> Optional[Issue]:
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                assignees=assignees,
                labels=labels
            )
            print(f"Created issue '{title}'.")
            return issue
        except github.GithubException as e:
            print(f"Failed to create issue '{title}'. Error: {str(e)}")
            return None


class GraphQLHelper:
    def __init__(self, auth: str, repo: str = os.environ.get("GITHUB_REPOSITORY"), graphql_url: str = "https://api.github.com/graphql"):
        self.auth = auth
        self.repo = repo
        self.url = graphql_url
        self.headers = {"Authorization": f"Bearer {self.auth}"}

    def query_prj(self, number: int, scope: str = 'organization') -> Optional[Dict[str, str]]:
        org = self.repo.split('/')[0]
        
        query = f'''
        query {{
            {scope}(login: "{org}") {{
                projectV2(number: {number}) {{
                    id
                    title
                }}
            }}
        }}
        '''
        
        response = self._make_request(query)
        
        try:
            project_data = response['data'][scope]['projectV2']
            return {
                "id": project_data['id'],
                "title": project_data['title']
            }
        except (KeyError, TypeError):
            return None
    
    def add_item_to_prj(self, prj_id: str, item_id: str) -> Optional[str]:
        mutation = f'''
        mutation {{
            addProjectV2ItemById(input: {{projectId: "{prj_id}", contentId: "{item_id}"}}) {{
                item {{
                    id
                }}
            }}
        }}
        '''
        
        response = self._make_request(mutation)
        
        try:
            return response['data']['addProjectV2ItemById']['item']['id']
        except (KeyError, TypeError):
            return None
        
    def _make_request(self, query: str) -> Dict:
        payload = {"query": query}
        response = requests.post(self.url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()