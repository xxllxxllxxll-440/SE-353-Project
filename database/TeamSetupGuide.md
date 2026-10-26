# Sixty-Three Social

Team setup guide – database starter code

This guide explains how to set up the shared database and run the Python code. It is meant for our team, not as documentation for a finished website.

## 1. What is included

| File or folder | What it does |
| --- | --- |
| [app/01\_create\_database.sql](app/01\_create\_database.sql) | Creates tables, relationships, and two views. |
| [app/02\_sample\_data.sql](app/02\_sample\_data.sql) | Adds fictional restaurant data for testing. |
| [app/03\_test\_queries.sql](app/03\_test\_queries.sql) | Checks inventory, vendors, and financial totals. |
| [app/database.py](app/database.py) | Connects Python to MySQL; inventory, purchases, and reports. |
| [app/test\_database\_logic.py](app/test\_database\_logic.py) | Small offline tests for purchase logic. |
| [app/.env.example](app/.env.example) | Template for local database settings; contains no password. |
| [app/requirements.txt](app/requirements.txt) | The two Python packages needed for this part. |

## 2. Get the project from GitHub

1\.  Accept the private repository invitation from the repository owner.

2\.  Open GitHub Desktop and clone the Sixty-Three-Social repository to your computer.

3\.  Open the folder you cloned. Do not edit or commit anyone else’s password or .env file.

For code changes, make your own branch and push it to GitHub. Open a pull request so the group can review before merging into main.

## 3. Set up or check the Aiven database

1\.  Get permission to use the team’s Aiven MySQL service. Use a separate database login if the service allows it. Share passwords privately, never through GitHub.

2\.  In MySQL Workbench, connect to the team’s restaurant MySQL service using its actual host, port, and SSL settings.

3\.  If the tables do not exist yet, open and run `01\_create\_database.sql` first, then `02\_sample\_data.sql`. If there is already team data, check with Julius before changing anything.

4\.  Run `03\_test\_queries.sql` to check the tables and see some sample results.

On a fresh sample database, there should be 9 tables, 2 views, 4 inventory items, and 3 vendors. Existing shared data may give different totals.

## 4. Set up Python on Windows

Open PowerShell in the cloned repository, then run these commands in order:

```PowerShell
py -m venv .venv

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

Copy-Item .env.example .env

cd database
```

If the `py` command is not recognized, try `python` instead. Open `database/.env` in Notepad and replace the placeholders with your personal Aiven connection details:

```PowerShell
DB\_HOST=your-service-hostname

DB\_PORT=your-service-port

DB\_USER=your-database-username

DB\_PASSWORD=your-private-password

DB\_NAME=restaurant\_project

DB\_SSL\_CA=C:/path/to/your/ca.pem
```

Download the Aiven CA certificate for the service and use its full local path. Do not upload `.env` or `ca.pem`. Keep SSL certificate checking enabled.

## 5. Test the setup

While PowerShell is still in the database folder, check the connection:

```PowerShell
.\\.venv\\Scripts\\python.exe -c "import database; print(database.connection\_check())"
```

You should see the active database name and MySQL version. This verifies the Python connection, not the whole website.

Run the local unit tests with:

```PowerShell
.\\.venv\\Scripts\\python.exe -m unittest -v test\_database\_logic.py
```

These unit tests use fake database connections. They test some purchase calculations and rollback behavior, but do not prove that the live Aiven database works.

For a database test, use `03\_test\_queries.sql` in Workbench. Do not create test purchases on the shared database unless the group agrees first.

## 6. How the application will use this

- Julius: maintains the MySQL tables, sample data, Python database functions, and financial queries.
- Cole: connects database.py to the Flask backend and handles application routes and access checks.
- Jorden: builds the HTML/CSS interface and connects it to the backend routes. Browser code must not contain the database password.

Example: the frontend asks the backend for an inventory list. The backend calls inventory() in database.py, which reads the MySQL tables. The browser does not connect directly to Aiven.

## 7. What is complete and what is not

| Included in this starter | Still to be developed |
| --- | --- |
| Database tables and sample records | Full website/dashboard |
| Inventory, vendor, purchase, and report functions | User login and role permissions |
| Low-stock database view | Routes connecting pages to Python |
| Offline tests and SQL check queries | Exporting/printing and deployment |

The financial report is a basic comparison of recorded revenue and expenses. It is not a full accounting system. Purchase costs already appear in the expenses table, so do not count them a second time.

## 8. Common setup problems

| Problem | What to check |
| --- | --- |
| Access denied | Confirm Aiven username, password, and permissions. |
| Unknown database / missing tables | Check the service and run the schema script if appropriate. |
| SSL certificate error | Make sure `DB\_SSL\_CA` points to the correct CA file. |
| Python import error | Activate/use `.venv` and install requirements.txt. |
| Different totals from the guide | Another teammate may already have changed the shared data. |

## 9. Before we submit anything

- Verify the code still runs on at least one teammate’s computer.
- Make sure `.env`, `ca.pem`, and passwords are not in GitHub Desktop’s Changes list.
- Record any actual test results; do not report a test as passed unless someone ran it.
- Confirm the repo is private and Jorden and Cole can clone it.
- Add the website files as the team builds them. This folder is the database portion only.

If we later change a table, tell the group before rerunning the setup scripts. CREATE TABLE IF NOT EXISTS does not update an existing table design.
