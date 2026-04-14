import os
from dotenv import load_dotenv

if os.environ.get('FLASK_ENV', 'prod') != 'prod':
    load_dotenv()

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'prod'))
