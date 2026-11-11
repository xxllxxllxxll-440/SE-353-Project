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

### Using MySQL Workbench

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

### Using Oracle SQL Developer

[Downloads for Oracle SQL Developer are available here.](https://www.oracle.com/database/sqldeveloper/technologies/download/)

On Linux, you will need to download the `.rpm`, extract it, then open the extracted `sqldeveloper` folder and run `./sqldeveloper.sh`

#### 1. Download MySQL Connector/J

MySQL Connector/J is the official JDBC driver that allows Java applications, including SQL Developer, to communicate with MySQL databases.

1. Visit the official [MySQL Connector/J Downloads](https://dev.mysql.com/downloads/connector/j/) page.
2. Select **Platform Independent** as the operating system.
3. Download the ZIP archive.
4. Extract the downloaded archive.
5. Locate the `.jar` file inside the extracted folder. It will be named similarly to `mysql-connector-j-9.x.x.jar`.

Keep track of where you extracted this file. You will need its location in the next step.

#### 2. Register the JDBC Driver in SQL Developer

Once the driver has been downloaded, register it with Oracle SQL Developer.

1. Open Oracle SQL Developer.
2. Navigate to **Tools → Preferences**.
3. Expand the **Database** section.
4. Select **Third Party JDBC Drivers**.
5. Click **Add Entry**.
6. Browse to the MySQL Connector/J `.jar` file downloaded in Step 1.
7. Select the file and click **Open**.
8. Click **OK** to save your changes.
9. Restart SQL Developer if necessary.

After registering the driver, SQL Developer should be able to recognize MySQL JDBC connections.

**Next Step:** Configure a connection to your Aiven MySQL server using its hostname, port, username, password, and SSL certificate.

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
