import os
import pytest
from app import create_app
from flask import Flask

@pytest.fixture
def app():
    app = create_app()  # Cria uma instância do app
    app.config['TESTING'] = True  # Habilita o modo de teste
    app.config['UPLOAD_FOLDER'] = './uploads'  # Define a pasta de upload para os testes
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Cria a pasta se não existir

    yield app  # Permite que o teste utilize o app

@pytest.fixture
def client(app):
    return app.test_client()  # Retorna um cliente de teste

def test_gerar_relatorio(client):
    # Simulação de um POST para a rota /gerar
    response = client.post('/relatorios/gerar', data={
        'start_date': '2024-10-01',
        'end_date': '2024-10-31',
        'autorResponsavel': 'Test User',
        'numberVersion': 1,
        'pipefy_image': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'grafana_image_1': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'grafana_image_2': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'grafana_image_3': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'grafana_image_4': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'grafana_image_5': (open('./app/img_itfacil.png', 'rb'), 'img_itfacil.png'),
        'custom_link1': 'http://example.com/link1',
        'custom_link2': 'http://example.com/link2',
        'custom_link3': 'http://example.com/link3'
    })

    # Verificando o status da resposta
    assert response.status_code == 200
