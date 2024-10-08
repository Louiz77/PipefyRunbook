import requests
from app.views.status import all_cards
from flask import current_app
from collections import defaultdict
from datetime import datetime, timedelta

def get_all_cards():
    headers = {
        "Authorization": f"Bearer {current_app.config['PIPEFY_API_KEY']}",
        "Content-Type": "application/json"
    }

    pipe_ids = [303822738]  # IDs dos pipes
    all_pipes_data = []  # Lista para acumular os dados de todos os pipes

    for pipe_id in pipe_ids:
        query = f"""
        {{
          pipe(id: {pipe_id}) {{
            id
            name
            phases {{
              name
              cards {{
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

            all_pipes_data.append(response_data["data"]["pipe"])

        except ValueError:
            return {"error": "JSON response erro"}

    return all_pipes_data

def get_open_cards(start_date, end_date):
    headers = {
        "Authorization": f"Bearer {current_app.config['PIPEFY_API_KEY']}",
        "Content-Type": "application/json"
    }

    pipe_ids = [304582953, 303822738]  # IDs dos pipes

    open_cards = []

    for pipe_id in pipe_ids:
        query = f"""
        {{
          pipe(id: {pipe_id}) {{
            id
            name
            phases {{
              name
              cards {{
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
            print(f"Error response: {response.text}")
            return {"error": f"Request failed with status code {response.status_code}"}

        try:
            response_data = response.json()
            if 'errors' in response_data:
                return {"error": response_data['errors']}

            pipe_name = response_data['data']['pipe']['name']
            print(f"Pipe: {pipe_name}")

            for phase in response_data['data']['pipe']['phases']:
                for card in phase['cards']['edges']:
                    card_data = card['node']
                    card_date = datetime.strptime(card_data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    if start_date <= card_date <= end_date:
                        card_data['department'] = pipe_name
                        open_cards.append(card_data)

        except ValueError:
            return {"error": "Invalid JSON response"}
    return open_cards

def contar_ocorrencias_tipo_solicitacao(cards):
    """
    Conta as ocorrências de cada valor no campo 'Escolha o tipo de solicitação'.
    """
    ocorrencias = defaultdict(int)

    for card in cards:
        tipo_solicitacao = next((field['value'] for field in card['fields'] if field['name'] == 'Escolha o tipo de solicitação'), None)
        if tipo_solicitacao:
            ocorrencias[tipo_solicitacao] += 1

    return ocorrencias

def buscar_chamados_concluidos(pipes_data, start_date, end_date):
    """
    Busca chamados concluídos dentro do período selecionado,
    mesmo que tenham sido criados em um período anterior.
    """
    total_chamados_concluidos = 0
    chamados_concluidos_por_data = defaultdict(int)

    # Converter start_date e end_date para date se forem datetime
    start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, datetime) else end_date

    for pipe in pipes_data:
        phases = pipe.get('phases', [])
        for phase in phases:
            cards = phase.get('cards', {}).get('edges', [])
            for card_edge in cards:
                card = card_edge.get('node', {})
                phases_history = card.get('phases_history', [])
                total_duration = sum(phase['duration'] for phase in phases_history)
                card_conclusion_date = (datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=total_duration)).date()

                if card.get('current_phase', {}).get('name') == 'Concluído' and start_date <= card_conclusion_date <= end_date:
                    total_chamados_concluidos += 1
                    chamados_concluidos_por_data[card_conclusion_date] += 1

    return total_chamados_concluidos, chamados_concluidos_por_data

def buscar_chamados_abertos(pipes_data, start_date, end_date):
    """
    Busca chamados abertos dentro do período selecionado.
    """
    total_chamados_abertos = 0
    chamados_abertos_por_data = defaultdict(int)

    # Converter start_date e end_date para date se forem datetime
    start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, datetime) else end_date

    for pipe in pipes_data:
        phases = pipe.get('phases', [])
        for phase in phases:
            cards = phase.get('cards', {}).get('edges', [])
            for card_edge in cards:
                card = card_edge.get('node', {})
                card_created_date = datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ").date()

                if start_date <= card_created_date <= end_date:
                    total_chamados_abertos += 1
                    chamados_abertos_por_data[card_created_date] += 1

    return total_chamados_abertos, chamados_abertos_por_data

def processar_dados_pipe(pipes_data, start_date, end_date):
    """
    Processa os dados dos pipes para calcular o total de chamados abertos e concluídos.
    """
    total_chamados_abertos = 0
    total_chamados_concluidos = 0
    chamados_por_data = defaultdict(lambda: {'abertos': 0, 'concluidos': 0})

    start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, datetime) else end_date

    for pipe in pipes_data:
        phases = pipe.get('phases', [])
        for phase in phases:
            cards = phase.get('cards', {}).get('edges', [])
            print(cards)
            for card_edge in cards:
                card = card_edge.get('node', {})
                phases_history = card.get('phases_history', [])
                total_duration = sum(phase['duration'] for phase in phases_history)
                card_conclusion_date = (datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(
                    seconds=total_duration)).date()

                if card.get('current_phase', {}).get(
                        'name') == 'Concluído' and start_date <= card_conclusion_date <= end_date:
                    total_chamados_concluidos += 1
                    chamados_concluidos_por_data[card_conclusion_date] += 1


    for pipe_data in pipes_data:
        if not isinstance(pipe_data, dict) or 'phases' not in pipe_data:
            print("Erro: Dados do pipe não contêm o formato esperado.")
            continue

        phases = pipe_data.get('phases', [])
        for phase in phases:
            cards = phase.get('cards', {}).get('edges', [])
            for card_edge in cards:
                card = card_edge.get('node', {})
                card_created_date = datetime.strptime(card['created_at'],
                                                      "%Y-%m-%dT%H:%M:%SZ").date()
                if start_date <= card_created_date <= end_date:
                    total_chamados_abertos += 1
                    chamados_por_data[card_created_date]['abertos'] += 1
                phases_history = card.get('phases_history', [])
                total_duration = sum(phase_hist.get('duration', 0) for phase_hist in phases_history)
                card_conclusion_date = (datetime.combine(card_created_date, datetime.min.time()) + timedelta(seconds=total_duration)).date()
                if (card.get('current_phase', {}).get('name') == 'Concluído'):
                    total_chamados_concluidos += 1
                    chamados_por_data[card_conclusion_date]['concluidos'] += 1

    return total_chamados_abertos, total_chamados_concluidos, chamados_por_data