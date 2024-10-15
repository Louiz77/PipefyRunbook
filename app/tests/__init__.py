from flask import Flask
from app.views.relatorios import bp as relatorios_bp
from app.services import pipefy_service, grafana_service, prometheus_service
import os

def create_app(test_config=None):
    # Cria o app Flask
    app = Flask(__name__, instance_relative_config=True)

    # Carrega a configuração padrão
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads')
    )

    if test_config is None:
        # Se não houver configuração de teste, carrega a configuração padrão
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Se houver configuração de teste, carrega a configuração
        app.config.from_mapping(test_config)

    # Garante que a pasta de upload exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Registra os blueprints
    app.register_blueprint(relatorios_bp)

    return app
