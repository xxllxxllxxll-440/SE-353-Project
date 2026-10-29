# Sixty-Three Social

## Team setup guide: Linux (Debian and Arch)

This guide covers the database starter code on Linux. The commands are
intended for both Debian-based systems (such as Debian 13) and Arch
Linux. Package installation differs by distribution; Git, Python virtual
environments, the project code, and the Aiven connection workflow are
otherwise similar.

This is a team setup guide, not documentation for a finished website.

## 1. What is included

| File or folder | What it does |
|---|---|
| `database/app/01_create_database.sql` | Creates tables, relationships, and two views. |
| `database/app/02_sample_data.sql` | Adds fictional restaurant data for testing. |
| `database/app/03_test_queries.sql` | Checks inventory, vendors, and financial totals. |
| `database/app/database.py` | Connects Python to MySQL; provides inventory, purchase, and report functions. |
| `database/app/test_database_logic.py` | Small offline tests for purchase logic. |
| `database/app/.env.example` | Template for local database settings; contains no password. |
| `requirements.txt` | Python dependencies for the project. |

Paths above assume `requirements.txt` is in the repository root and the
SQL/Python files are in `database/app/`. If your checkout differs, use
the paths shown by `find` in section 3.

## 2. Get the project from GitHub

1.  Accept the private repository invitation from the repository owner.
2.  Copy the repository's HTTPS or SSH clone URL from GitHub.
3.  Clone it from a terminal:

``` bash
git clone YOUR_REPOSITORY_URL
cd Sixty-Three-Social
```

Replace `YOUR_REPOSITORY_URL` and the directory name with the actual URL
and cloned folder name.

For code changes, make a branch and push it to GitHub:

``` bash
git switch -c my-feature
git status
```

After making and testing changes:

``` bash
git add path/to/changed-file
git commit -m "Describe the change"
git push -u origin my-feature
```

Replace the example branch and file path with your own. Open a pull
request on GitHub so the group can review the change before it is merged
into `main`.

## 3. Install Linux prerequisites

### Debian / Ubuntu

``` bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

### Arch Linux

``` bash
sudo pacman -Syu
sudo pacman -S --needed git python python-pip
```

A MySQL command-line client or database GUI is optional. You can use a
GUI such as DBeaver if you prefer to inspect SQL results visually; it is
not required to run the Python code.

Check the checkout's layout from the repository root:

``` bash
find . -maxdepth 3 \( \
  -name requirements.txt -o \
  -name .env.example -o \
  -name database.py -o \
  -name test_database_logic.py -o \
  -name '03_test_queries.sql' \
\) -print
```

## 4. Create the Python environment and install dependencies

Run these commands from the repository root, where `requirements.txt` is
located:

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Use `python -m pip`, not a bare system `pip`, so packages install into
the project's virtual environment. Debian may block system-wide pip
installs under PEP 668; do not work around that by using `sudo pip` or
`--break-system-packages`.

You can also invoke the environment directly without activating it:

``` bash
./.venv/bin/python -m pip install -r requirements.txt
```

Verify that Python and pip come from `.venv`:

``` bash
which python
which pip
python -m pip --version
```

The reported paths should contain the repository's `.venv/bin/`
directory.

## 5. Configure Aiven credentials and SSL

Ask for permission to use the team's Aiven MySQL service. Use an
individual database login if the service supports it. Share credentials
privately, never through GitHub.

Copy the template into the app directory:

``` bash
cp database/app/.env.example database/app/.env
```

Download the Aiven CA certificate and place it in the same directory as
`.env` and `database.py`:

``` text
database/app/.env
database/app/ca.pem
database/app/database.py
```

Edit `database/app/.env` and enter your own connection details:

``` dotenv
DB_HOST=your-service-hostname
DB_PORT=your-service-port
DB_USER=your-database-username
DB_PASSWORD=your-private-password
DB_NAME=restaurant_project
DB_SSL_CA=ca.pem
```

Use the actual values supplied by Aiven/the team. Do not copy these
placeholders literally.

**Important about the certificate path:** `DB_SSL_CA=ca.pem` is a
relative path. It only works if `database.py` resolves it relative to
the app directory or the process happens to run from that directory. The
robust approach in `database.py` is to resolve it relative to the
`.env`/script directory, for example:

``` python
from pathlib import Path
import os
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")

DB_SSL_CA = str(APP_DIR / os.environ.get("DB_SSL_CA", "ca.pem"))
```

Use the resolved `DB_SSL_CA` in the existing MySQL connection code.
Avoid loading `.env` from multiple places if the file already has a
configuration-loading section; adapt that section instead of duplicating
it. Keep certificate verification enabled.

Protect the secrets:

``` bash
chmod 600 database/app/.env database/app/ca.pem
```

Confirm Git ignores them:

``` bash
git check-ignore -v database/app/.env database/app/ca.pem
git status --short
```

The first command should show ignore rules for both files. If it does
not, add suitable entries to `.gitignore` before committing anything,
for example:

``` gitignore
.env
*.pem
```

Only use `*.pem` if the repository does not intentionally track any PEM
files. Never commit `.env`, `ca.pem`, or passwords.

## 6. Check the Aiven connection

Run from the repository root:

``` bash
./.venv/bin/python -c "import sys; print(sys.executable)"
```

Then change to the app directory and run the connection check:

``` bash
cd database/app
../../.venv/bin/python -c "import database; print(database.connection_check())"
```

Expected output includes the active database name and MySQL version, for
example:

``` text
{'database_name': 'restaurant_project', 'mysql_version': '8.4.11'}
```

The exact MySQL version may differ. This confirms the Python connection
works; it does not test the entire website.

## 7. Run the offline unit tests

From `database/app`:

``` bash
../../.venv/bin/python -m unittest -v test_database_logic.py
```

These tests use fake database connections. They check purchase
calculations and rollback behavior, but do not prove that the live Aiven
database works.

## 8. Run `03_test_queries.sql` against Aiven

First inspect the script:

``` bash
less 03_test_queries.sql
```

Use `q` to exit `less`. Confirm that the script contains the intended
checks. Do not run schema changes or data-modifying statements against
the shared database without agreement from Julius.

### Option A: Use a database GUI

Use a compatible client such as DBeaver, create a MySQL connection with
the actual Aiven host, port, username, database, and SSL CA certificate,
then open `03_test_queries.sql` and execute the intended queries. Keep
certificate verification enabled.

### Option B: Use the project's Python connector and `.env`

From `database/app`, run this temporary script. It loads the same `.env`
settings used by the application, reads the SQL file, executes its
statements, and prints result rows. It assumes the test file contains
ordinary SQL statements separated by semicolons, not stored-procedure
definitions or semicolons inside string literals.

``` bash
../../.venv/bin/python - <<'PY'
from pathlib import Path
import os

import mysql.connector
from dotenv import load_dotenv

app_dir = Path(__file__).resolve().parent
load_dotenv(app_dir / ".env")

ca_value = os.environ.get("DB_SSL_CA", "ca.pem")
ca_path = Path(ca_value)
if not ca_path.is_absolute():
    ca_path = app_dir / ca_path

sql_path = app_dir / "03_test_queries.sql"
sql_text = sql_path.read_text(encoding="utf-8")

connection = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ.get("DB_NAME", "restaurant_project"),
    ssl_ca=str(ca_path),
    ssl_verify_cert=True,
)

try:
    cursor = connection.cursor()
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]

    for number, statement in enumerate(statements, start=1):
        print(f"\n--- Query {number} ---")
        cursor.execute(statement)

        if cursor.with_rows:
            for row in cursor.fetchall():
                print(row)
            if cursor.with_rows and cursor.description:
                print(f"(columns: {', '.join(column[0] for column in cursor.description)})")
        else:
            print(f"Statement completed. Rows affected: {cursor.rowcount}")
finally:
    cursor.close()
    connection.close()
PY
```

If the script uses SQL syntax with semicolons inside strings or stored
procedures, do not use this simple splitter. Use a database GUI or a
client that supports running SQL scripts instead. This runner does not
commit purchases or intentionally modify data, but always inspect the
SQL file before executing it.

On a fresh sample database, the guide expects 9 tables, 2 views, 4
inventory items, and 3 vendors. Existing shared data may produce
different totals.

## 9. How the application will use this

-   Julius maintains the MySQL tables, sample data, Python database
    functions, and financial queries.
-   Cole connects `database.py` to the Flask backend and handles
    application routes and access checks.
-   Jorden builds the HTML/CSS interface and connects it to backend
    routes. Browser code must not contain the database password.

Example: the frontend asks the backend for an inventory list. The
backend calls `inventory()` in `database.py`, which reads the MySQL
tables. The browser does not connect directly to Aiven.

## 10. What is complete and what is not

| Included in this starter | Still to be developed |
|---|---|
| Database tables and sample records | Full website/dashboard |
| Inventory, vendor, purchase, and report functions | User login and role permissions |
| Low-stock database view | Routes connecting pages to Python |
| Offline tests and SQL check queries | Exporting/printing and deployment |

The financial report is a basic comparison of recorded revenue and
expenses. It is not a full accounting system. Purchase costs already
appear in the expenses table, so do not count them a second time.

## 11. Common setup problems

| Problem | What to check |
|---|---|
| `externally-managed-environment` | Activate `.venv` and use `python -m pip`, not system pip. |
| `No module named mysql` | Install dependencies inside `.venv` with `python -m pip install -r requirements.txt`. |
| Access denied | Confirm Aiven username, password, and permissions. |
| Unknown database / missing tables | Check the service and run the schema script only if appropriate. |
| SSL certificate error | Confirm `DB_SSL_CA` resolves to the correct CA file and certificate verification remains enabled. |
| Python import error | Run from `database/app` or use the commands above with the correct paths. |
| Different totals from the guide | Another teammate may already have changed the shared data. |

## 12. Before submitting

-   Verify the code runs on at least one teammate's computer, ideally
    both Debian and Arch.
-   Make sure `.env`, `ca.pem`, and passwords are not staged or tracked
    by Git.
-   Record actual test results; do not report a test as passed unless
    someone ran it.
-   Confirm the repository is private and teammates can clone it.
-   Add website files as the team builds them. This folder is the
    database portion only.

If a table changes, tell the group before rerunning setup scripts.
`CREATE TABLE IF NOT EXISTS` does not update an existing table design.
