import requests
from app.views.status import all_cards
from flask import current_app
from collections import defaultdict
from collections import Counter
from datetime import datetime, timedelta
import json
import pandas as pd
from io import StringIO
from io import BytesIO
import time
import math

def wait_for_report(export_id, max_wait_time=900, poll_interval=5):
    """
    Aguarda até que o relatório esteja pronto (estado: done ou finished).

    :param export_id: O ID do relatório exportado.
    :param max_wait_time: Tempo máximo para esperar (em segundos).
    :param poll_interval: Intervalo de tempo entre os checks (em segundos).
    :return: O status final do relatório, ou erro se o tempo máximo for atingido.
    """
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        # Verificar o status do relatório
        report_status = get_report_status(export_id)

        # Verificar se o report_status é None
        if report_status is None:
            return {"error": "Failed to retrieve report status"}

        if "error" in report_status:
            return {"error": report_status["error"]}

        # Considera o relatório pronto se o estado for 'done' ou 'finished'
        if report_status['state'] in ['finished', 'done']:
            # Verificar se o link do arquivo está disponível
            if 'fileURL' in report_status:
                return report_status
            else:
                return {"error": "Report completed, but fileURL is missing."}

        print(f"Arquivo em processamento. Status atual: {report_status['state']}")
        time.sleep(poll_interval)

    return {"error": "Report generation timed out"}

def export_report(pipe_id, report_id):
    """
    Exporta um relatório EXCEL via API do Pipefy.
    """
    try:
        headers = {
            "Authorization": f"Bearer {current_app.config['PIPEFY_API_KEY']}",
            "Content-Type": "application/json"
        }

        mutation = f"""
        mutation {{
            exportPipeReport(input: {{ pipeId: {pipe_id}, pipeReportId: {report_id} }}) {{
                pipeReportExport {{
                    id
                }}
            }}
        }}
        """

        response = requests.post(
            "https://api.pipefy.com/graphql",
            json={'query': mutation},
            headers=headers
        )

        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}, Detalhes: {response.text}")
            return {"error": f"Failed report. Status: {response.status_code}"}

        try:
            report_data = response.json()
            print("Resposta da API:", report_data)

            if 'data' in report_data and 'exportPipeReport' in report_data['data']:
                export_id = report_data['data']['exportPipeReport']['pipeReportExport']['id']
                return export_id
            else:
                print("Dados não encontrados na resposta:", report_data)
                return {"error": "Invalid response"}
        except ValueError as e:
            print(f"Erro ao processar a resposta JSON: {str(e)}")
            return {"error": "Failed parse response JSON"}
    except Exception as e:
        return e

def get_report_status(export_id):
    """
    Consulta o status do relatório exportado e retorna o link para download.
    """
    headers = {
        "Authorization": f"Bearer {current_app.config['PIPEFY_API_KEY']}",
        "Content-Type": "application/json"
    }

    query = f"""
    {{
        pipeReportExport(id: {export_id}) {{
            fileURL
            state
            startedAt
            requestedBy {{
                id
            }}
        }}
    }}
    """

    response = requests.post(
        "https://api.pipefy.com/graphql",
        json={'query': query},
        headers=headers
    )

    if response.status_code == 200:
        report_status = response.json()
        return report_status['data']['pipeReportExport']
    else:
        return {"error": "Failed to retrieve report status", "status_code": response.status_code}

def download_and_process_report(export_id):
    """
    Se o status chegar como concluido, sera feito o download do arquivo e processará os dados.
    """
    report_status = get_report_status(export_id)
    if "error" in report_status:
        return {"error": report_status["error"]}

    if report_status['state'] not in ['finished', 'done']:
        return {"error": f"Report not ready, current state: {report_status['state']}"}

    if "fileURL" not in report_status:
        return {"error": "Missing file URL"}

    file_url = report_status['fileURL']
    response = requests.get(file_url)
    if response.status_code != 200:
        return {"error": "Failed to download the report file", "status_code": response.status_code}

    # leitura do arquivo para iniciar o processamento dos dados
    try:
        df = pd.read_excel(BytesIO(response.content))
    except Exception as e:
        return {"error": f"Error reading Excel file: {str(e)}"}

    df['Created at'] = pd.to_datetime(df['Created at'], errors='coerce')
    df['Finished at'] = pd.to_datetime(df['Finished at'], errors='coerce')

    return df.to_dict(orient='records')

def filter_chamados(calls_data, start_date, end_date):
    """
    Filtra e separa chamados no periodo / Abertos X Concluidos.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    chamados_abertos = []
    chamados_concluidos = []

    for call in calls_data:
        created_at = pd.to_datetime(call['Created at'], errors='coerce')
        current_phase = call.get('Current phase')

        if start_date <= created_at <= end_date:
            chamados_abertos.append(call)

        if current_phase == 'Concluído':
            chamados_concluidos.append(call)

    return chamados_abertos, chamados_concluidos

def get_all_cards():
    """
    Consulta os cards na totalidade (SEM LIMITE DE REQUESTS MAS SEM PRECISÃO).
    """
    headers = {
        "Authorization": f"Bearer {current_app.config['PIPEFY_API_KEY']}",
        "Content-Type": "application/json"
    }
    pipe_ids = [303822738]
    all_cards = []

    for pipe_id in pipe_ids:
        for phase_name in ["Concluído"]:
            has_more = True
            after = None

            while has_more:
                after_value = f'"{after}"' if after else "null"
                query = f"""
                {{
                  pipe(id: {pipe_id}) {{
                    id
                    name
                    phases {{
                      name
                      cards(first: 50, after: {after_value}) {{
                        pageInfo {{
                          hasNextPage
                          endCursor
                        }}
                        edges {{
                          node {{
                            id
                            title
                            created_at
                            due_date
                            assignees {{
                              name
                            }}
                            phases_history {{
                              phase {{
                                name
                              }}
                              duration
                            }}
                            fields {{
                              name
                              value
                            }}
                            current_phase {{
                              name
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
                """

                response = requests.post(
                    "https://api.pipefy.com/graphql",
                    json={'query': query},
                    headers=headers
                )

                if response.status_code != 200:
                    return {"error": f"Request failed with status code {response.status_code}"}

                try:
                    response_data = response.json()
                    if 'errors' in response_data:
                        return {"error": response_data['errors']}

                    pipe_data = response_data["data"]["pipe"]
                    phases = pipe_data.get("phases", [])

                    for phase in phases:
                        if phase["name"] == phase_name:
                            all_cards.extend([edge["node"] for edge in phase["cards"]["edges"]])

                            page_info = phase["cards"]["pageInfo"]
                            has_more = page_info["hasNextPage"]
                            after = page_info["endCursor"]
                            break

                except ValueError:
                    return {"error": "Erro ao processar resposta JSON"}
    return all_cards

def contar_chamados_abertos(pipe_data, start_date, end_date):
    """
    Processa quantidade total de chamados abertos.
    """
    total_abertos = 0
    chamados_por_data = defaultdict(lambda: {'abertos': 0})

    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

    for card in pipe_data:
        card_created_date = datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ")

        if start_date <= card_created_date <= end_date:
            total_abertos += 1
            chamados_por_data[card_created_date.date()]['abertos'] += 1

    return total_abertos, chamados_por_data

def contar_chamados_concluidos(pipe_data, start_date, end_date):
    """
    Processa quantidade total de chamados concluidos.
    """
    total_concluidos = 0
    chamados_por_data = defaultdict(lambda: {'concluidos': 0})

    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

    for card in pipe_data:
        phases_history = card.get('phases_history', [])

        if card.get('current_phase', {}).get('name') == 'Concluído':
            for phase in phases_history:
                if phase['phase']['name'] == 'Concluído':
                    conclusion_duration = phase.get('duration', 0)
                    card_created_date = datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    card_conclusion_date = card_created_date + timedelta(seconds=conclusion_duration)

                    if start_date <= card_conclusion_date <= end_date:
                        total_concluidos += 1
                        chamados_por_data[card_conclusion_date.date()]['concluidos'] += 1

    return total_concluidos, chamados_por_data

def processar_dados_pipe(pipe_data, start_date, end_date):
    """
    Processa dados (AbertosXConcluidos) e gera uma variavel para trabalhar com estes dados.
    """
    total_abertos, chamados_abertos_por_data = contar_chamados_abertos(pipe_data, start_date, end_date)
    total_concluidos, chamados_concluidos_por_data = contar_chamados_concluidos(pipe_data, start_date, end_date)

    return total_abertos, total_concluidos, chamados_abertos_por_data

def filtrar_top_solicitacoes(data_records, start_date, end_date):
    """
    Filtra as cinco principais solicitações abertas no período selecionado,
    excluindo valores nulos ou 'nan'.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_records = [
        record for record in data_records if start_date <= record['Created at'] <= end_date
    ]

    tipo_solicitacao_counter = Counter(
        str(record['Selecione um item']) for record in filtered_records
        if record.get('Selecione um item') and not pd.isna(record['Selecione um item'])
    )

    top_5_solicitacoes = tipo_solicitacao_counter.most_common(5)

    return top_5_solicitacoes