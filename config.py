import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'civic-ai-secret-key-2026-prod-navy')
    BASE_DIR = BASE_DIR
    
    # Detect Vercel / serverless environment
    IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    
    if IS_VERCEL:
        DATABASE_PATH = '/tmp/civic_ai.db'
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'civic_ai.db')
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
