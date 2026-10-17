import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sahakarseva-local-secure-key-2026")

    # MySQL is the primary database for SahakarSeva.
    # Local setup works out of the box for the common XAMPP/MySQL root user.
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "contractor_erp_db")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Reports folder
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reports")

    # Optional external AI credentials. The built-in assistant works without them.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROK_API_KEY = os.getenv("GROK_API_KEY", os.getenv("XAI_API_KEY", ""))
