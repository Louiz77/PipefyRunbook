from flask import Blueprint, request, send_file, jsonify, after_this_request, current_app, render_template
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
    grafana_images = [request.files[f'grafana_image_{i}'] for i in range(1, 6)]

    custom_link1 = request.form.get('custom_link1')
    custom_link2 = request.form.get('custom_link2')
    custom_link3 = request.form.get('custom_link3')

    pipefy_image_filename = secure_filename(pipefy_image.filename)
    grafana_image_paths = []
    for i in range(1, 6):
        grafana_image = request.files.get(f'grafana_image_{i}')
        if grafana_image:
            grafana_image_filename = secure_filename(grafana_image.filename)
            grafana_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], grafana_image_filename)
            grafana_image.save(grafana_image_path)
            grafana_image_paths.append(grafana_image_path)

    if not grafana_image_paths:
        return jsonify({"error": "Nenhuma imagem foi enviada."}), 400

    pipefy_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pipefy_image_filename))
    all_cards_data = pipefy_service.get_all_cards()
    cards_data = pipefy_service.get_all_cards()
    #grafana_data = grafana_service.get_grafana_data(dashboard_uid, start_date, end_date)
    #prometheus_data = prometheus_service.consultar_prometheus(start_date, end_date)

    total_abertos, total_concluidos, chamados_por_data = pipefy_service.processar_dados_pipe(all_cards_data, start_date, end_date)

    export_id = pipefy_service.export_report(303822738, 300767196)
    if "error" in export_id:
        return jsonify({"error": export_id["error"]}), 400
        pass

    report_status = pipefy_service.wait_for_report(export_id)
    if "error" in report_status:
        return jsonify({"error": report_status["error"]}), 400
        pass

    data_records = pipefy_service.download_and_process_report(export_id)
    if "error" in data_records:
        return jsonify({"error": data_records["error"]}), 400
        pass

    df = pipefy_service.download_and_process_report(export_id)
    if "error" in df:
        return jsonify({"error": df["error"]}), 400
        pass

    chamados_abertos, chamados_concluidos = pipefy_service.filter_chamados(data_records, start_date, end_date)
    top_5_solicitacoes = pipefy_service.filtrar_top_solicitacoes(data_records, start_date, end_date)
    output_file = report_utils.gerar_relatorio_completo(top_5_solicitacoes, data_records, total_abertos, total_concluidos, chamados_por_data, pipefy_image_filename, grafana_image_paths, autorResponsavel, numberVersion, cards_data, all_cards_data, start_date, end_date, custom_link1, custom_link2, custom_link3)

    try:
        return send_file(output_file, as_attachment=True, download_name="relatorio_runbook.docx")
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")
        return jsonify({"error": "Erro ao enviar o arquivo para download."}), 500
@bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    dashboard_uid = request.args.get('dashboard_uid')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not all([dashboard_uid, start_date, end_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    data = grafana_service.get_grafana_data(dashboard_uid, start_date, end_date)
    return jsonify(data)