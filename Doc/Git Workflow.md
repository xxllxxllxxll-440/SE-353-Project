# Git Workflow

This project uses Git and GitHub for version control. Each team member should have their own local copy of the repository.

## First-Time Setup

After cloning the repository, configure your Git username and email if you have not already done so:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

You can check your configuration with:

```bash
git config --global --list
```

## Before Starting Work

Always get the newest version of the project before making changes:

```bash
git pull
```

If you are using a Python virtual environment, activate it afterward if necessary:

```bash
source .venv/bin/activate
```

## Making Changes

Make your changes to the project normally.

You can check which files have changed with:

```bash
git status
```

It is a good idea to check this before committing so you know exactly what you are about to save.

## Saving Your Changes

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

## Uploading Your Changes

After committing:

```bash
git push
```

Your commit will now be uploaded to GitHub.

## Normal Work Cycle

For most work, the process should be:

```bash
git pull

# Make your changes

git status
git add .
git commit -m "Describe your changes"
git push
```

### Before Pushing

Make sure the application still runs before pushing your changes:

```bash
python run.py
```

If you changed Python code, templates, database code, or other important functionality, test the affected functionality before committing.

## Important: Do Not Commit Secrets

Never commit:

* Database passwords
* API keys
* `.env` files
* Personal credentials
* Private configuration files

These should be listed in `.gitignore`.

## If `git push` Is Rejected

If Git says your push was rejected because the remote repository contains changes you do not have locally, **do not use `git push --force`**.

First run:

```bash
git pull
```

If Git reports a merge conflict, stop and ask another team member for help before continuing. Do not randomly delete or overwrite files to make the conflict disappear.

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

## Working on Different Features

For larger features, use a separate branch instead of working directly on `main`.

Create a branch:

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
