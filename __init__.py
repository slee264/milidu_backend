import os
from flask import Flask

from config import SECRET_KEY
def create_app(test_config=None):
    app = Flask("app")
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.from_mapping(
        SECRET_KEY = SECRET_KEY,
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    )
    
    # if test_config is None:
        
    # else:
    
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    return app