import pytest
from flask import Flask
from ..views.relatorios import bp as relatorios_bp

@pytest.fixture
def app():
    # Criação de uma instância do Flask para os testes
    app = Flask(__name__)
    app.register_blueprint(relatorios_bp)
    yield app

@pytest.fixture
def client(app):
    # Criação de um cliente de teste
    return app.test_client()

def test_gerar_relatorio(client):
    """
    Teste Unitario para garantir a eficiência do código
    :param client:
    :return: Response
    """
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
    assert b'relatorio_runbook.docx' in response.data  # Verifica se o nome do arquivo está no conteúdo da resposta
