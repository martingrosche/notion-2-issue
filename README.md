# Notion 2 Issue

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Version: v1.0.0](https://img.shields.io/badge/Version-v1.0.0-green)](https://github.com/martingrosche/notion-2-issue/releases)
[![GitHub Action: Marketplace](https://img.shields.io/badge/GitHub%20Action-Marketplace-blue?logo=github)](https://github.com/marketplace/actions/notion-2-issue)

This GitHub action creates GitHub issues depending on a notion database and link them to there referenced project.

## Table Of Content

- [Table Of Content](#table-of-content)
- [Usage](#usage)
- [Notion Database Template](#notion-database-template)
- [Features](#features)
- [Example Usage](#example-usage)
- [Input Description](#input-description)
- [Issues](#issues)
- [License](#license)

## Usage

1. Create a [new internal Notion integration](https://www.notion.so/my-integrations), give it a name (e.g. `github`) and note the value of the Internal Integration Token for further usage.
2. Connect Notion Database to the name of the Integration Token. Open your Database -> `...` -> `Add Connection` (e.g. `github`).
3. Note the `Database ID`.
   > `https://www.notion.so/<long_hash_1>?v=<long_hash_2>`

   The `long_hash_1` is the database ID and `<long_hash_2>` is the view ID.
4. In your GitHub repository, go to `Settings` -> `Secrets` -> `Actions`, and add a `New repository secret`.
   - Create a first secret and set the `Name` to `NOTION_TOKEN` and the `Value` to the Internal Integration Token you created in step 1.
   - Create a second one and set the name `Name` to `NOTION_DATABASE` and the `Value` to the `Database ID` described in Step 3.
5. [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) are recommended.

## Notion Database Template

Here is a [database template](https://plastic-giant-1e8.notion.site/0a57a7856cf9448e821583be3bcfa355?v=e3064104173f4d59990e9e072124e389) page for creating GitHub issues from a database. Switch to that page, duplicate it and test it.
![GitHub_Issues_Template](docs/images/GitHub_Issues_Template_dark.png#gh-dark-mode-only)
![GitHub_Issues_Template](docs/images/GitHub_Issues_Template_light.png#gh-light-mode-only)

## Features

- Create GitHub issues via notion database
- Link created GitHub issue to the referenced project (*ProjectNumber*)
  > To find the project number, look at the project URL. For example, https://github.com/orgs/octo-org/projects/5 has a project number of 5.

## Example Usage

The following example demonstrates a GitHub action that runs on a schedule or is triggered manually and sets the `Read and write permissions` only for this one. To set this permission globally go to `Settings` -> `Actions` -> `General` -> `Workflow permissions` -> `Read and write permissions` -> `Save`. Make sure your repo can run actions `Settings` -> `Actions` -> `General` -> `Actions Permission` -> `Allow all actions and reusable workflows` -> `Save`.

```yaml
name: Notion Database
on: 
  # run action manually
  workflow_dispatch:
  # run every night at midnight 
  schedule:
    - cron: '0 0 * * *'
permissions:
  contents: read
  repository-projects: read
  issues: write
jobs:
  sync-github-issues:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run Action
        uses: martingrosche/notion-2-issue@v1.1.0
        with:
          notionToken: ${{ secrets.NOTION_TOKEN }}
          notionDatabase: ${{ secrets.NOTION_DATABASE }}
```

## Input Description

| Name             | Required | Default             | Description                                                                                                                            |
| ---------------- | -------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `notionToken`    | True     |                     | The Notion internal integration token. See [Usage](#usage) for more information.                                                       |
| `notionDatabase` | True     |                     | The notion database ID. See [Usage](#usage) for more information.                                                                      |
| `githubToken`    | False    | ${{ github.token }} | [GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) for authentication in a workflow run |

## Issues

To report a bug or request an enhancement to this plugin please raise a new [GitHub issue](https://github.com/martingrosche/notion-2-issue/issues/new/choose).

## License

This project is licensed under the terms of the [MIT license](./LICENSE) @[martingrosche](https://github.com/martingrosche).
