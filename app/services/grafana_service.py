import requests
from flask import current_app

def get_grafana_data(dashboard_uid, start_date, end_date):
    """
    Função para buscar dados do Grafana no intervalo de tempo especificado.
    """
    grafana_url = f"{current_app.config['GRAFANA_URL']}/api/dashboards/uid/{dashboard_uid}"
    headers = {
        "Authorization": f"Bearer {current_app.config['GRAFANA_API_KEY']}",
        "Content-Type": "application/json"
    }

    params = {
        "from": start_date,
        "to": end_date
    }

    try:
        response = requests.get(grafana_url, headers=headers, params=params)

        if response.status_code != 200:
            return {"error": f"Request failed with status code {response.status_code}"}

        grafana_data = response.json()
        return grafana_data # resultado dos dados obtidos

    except ValueError:
        return {"error": "Invalid JSON response"}
    except Exception as e:
        return {"error": str(e)}