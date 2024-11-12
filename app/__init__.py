from flask import Flask
from config import Config
import os
from flask_cors import CORS

# Inicializar as blueprints do flask
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    # Carregar os arquivos de upload do usuario
    app.config['UPLOAD_FOLDER'] = './uploads'

    if not os.path.exists(app.config['UPLOAD_FOLDER']): # Cria a pasta se nao houver
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .views import main, relatorios, status
    app.register_blueprint(main.bp)
    app.register_blueprint(relatorios.bp)
    app.register_blueprint(status.bp)

    return app