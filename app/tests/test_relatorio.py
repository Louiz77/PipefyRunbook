import pytest
from unittest.mock import patch
from app import create_app
from datetime import datetime

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

@patch('app.services.pipefy_service.get_all_cards')
@patch('app.services.pipefy_service.export_report')
@patch('app.services.pipefy_service.wait_for_report')
@patch('app.services.pipefy_service.download_and_process_report')
@patch('app.services.pipefy_service.filter_chamados')
@patch('app.services.pipefy_service.filtrar_top_solicitacoes')
def test_gerar_relatorio(mock_filtrar_top_solicitacoes, mock_filter_chamados, mock_download_and_process_report,
                         mock_wait_for_report, mock_export_report, mock_get_all_cards, client):
    # Simula o retorno da função get_all_cards
    mock_get_all_cards.return_value = [
        {
            'created_at': '2024-10-01T12:00:00Z',
            'title': 'Chamado 1',
            'current_phase': {'name': 'Concluído'}
        },
        {
            'created_at': '2024-10-02T12:00:00Z',
            'title': 'Chamado 2',
            'current_phase': {'name': 'Em Andamento'}
        }
    ]

    # Simula o retorno da função export_report
    mock_export_report.return_value = {'id': 'mock_export_id'}

    # Simula o retorno da função wait_for_report
    mock_wait_for_report.return_value = {'status': 'completed'}

    # Simula o retorno da função download_and_process_report com a chave 'Created at' como objeto datetime
    mock_download_and_process_report.return_value = [
        {'Created at': datetime(2024, 10, 1, 12, 0, 0), 'Finished at': datetime(2024, 10, 5, 12, 0, 0), 'title': 'Chamado 1'},
        {'Created at': datetime(2024, 10, 2, 12, 0, 0), 'Finished at': datetime(2024, 10, 6, 12, 0, 0), 'title': 'Chamado 2'}
    ]

    # Simula o retorno da função filter_chamados
    mock_filter_chamados.return_value = (1, 1)  # Total de chamados abertos e concluídos

    # Simula o retorno da função filtrar_top_solicitacoes
    mock_filtrar_top_solicitacoes.return_value = [
        {'type': 'Incidente', 'count': 1},
        {'type': 'Solicitação de Serviço', 'count': 1}
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

    # Verificando se o cabeçalho 'Content-Disposition' contém o nome do arquivo correto
    assert 'relatorio_runbook.docx' in response.headers['Content-Disposition']

    # Verificando o tipo de conteúdo para garantir que seja um arquivo Word
    assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
