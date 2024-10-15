import os
import pytest
from flask import Flask
from app import create_app
from unittest.mock import patch


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = './uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@patch('app.services.pipefy_service.get_all_cards')  # Mocking the function
def test_gerar_relatorio(mock_get_all_cards, client):
    # Simula o retorno da função get_all_cards
    mock_get_all_cards.return_value = [
        {
            'created_at': '2024-10-01T12:00:00Z',
            'title': 'Chamado 1',
            'current_phase': 'Concluído'
        },
        {
            'created_at': '2024-10-02T12:00:00Z',
            'title': 'Chamado 2',
            'current_phase': 'Em Andamento'
        }
    ]

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
