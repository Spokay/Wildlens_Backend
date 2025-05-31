# Application requirements

1. Python 3.12.0
2. Dependency Installation
3. Minimal Environment Variables

# Install dependencies
```bash
pip install -r requirements.txt
```

# Minimal .env file for production environment
```env
ENVIRONMENT=production
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_STORAGE_CONTAINER_NAME=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
DB_PORT=
WILDLENS_PREDICTION_API_KEY=
WILDLENS_PREDICTION_API_BASE_URL=
JWT_SECRET_KEY=[MINIMUM 32 CHARACTERS]
JWT_ALGORITHM=
JWT_EXPIRATION_MINUTES=
```

# Minimal .env file for development environment
```env
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_STORAGE_CONTAINER_NAME=
```

# Minimal .env file for testing environment
```env
ENVIRONMENT=testing
```