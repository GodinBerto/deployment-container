class Config:
    SECRET_KEY = 'your_secret_key'
    JWT_SECRET_KEY = 'your_jwt_secret_key'
    DATABASE_PATH = ""
    API_VERSION = 'v1'
    BASE_URL = f'api/{API_VERSION}'
    
    # Email configuration
    SENDER_EMAIL = 'godfredquarm123@gmail.com'  # Update with your email
    SENDER_PASSWORD = 'evncrhlyjlhyfmze'  # Use Gmail App Password for Gmail
