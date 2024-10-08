from flask import Blueprint, request, send_file, jsonify, after_this_request, current_app
from ..services import pipefy_service, grafana_service, prometheus_service
from ..utils import report_utils
from werkzeug.utils import secure_filename
from datetime import datetime
import os

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

@bp.route('/gerar', methods=['POST'])
def gerar_relatorio():
    dashboard_uid = 'f426f015-643d-43b5-9046-15720a0ca33e'
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

    autorResponsavel = request.form.get('autorResponsavel')
    numberVersion = request.form.get('numberVersion')

    pipefy_image = request.files['pipefy_image']
    grafana_image = request.files['grafana_image']
    totvs_image = request.files['totvs_image']

    pipefy_image_filename = secure_filename(pipefy_image.filename)
    grafana_image_filename = secure_filename(grafana_image.filename)
    totvs_image_filename = secure_filename(totvs_image.filename)

    pipefy_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pipefy_image_filename))
    grafana_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], grafana_image_filename))
    totvs_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], totvs_image_filename))

    # Coletar dados das APIs (Pipefy, Grafana e Prometheus)
    all_cards_data = pipefy_service.get_all_cards()
    cards_data = pipefy_service.get_open_cards(start_date, end_date)
    #grafana_data = grafana_service.get_grafana_data(dashboard_uid, start_date, end_date)
    #prometheus_data = prometheus_service.consultar_prometheus(start_date, end_date)

    total_abertos, total_concluidos, chamados_por_data = pipefy_service.processar_dados_pipe(all_cards_data, start_date, end_date)

    # Gera o relatório completo usando report_utils
    output_file = report_utils.gerar_relatorio_completo(total_abertos, total_concluidos, chamados_por_data, pipefy_image_filename, grafana_image_filename, totvs_image_filename, autorResponsavel, numberVersion, cards_data, all_cards_data, start_date, end_date)

    return send_file(output_file, as_attachment=True, download_name="relatorio_runbook.docx")


@bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    dashboard_uid = request.args.get('dashboard_uid')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not all([dashboard_uid, start_date, end_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    data = grafana_service.get_grafana_data(dashboard_uid, start_date, end_date)
    return jsonify(data)