from flask import Flask
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = './uploads'

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .views import main, relatorios, status
    app.register_blueprint(main.bp)
    app.register_blueprint(relatorios.bp)
    app.register_blueprint(status.bp)

    return app