import uuid

from flask import Blueprint, request, send_file, jsonify, current_app
from ..services import pipefy_service, grafana_service, prometheus_service
from ..utils import report_utils
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

# Endpoint para gerar o relatorio / index.html envia as infos para este endpoint atraves do POST
@bp.route('/gerar', methods=['POST'])
def gerar_relatorio():
    id_user_uuid = str(uuid.uuid4())

    dashboard_uid = 'f426f015-643d-43b5-9046-15720a0ca33e' # id do dashboard do grafana
    start_date_str = request.form.get('start_date') # data selecionada na tela do formulario
    end_date_str = request.form.get('end_date') # data selecionada na tela do formulario

    # convertendo a data em um formato valido de date()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

    autorResponsavel = request.form.get('autorResponsavel') # nome do autor escrito no forms
    numberVersion = request.form.get('numberVersion') # numero da versao escrito no forms

    pipefy_image = request.files['pipefy_image'] # upload da imagem pipefy

    custom_link1 = request.form.get('custom_link1') # link do checklist diario / customizado
    custom_link2 = request.form.get('custom_link2') # link do controle de app / customizado
    custom_link3 = request.form.get('custom_link3') # link do inventario de maq / customizado

    relatorio_dev = request.files['relatorio_dev']
    if relatorio_dev:
        relatorio_dev_filename = secure_filename(str(id_user_uuid)+relatorio_dev.filename)
        relatorio_dev_path = os.path.join(current_app.config['UPLOAD_FOLDER'], relatorio_dev_filename)
        relatorio_dev.save(relatorio_dev_path)
    else:
        print('erro aq')
        return jsonify({"error": "Nenhum arquivo para append foi enviada."}), 400

    # logica para salvar as imagens para que possam ser inseridas no docx posteriormente
    pipefy_image_filename = secure_filename(pipefy_image.filename)
    grafana_image_paths = [] # upload das imagens do grafana
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

    # api para capturar dados dos cards / API DIRETA SEM LIMITE DE REQST
    all_cards_data = pipefy_service.get_all_cards()
    cards_data = pipefy_service.get_all_cards()
    total_abertos, total_concluidos, chamados_por_data = pipefy_service.processar_dados_pipe(all_cards_data, start_date,
                                                                                             end_date)

    # api do grafana e prometheus para geração dos dados dentro do relatorio
    #grafana_data = grafana_service.get_grafana_data(dashboard_uid, start_date, end_date)
    #prometheus_data = prometheus_service.consultar_prometheus(start_date, end_date)

    # API COM LIMITE DE REQUESTS / GERACAO DE SPREEDSHEETS COM OS DADOS DOS CARDS PARA FILTRO
    export_id = pipefy_service.export_report(303822738, 300767196)
    if "error" in export_id:
        return jsonify({"error": export_id["error"]}), 400
        pass

    # logica para aguardar a geração do spreedsheet finalizar para que possa continuar para as proximas etapas
    report_status = pipefy_service.wait_for_report(export_id)
    if "error" in report_status:
        return jsonify({"error": report_status["error"]}), 400
        pass

    # logica para baixar o arquivo e processar os dados apos geracao do link
    data_records = pipefy_service.download_and_process_report(export_id)
    if "error" in data_records:
        return jsonify({"error": data_records["error"]}), 400
        pass

    # processamento dos dados retornado na planilha
    chamados_abertos, chamados_concluidos = pipefy_service.filter_chamados(data_records, start_date, end_date)

    # criacao do top5 solicitacoes abertas no periodo selecionado
    top_5_solicitacoes = pipefy_service.filtrar_top_solicitacoes(data_records, start_date, end_date)

    # funcao PRINCIPAL para geracao do relatorio completo / output_file = arquivo resultado
    output_file = report_utils.gerar_relatorio_completo(id_user_uuid, top_5_solicitacoes, data_records, total_abertos, total_concluidos, chamados_por_data, pipefy_image_filename, grafana_image_paths, autorResponsavel, numberVersion, cards_data, all_cards_data, start_date, end_date, custom_link1, custom_link2, custom_link3)

    final_output_path = report_utils.append_relatorio_dev(output_file, relatorio_dev_path, id_user_uuid)
    try:
        return send_file(final_output_path, as_attachment=True, download_name="relatorio_runbook.docx")
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")
        return jsonify({"error": "Erro ao enviar o arquivo para download."}), 500