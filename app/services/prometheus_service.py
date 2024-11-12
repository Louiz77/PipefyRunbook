import requests
from flask import current_app
from datetime import datetime

def consultar_prometheus(start_time, end_time, step=200):
    if isinstance(start_time, datetime): # Conversao timestamp / date
        start_time = int(start_time.timestamp())
    if isinstance(end_time, datetime):
        end_time = int(end_time.timestamp())

    prometheus_url = current_app.config['PROMETHEUS_URL']
    headers = {
        "Content-Type": "application/json"
    }
    # query para extrair dados necessarios para gerar graficos
    prometheus_queries = {
        "cpu_usage_simple": 'avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))',
        "CPU usage": "100 - (avg(irate(node_cpu_seconds_total{instance=~\"10.30.10.20:9100\",mode=\"idle\"}[5m])) * 100)",
        "CPU iowait": "avg(irate(node_cpu_seconds_total{instance=~\"10.30.10.20:9100\",mode=\"iowait\"}[5m])) * 100",
        "Memory usage": "(1 - (node_memory_MemAvailable_bytes{instance=~\"10.30.10.20:9100\"} / (node_memory_MemTotal_bytes{instance=~\"10.30.10.20:9100\"})))* 100",
        "Currently open file descriptor": "node_filefd_allocated{instance=~\"10.30.10.20:9100\"}",
        "Root partition usage": "100 - ((node_filesystem_avail_bytes{instance=~\"10.30.10.20:9100\",mountpoint=\"/\",fstype=~\"ext4|xfs\"} * 100) / node_filesystem_size_bytes {instance=~\"10.30.10.20:9100\",mountpoint=\"/\",fstype=~\"ext4|xfs\"})",
        "Maximum partition usage": "100 - ((node_filesystem_avail_bytes{instance=~\"10.30.10.20:9100\",mountpoint=\"/\",fstype=~\"ext4|xfs\"} * 100) / node_filesystem_size_bytes {instance=~\"10.30.10.20:9100\",mountpoint=\"/\",fstype=~\"ext4|xfs\"})"
    }

    results = {}

    for query_name, expr in prometheus_queries.items(): # Iniciar consultas das querys
        params = {
            'query': expr,
            'start': start_time,
            'end': end_time,
            'step': step
        }

        try:
            response = requests.get(f"{prometheus_url}/api/v1/query_range", headers=headers, params=params)

            if response.status_code != 200:
                print(f"Erro na requisição para o Prometheus: {response.status_code}, {response.text}")
                results[query_name] = {"error": f"Erro na requisição para o Prometheus: {response.status_code}, {response.text}"}
            else:
                results[query_name] = response.json()

        except Exception as e:
            results[query_name] = {"error": f"Erro ao consultar o Prometheus: {str(e)}"}

    return results

def processar_dados_prometheus(prometheus_data):
    """
    Processa os dados retornados pela consulta ao Prometheus e extrai os timestamps e valores.

    :param prometheus_data: Dados retornados pela consulta ao Prometheus
    :return: Duas listas: uma com os timestamps e outra com os valores
    """
    resultados = prometheus_data.get('data', {}).get('result', [])
    if not resultados:
        return [], []

    valores = resultados[0].get('values', [])

    timestamps = [datetime.fromtimestamp(int(val[0])) for val in valores]
    valores_medidos = [float(val[1]) for val in valores]

    return timestamps, valores_medidos