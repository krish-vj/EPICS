"""
Database Configuration
"""
import os
from dotenv import load_dotenv
load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""
    
    # MySQL Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    print(f"hello \n \n {MYSQL_PASSWORD} \n \n")
    
    # SQLAlchemy Database URL
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    
    # Connection pool settings
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600

class Settings:
    """Application settings"""
    
    # API Settings
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    PROJECT_NAME = "Healthcare Management System"
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # CORS Settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # File Upload Settings
    UPLOAD_DIR = "uploads"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Create instances
db_config = DatabaseConfig()
settings = Settings()
