# Notion 2 Issue

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/martingrosche/notion-2-issue?display_name=release&logo=github&color=green)](https://github.com/martingrosche/notion-2-issue/releases)
[![GitHub Action: Marketplace](https://img.shields.io/badge/GitHub-Marketplace-blue?logo=githubactions)](https://github.com/marketplace/actions/notion-2-issue)

Notion 2 Issue is a GitHub Action that automatically creates GitHub issues based on entries in a Notion database and links them to their referenced projects. This tool bridges the gap between Notion task management and GitHub issue tracking, streamlining your workflow.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
  - [Notion Setup](#notion-setup)
  - [GitHub Setup](#github-setup)
- [Notion Database Template](#notion-database-template)
- [Usage](#usage)
- [Example Workflow](#example-workflow)
- [Input Parameters](#input-parameters)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Issues](#issues)
- [License](#license)

## Features

1. **Automated Issue Creation**: Generate GitHub issues directly from Notion database entries.
2. **Project Integration**: Automatically link created issues to referenced GitHub projects.
3. **Output Tracking**: Provides a list of created issue numbers for further automation or tracking.
4. **Job Summary**: Displays a summary of the action's results for quick review.

## Setup

### Notion Setup

1. Create a [new internal Notion integration](https://www.notion.so/my-integrations):
   - Give it a name (e.g., `github`)
   - Note the Internal Integration Token for later use

2. Connect your Notion Database to the integration:
   - Open your Database → `...` → `Add Connection` → Select your integration

3. Note the `Database ID`:
   - In the database URL: `https://www.notion.so/<DATABASE_ID>?v=<VIEW_ID>`
   - The `<DATABASE_ID>` is what you need

### GitHub Setup

1. In your GitHub repository, go to `Settings` → `Secrets` → `Actions`
2. Add two new repository secrets:
   - `NOTION_TOKEN`: Set to your Notion Internal Integration Token
   - `NOTION_DATABASE`: Set to your Notion Database ID

## Notion Database Template

Use the [provided template](https://plastic-giant-1e8.notion.site/0a57a7856cf9448e821583be3bcfa355?v=e3064104173f4d59990e9e072124e389) to set up your Notion database for GitHub issue creation. Duplicate the template to get started quickly.

![Notion Database Template](docs/images/GitHub_Issues_Template_dark.png#gh-dark-mode-only)
![Notion Database Template](docs/images/GitHub_Issues_Template_light.png#gh-light-mode-only)

## Usage

1. Set up your Notion database and GitHub secrets as described in the [Setup](#setup) section.
2. Create a GitHub Actions workflow file (e.g., `.github/workflows/notion-sync.yml`) in your repository.
3. Configure the workflow to use the `martingrosche/notion-2-issue` action (see [Example Workflow](#example-workflow)).
4. Commit and push the workflow file to trigger the action.

## Example Workflow

```yaml
name: Notion to GitHub Issues Sync
on: 
  workflow_dispatch:  # Allows manual triggering
  schedule:
    - cron: '0 0 * * *'  # Runs daily at midnight UTC

permissions:
  contents: read
  repository-projects: read
  issues: write

jobs:
  sync-notion-to-github:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Sync Notion to GitHub Issues
        id: notion_sync
        uses: martingrosche/notion-2-issue@v1.1.0
        with:
          notionToken: ${{ secrets.NOTION_TOKEN }}
          notionDatabase: ${{ secrets.NOTION_DATABASE }}
          githubToken: ${{ secrets.PROJECT_TOKEN }}

      - name: Print Created Issue Numbers
        run: echo "Created issue numbers: ${{ steps.notion_sync.outputs.issueNumbers }}"
```

## Input Parameters

| Name             | Required | Default               | Description                       |
| ---------------- | -------- | --------------------- | --------------------------------- |
| `notionToken`    | Yes      |                       | Notion internal integration token |
| `notionDatabase` | Yes      |                       | Notion database ID                |
| `githubToken`    | No       | `${{ github.token }}` | GitHub token for authentication   |

> **Note**: For project linking, use a `githubToken` with full control of projects. See [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for more information.

## Output

| Name           | Description                         |
| -------------- | ----------------------------------- |
| `issueNumbers` | A list of the created issue numbers |

## Troubleshooting

- **Issues not being created**: Ensure your Notion token has the correct permissions and the database ID is correct.
- **Project linking fails**: Verify that your GitHub token has sufficient permissions to access and modify projects.
- **Workflow doesn't run**: Check that Actions are enabled for your repository and the workflow file is in the correct location.

For more detailed troubleshooting, check the Action logs in your GitHub repository.

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a new Pull Request

Please ensure your code adheres to the existing style and all tests pass before submitting a PR.

## Issues

To report a bug or request an enhancement, please [open a new GitHub issue](https://github.com/martingrosche/notion-2-issue/issues/new/choose).

## License

This project is licensed under the [MIT License](./LICENSE) © [martingrosche](https://github.com/martingrosche).
