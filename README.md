# SE-353-Project

## Local Development Configuration

### Requirements

Required software to run this project locally:

- Python 3
- Git
- pip
- Python `venv` module

### 1. Clone Repo

This clones the repo and enters the directory:

```bash
git clone https://github.com/xxllxxllxxll-440/SE-353-Project.git
cd SE-353-Project
```

### 2. Starting the project

Documentation to start the different applications within the software package

[Flask Web Server](/app/README.md)

[SQL Backend (Windows)](/database/TeamSetupGuide.md)

[SQL Backend (Linux)](/database/LinuxTeamSetupGuide.md)

## Interacting with the MySQL Server

We recommend using MySQL Workbench for this, but the setup should be similar for Oracle SQL Developer and other clients.

[Downloads for MySQL Workbench are available here.](https://dev.mysql.com/downloads/workbench/)

Most Linux distributions have it available as a package, usually called `mysql-workbench`.

You will need to form the connection based on the provided `.env` file. Below is a table showing how the fields convert. `TLS Mode` also needs to be set to `Require and Verify CA`.

| `.env`      | MySQL Workbench       |
|-------------|-----------------------|
|`DB_USER`    |User Name              |
|`DB_HOST`    |Host Name or IP Address|
|`DB_PORT`    |Port                   |
|`DB_NAME`    |Default Schema         |
|`DB_PASSWORD`|Factor 1 Authentication|
|`DB_SSL_CA`  |CA Certificate Path    |

## While working on project

Ensure that your local copy is staying up to date:

```bash
git pull
pip install -r requirements.txt
```

Ensure you push your local copy to the repo often.

A quick guide to Git workflow is here: [Git Workflow](Doc/Git%20Workflow.md)

## Folder layout

### [/Doc](/Doc/)

Provides documents for the project, including requirements for those documents.

### [/app](/app/)

Where the Python application lives, with documentation to run it.

### [/database](/database/)

Where the server application lives, with documentation to run it.
