# Application requirements

1. Python 3.12.0
2. Dependency Installation
3. Minimal Environment Variables

# Install dependencies
```bash
pip install -r requirements.txt
```

# Run Backend
```bash
fastapi dev ./app/main.py --port 8001 --host 0.0.0.0
```

# Minimal .env file necessary to launch the backend
```env
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_STORAGE_CONTAINER_NAME=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
DB_PORT=
JWT_SECRET_KEY=
JWT_ALGORITHM=
JWT_EXPIRATION_MINUTES=
```