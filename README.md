# Application mandatory requirements

1. (Installed separatly) Python 3.12.0
2. (Installed with pip) Tensorflow 2.18.0
3. (Installed separatly) ODBC Driver 18 for SQL Server

# Install dependencies
```bash
pip install -r requirements.txt
```

# Installation command of ODBC Driver 18 for SQL Server (Ubuntu)
```bash
sudo su
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
exit
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
sudo apt-get install -y unixodbc-dev
```