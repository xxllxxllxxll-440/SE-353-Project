# Git Workflow

This project uses Git and GitHub for version control. Each team member should have their own local copy of the repository.

## Table of Contents

- [GitHub Desktop](#github-desktop)
  - [Set Up GitHub Desktop](#set-up-github-desktop)
  - [Use GitHub Desktop for the Normal Work Cycle](#use-github-desktop-for-the-normal-work-cycle)
  - [Create a Feature Branch in GitHub Desktop](#create-a-feature-branch-in-github-desktop)
- [Command Line](#command-line)
  - [Configure Git](#configure-git)
  - [Use the Command Line for the Normal Work Cycle](#use-the-command-line-for-the-normal-work-cycle)
  - [Work on a Feature Branch from the Command Line](#work-on-a-feature-branch-from-the-command-line)
- [Before Pushing](#before-pushing)
- [Do Not Commit Secrets](#do-not-commit-secrets)
- [If a Push Is Rejected](#if-a-push-is-rejected)
- [Recommended Commit Messages](#recommended-commit-messages)

## GitHub Desktop

You can use GitHub Desktop instead of the command line for the same workflow.

### Set Up GitHub Desktop

1. Install [GitHub Desktop](https://desktop.github.com/) and sign in to your GitHub account.
2. Select **File > Clone Repository** and choose this project from the **GitHub.com** tab, or use the **URL** tab if you have the repository URL.
3. Choose a local folder for the project and select **Clone**.
4. Open GitHub Desktop's settings/preferences and, under **Git**, check that your name and email are correct. These are recorded with your commits.

### Use GitHub Desktop for the Normal Work Cycle

1. In GitHub Desktop, select this project under **Current Repository**.
2. Before editing, select **Fetch origin**. If GitHub Desktop indicates that there are incoming changes, select **Pull origin** to bring them into your local copy.
3. Make and test your changes in the project.
4. Return to GitHub Desktop and review the changed files in the **Changes** tab. Select or clear the checkboxes to include only the files you intend to commit. Do not commit secrets such as `.env` files, passwords, or API keys.
5. Enter a short description in the **Summary** field, then select **Commit to [your branch]**.
6. Select **Push origin** to upload your commit to GitHub. A commit is only a local checkpoint until it is pushed.

### Create a Feature Branch in GitHub Desktop

For larger features, first select `main` from **Current Branch**, then fetch and pull so it is up to date. Select **Current Branch > New Branch**, enter a descriptive branch name (for example, `inventory-page`), and create the branch from `main`. Follow the normal work cycle above, then select **Publish branch** to upload it. Open the project on GitHub.com and create a pull request to have the branch reviewed and merged into `main`.

For small changes, the team may work directly on `main` if everyone agrees. Pull before starting and push frequently.

## Command Line

### Configure Git

After cloning the repository, configure your Git username and email if you have not already done so:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

You can check your configuration with:

```bash
git config --global --list
```

### Use the Command Line for the Normal Work Cycle

For most work, get the newest version before making changes:

```bash
git pull
```

Make your changes to the project normally.

You can check which files have changed with:

```bash
git status
```

It is a good idea to check this before committing so you know exactly what you are about to save.

First, add the files you want to include in the commit:

```bash
git add .
```

Then create a commit:

```bash
git commit -m "Describe what you changed"
```

For example:

```bash
git commit -m "Add inventory item page"
```

A commit is a saved checkpoint of your work. It does not upload anything to GitHub yet.

After committing:

```bash
git push
```

Your commit will now be uploaded to GitHub.

The normal work cycle is:

```bash
git pull

# Make your changes

git status
git add .
git commit -m "Describe your changes"
git push
```

### Work on a Feature Branch from the Command Line

For larger features, use a separate branch instead of working directly on `main`.

```bash
git checkout -b inventory-page
```

Work normally, then:

```bash
git add .
git commit -m "Add inventory page"
git push -u origin inventory-page
```

The branch can then be reviewed and merged into `main`.

For small changes, the team may work directly on `main` if everyone agrees, but pulling before starting and pushing frequently is still required.

## Before Pushing

Make sure the application still runs before pushing your changes.

If you changed code, templates, database code, or other important functionality, test the affected functionality before committing.

If GitHub Desktop reports that the remote has changes you do not have locally, fetch and pull before trying again. **Do not force-push.** If a merge conflict appears, stop and ask another team member for help; do not discard or overwrite files to make it disappear.

## Do Not Commit Secrets

Never commit:

- Database passwords
- API keys
- `.env` files
- Personal credentials
- Private configuration files

These should be listed in `.gitignore`.

## If a Push Is Rejected

If Git says your push was rejected because the remote repository contains changes you do not have locally, **do not use `git push --force`**.

Run `git pull` (or fetch and pull in GitHub Desktop) to bring in remote changes before trying again. If Git reports a merge conflict, stop and ask another team member for help before continuing. Do not randomly delete or overwrite files to make the conflict disappear.

## Recommended Commit Messages

Commit messages should briefly describe what was changed.

Good:

```text
Add inventory item form
Fix vendor deletion
Add purchase database model
Update dashboard styling
Fix low-stock calculation
```

Avoid vague messages such as:

```text
stuff
changes
update
fixed it
asdf
```
