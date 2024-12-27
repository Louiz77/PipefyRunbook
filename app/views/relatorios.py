from flask import Blueprint, request, send_file, jsonify, current_app
from ..services import pipefy_service
from ..utils import report_utils
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
from threading import Thread

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

relatorio_status = {}

@bp.route('/gerar', methods=['POST'])
def gerar_relatorio():
    # Identificador único para cada usuário/relatório
    id_user_uuid = str(uuid.uuid4())

    # Parâmetros de entrada
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
    autorResponsavel = request.form.get('autorResponsavel')
    numberVersion = request.form.get('numberVersion')

    pipefy_image = request.files['pipefy_image']  # upload da imagem pipefy

    # Links customizados
    custom_link1 = request.form.get('custom_link1')
    custom_link2 = request.form.get('custom_link2')
    custom_link3 = request.form.get('custom_link3')

    # lógica para salvar as imagens para que possam ser inseridas no docx posteriormente
    pipefy_image_filename = secure_filename(f"{id_user_uuid}_{pipefy_image.filename}")
    pipefy_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pipefy_image_filename)
    pipefy_image.save(pipefy_image_path)

    grafana_image_paths = []  # upload das imagens do grafana
    for i in range(1, 6):
        grafana_image = request.files.get(f'grafana_image_{i}')
        if grafana_image:
            grafana_image_filename = secure_filename(grafana_image.filename)
            grafana_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], grafana_image_filename)
            grafana_image.save(grafana_image_path)
            grafana_image_paths.append(grafana_image_path)

    if not grafana_image_paths:
        return jsonify({"error": "Nenhuma imagem foi enviada."}), 400

    # Documento relatorio_dev
    relatorio_dev_path = None
    relatorio_dev = request.files.get('relatorio_dev')
    if relatorio_dev:
        relatorio_dev_filename = secure_filename(f"{id_user_uuid}_{relatorio_dev.filename}")
        relatorio_dev_path = os.path.join(current_app.config['UPLOAD_FOLDER'], relatorio_dev_filename)
        relatorio_dev.save(relatorio_dev_path)

    # API para capturar dados dos cards / API DIRETA SEM LIMITE DE REQST
    all_cards_data = pipefy_service.get_all_cards()
    cards_data = pipefy_service.get_all_cards()
    total_abertos, total_concluidos, chamados_por_data = pipefy_service.processar_dados_pipe(all_cards_data, start_date, end_date)

    # API COM LIMITE DE REQUESTS / GERACAO DE SPREEDSHEETS COM OS DADOS DOS CARDS PARA FILTRO
    export_id = pipefy_service.export_report(303822738, 300767196)
    if "error" in export_id:
        return jsonify({"error": export_id["error"]}), 400

    # Aguarda a geração do spreadsheet
    report_status = pipefy_service.wait_for_report(export_id)
    if "error" in report_status:
        return jsonify({"error": report_status["error"]}), 400

    # Processa os dados do spreadsheet gerado
    data_records = pipefy_service.download_and_process_report(export_id)
    if "error" in data_records:
        return jsonify({"error": data_records["error"]}), 400

    # Processamento dos dados
    print("Iniciou processamento dos dados (chamados_abertos, chamados_concluidos")
    chamados_abertos, chamados_concluidos = pipefy_service.filter_chamados(data_records, start_date, end_date)
    print("Finalizou processamento dos dados")
    print("Iniciou processamento dos dados (top_5_solicitacoes")
    top_5_solicitacoes = pipefy_service.filtrar_top_solicitacoes(data_records, start_date, end_date)
    print("Finalizou processamento dos dados")

    # Parâmetros para geração do relatório
    print("Inicializacao dos params")
    params = {
        "top_5_solicitacoes": top_5_solicitacoes,
        "data_records": data_records,
        "id_user_uuid": id_user_uuid,
        "total_abertos": total_abertos,
        "total_concluidos": total_concluidos,
        "chamados_por_data": chamados_por_data,
        "cards_data": cards_data,
        "start_date": start_date,
        "end_date": end_date,
        "all_cards_data": all_cards_data,
        "autorResponsavel": autorResponsavel,
        "numberVersion": numberVersion,
        "pipefy_image": pipefy_image_path,
        "grafana_image_paths": grafana_image_paths,
        "custom_link1": custom_link1,
        "custom_link2": custom_link2,
        "custom_link3": custom_link3,
        "relatorio_dev_path": relatorio_dev_path
    }
    for x in params:
        print(type(x))
    print("Inicializacao do caminho do arquivo de saida")

    relatorio_status[id_user_uuid] = {"status": "processando"}

    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"relatorio_{id_user_uuid}.docx")

    print("Inicializacao do thread")
    try:
        # Inicia a thread para geração do relatório
        Thread(target=gerar_relatorio_thread, args=[current_app.app_context(), params, output_path]).start()
    except Exception as e:
        print(e)

    return jsonify({
        "status": "Relatório em processamento",
        "report_id": id_user_uuid,
        "download_url": f"/relatorios/download/{id_user_uuid}"
    })

def gerar_relatorio_thread(app_context, params, output_path):
    try:
        print("Iniciou GERAR_RELATORIO_THREAD")
        app_context.push()
        print("Alterando contexto para app_context")

        final_output_path = report_utils.gerar_relatorio_completo(
            id_user_uuid=params["id_user_uuid"],
            top_5_solicitacoes=params["top_5_solicitacoes"],
            data_records=params["data_records"],
            total_abertos=params["total_abertos"],
            total_concluidos=params["total_concluidos"],
            chamados_por_data=params["chamados_por_data"],
            pipefy_image=params["pipefy_image"],
            grafana_image_paths=params["grafana_image_paths"],
            autorResponsavel=params["autorResponsavel"],
            numberVersion=params["numberVersion"],
            all_cards_data=params["all_cards_data"],
            cards_data=params["cards_data"],
            start_date=params["start_date"],
            end_date=params["end_date"],
            custom_link1=params["custom_link1"],
            custom_link2=params["custom_link2"],
            custom_link3=params["custom_link3"],
            relatorio_dev_path=params["relatorio_dev_path"],
            output_file=output_path
        )

        # Realiza o append do arquivo `relatorio_dev` ao final do relatório gerado
        final_output_path = report_utils.append_relatorio_dev(
            final_output_path, params["relatorio_dev_path"], params["id_user_uuid"]
        )

        relatorio_status[params["id_user_uuid"]] = {
            "status": "pronto",
            "file_path": os.path.abspath(final_output_path),
            "download_url": (f"http://10.5.9.45:8530/relatorios/download/{params['id_user_uuid']}")
        }
        print("Finalizou GERAR_RELATORIO_THREAD")
        print(relatorio_status)
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        relatorio_status[params["id_user_uuid"]] = {
            "status": "erro",
            "message": str(e)
        }

@bp.route('/status/<report_id>', methods=['GET'])
def status_relatorio(report_id):
    status_info = relatorio_status.get(report_id)
    if not status_info:
        return jsonify({"status": "não encontrado"}), 404

    if status_info["status"] == "pronto":
        status_info["download_url"] = f"http://localhost:8530/relatorios/download/{report_id}"

    return jsonify(status_info)

@bp.route('/download/<report_id>', methods=['GET'])
def download_relatorio(report_id):
    status_info = relatorio_status.get(report_id)
    if not status_info:
        return jsonify({"error": "Relatório não encontrado"}), 404

    if status_info["status"] != "pronto":
        return jsonify({"error": "Relatório ainda não está pronto"}), 400

    file_path = status_info["file_path"]

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")
        return jsonify({"error": "Erro ao enviar o arquivo"}), 500