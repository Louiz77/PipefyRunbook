import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PIPEFY_API_KEY = os.getenv("PIPEFY_API_KEY")
    GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
    GRAFANA_URL = os.getenv("GRAFANA_URL")
    PROMETHEUS_URL = os.getenv("PROMETHEUS_URL")