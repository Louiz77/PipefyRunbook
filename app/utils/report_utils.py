from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION_START
import docx
from datetime import datetime, timedelta
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from io import BytesIO
import io
import plotly.graph_objects as go
import base64
from flask import current_app

def gerar_relatorio_completo(total_abertos, total_concluidos, chamados_por_data, pipefy_image, grafana_image, totvs_image, autorResponsavel, numberVersion, cards_data, all_cards_data, start_date, end_date):
    """
    Gera o relatório completo diretamente pelo código, com base nas informações do Pipefy, Grafana e Prometheus.
    """
    doc = Document()

    # Inicial
    print("Processo de geração pagina inicial - INICIADO")
    gerar_pagina_inicial(doc, start_date, end_date)

    # 1. Sumário
    doc.add_heading('Relatório Gerencial Mensal', 0)
    doc.add_paragraph('Sumário:')
    doc.add_paragraph('1. Objetivo')
    doc.add_paragraph('2. Relatório Mensal')
    doc.add_paragraph('3. Run Book')
    doc.add_paragraph('4. Relatório Gerencial Informativo')
    doc.add_paragraph('5. Volumetria e Nível de Serviço')
    doc.add_paragraph('6. Controle do Documento')
    doc.add_paragraph('7. SLA Solução')
    doc.add_paragraph('8. Histórico de Versões')
    doc.add_paragraph('9. Fatos Relevantes')
    doc.add_paragraph('10. Gestão de Serviços')
    doc.add_paragraph('11. Relatório de Chamados')
    doc.add_paragraph('12. Classificação dos Incidentes')

    # 2. Objetivo
    doc.add_heading('Objetivo', level=1)
    doc.add_paragraph(
        'Mensalmente, será apresentado o relatório “Run-Book” contendo as informações baseadas na operação dos últimos 30 dias, com as seguintes informações, porém não limitado a:')

    doc.add_paragraph(
        '''
        • Relatório de incidentes ocorrido no período anterior contendo a classificação dos incidentes e SLA atingido
        • Descritivo e tratativa dos incidentes críticos ocorridos no período anterior. 
        • Informativo a respeito dos itens de segurança da informação como a atualização de patchs de segurança e hotfixes. 
        • Resumo dos recursos computacionais utilizados contendo % de consumo – capacidade do ambiente computacional. 
        • Resumo da saúde dos elementos tecnológicos fornecidos nesta solução. 
        • Resumo dos alertas gerados pelo sistema de monitoramento para todos os elementos tecnológicos fornecidos pela ITFácil. 
        • Indicativo de risco e recomendação de tomada de ação 
        • Relatório sobre inventário do parque e acompanhamento da vida útil.'''
    )

    doc.add_paragraph(
        'Adicionalmente ao Run-Book mensal, a ITfácil poderá fornecer a pedido do cliente'
    )

    doc.add_paragraph(
        '''
        • Relatório check-list de execução de rotina de backup diário 
        • Relatório check-list de execução de replicação do site Disaster Recovery diário 
        • Check-list operacional a respeito do funcionamento da infraestrutura e sistemas diário 
        • Relatórios de auditoria (conforme demanda)
        '''
    )

    doc.add_heading('SLA - Solução', level=1)
    doc.add_picture('./app/sla_padrao.jpg')


    doc.add_heading('Histórico de versões', level=1)
    gerar_historico_versoes(doc, autorResponsavel, numberVersion)

    doc.add_heading('Fatos relevantes', level=1)
    gerar_relatorio_chamados(doc, all_cards_data, start_date, end_date)
    gerar_chamados_por_departamento(doc, cards_data)

    doc.add_heading('Gestão de Serviços', level=1)
    doc.add_paragraph('Foi implantado a Gestão de projetos na Ecom, utilizando a ferramenta do Pipefy, com a criação de vários controles que podem ser gerenciados pela equipe Ecom e Itfácil em conjunto, essa ferramenta trouxe mais transparências nas atividades, registro dos passos e evidências além de criar uma base de conhecimento que pode ser consultada a qualquer momento.')
    if pipefy_image:
        doc.add_picture(os.path.join(current_app.config['UPLOAD_FOLDER'], pipefy_image), width=Inches(4.0))
    p = doc.add_paragraph('Acesse o quadro Pipefy aqui: ')
    add_hyperlink(p, 'https://app.pipefy.com/pipes/304582953', 'Quadro - Ecom - Tarefas ITFacil Equipe - Pipefy')

    doc.add_paragraph('3. Chamados por classificação')
    gerar_classificacao_incidentes(doc, cards_data)

    doc.add_heading('Resumo dos recursos computacionais utilizados contendo % de consumo – capacidade do ambiente computacional.', level=1)
    doc.add_paragraph('Considerando a topologia no ambiente Ecom / Cirion –abaixo, esta em desenvolvimento o  monitoramento com a capacidade de listar os % de consumo dos Host por períodos, promovendo as seguintes informações:')
    if grafana_image:
        doc.add_picture(os.path.join(current_app.config['UPLOAD_FOLDER'], grafana_image), width=Inches(4.0))
    #gerar_relatorio_com_dados_prometheus(doc, prometheus_data)
    #gerar_relatorio_com_dados_grafana(doc, grafana_data)

    doc.add_heading('Check-list operacional a respeito do funcionamento da infraestrutura e sistemas diário', level=1)
    p = doc.add_paragraph('Disponível no diretório: ')
    add_hyperlink(p, 'https://ecom742.sharepoint.com/sites/WorkPlace-IT/Documentos Compartilhados/General/TI.INVENTÁRIO/RUNBOOK/Julho/CHECKLISTS', 'Lista de Check List - Diario')

    doc.add_paragraph('Esta disponível o manual do check-list atualizado, com o processo passo-a-passo e um arquivo zip com todos os check list realizados inclusive com as observações e ocorrências.')

    doc.add_heading('Backup Cirion, acompanhamento diário', level=1)
    doc.add_paragraph('O backup é realizado junto ao checklist diário.')

    doc.add_heading('Controle de aplicativos instalados')
    p = doc.add_paragraph('Disponível no diretório:')
    add_hyperlink(p, '../Ecom%20Energia/WorkSPace%20-%20IT%20-%20General/TI.INVENTÁRIO/RUNBOOK/Agosto/Programas%20Instalados.xlsx', 'Controle de Aplicativos e Sistemas Instalados')

    doc.add_heading('O Sistema GLPI e o Kaspersky fazem a gestão dos ativos controalndo a parte física e lógica de todos os equipamentos')
    doc.add_paragraph('A lista completa, bem como o inventário por equipamentos poderá ser acompanhado e gerenciado diretamente no GLPI ou Kaspersky')
    p = doc.add_paragraph('Relatório completo está disponível em: ')
    add_hyperlink(p, '../Ecom%20Energia/WorkSPace%20-%20IT%20-%20General/TI.INVENTÁRIO/RUNBOOK/Agosto/Inventário%20GLPI.xlsx', 'Inventario de Maquinas - GLPI')

    doc.add_heading('Chamados Referente a TOTVS', level=1)
    if totvs_image:
        doc.add_picture(os.path.join(current_app.config['UPLOAD_FOLDER'], totvs_image), width=Inches(4.0))

    output_file = os.path.join(os.getcwd(), 'relatorio_runbook.docx')
    doc.save(output_file)

    return output_file

def gerar_chamados_por_departamento(doc, cards):
    """
    Gera a seção 'Chamados por Departamento' com gráfico de pizza.
    """
    doc.add_paragraph('2. Chamados por departamento')

    chamados_por_departamento = defaultdict(int)

    for card in cards:
        department = card.get('department')
        if department:
            chamados_por_departamento[department] += 1

    if chamados_por_departamento:
        for department, count in chamados_por_departamento.items():
            doc.add_paragraph(f'Chamados abertos para {department}: {count} chamado(s)')

        grafico_pizza_url = gerar_grafico_pizza2(chamados_por_departamento)
        if grafico_pizza_url:
            img_stream = io.BytesIO(base64.b64decode(grafico_pizza_url))
            doc.add_picture(img_stream, width=Inches(4.5))
    else:
        doc.add_paragraph("Nenhum chamado encontrado para os departamentos.")


def gerar_classificacao_incidentes(doc, cards):
    """
    Gera a seção 'Classificação dos Incidentes'.
    """
    doc.add_paragraph('Classificação dos Incidentes:')
    tipos_solicitacao = {}

    for card in cards:
        tipo_solicitacao = next(
            (field['value'] for field in card['fields'] if field['name'] == 'Escolha o tipo de solicitação'), None)
        if tipo_solicitacao:
            tipos_solicitacao[tipo_solicitacao] = tipos_solicitacao.get(tipo_solicitacao, 0) + 1

    gerar_grafico_pizza(doc, tipos_solicitacao)


def gerar_relatorio_chamados(doc, pipes_data, start_date, end_date):
    """
    Gera a seção 'Relatório de Chamados' com gráfico de linhas, incluindo:
    - Total de chamados abertos no período selecionado.
    - Total de chamados concluídos no período selecionado, independentemente da data de criação.
    """

    if not isinstance(pipes_data, list):
        doc.add_paragraph("Erro: Estrutura dos dados do pipe inválida.")
        return

    # Converter start_date e end_date para date se forem datetime
    start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, datetime) else end_date

    total_chamados_abertos = 0
    total_chamados_concluidos = 0
    chamados_por_data = defaultdict(lambda: {'abertos': 0, 'concluidos': 0})

    for pipe in pipes_data:
        phases = pipe.get('phases', [])
        if not isinstance(phases, list):
            doc.add_paragraph("Erro: Estrutura das fases do pipe inválida.")
            return
        for phase in phases:
            cards = phase.get('cards', {}).get('edges', [])
            for card_edge in cards:
                card = card_edge.get('node', {})
                card_created_date = datetime.strptime(card['created_at'], "%Y-%m-%dT%H:%M:%SZ").date()

                if start_date <= card_created_date <= end_date:
                    total_chamados_abertos += 1
                    chamados_por_data[card_created_date]['abertos'] += 1
                phases_history = card.get('phases_history', [])
                total_duration = sum(phase['duration'] for phase in phases_history)
                card_conclusion_date = (datetime.combine(card_created_date, datetime.min.time()) + timedelta(seconds=total_duration)).date()

                if card.get('current_phase', {}).get('name') == 'Concluído' and start_date <= card_conclusion_date <= end_date:
                    total_chamados_concluidos += 1
                    chamados_por_data[card_conclusion_date]['concluidos'] += 1

    doc.add_paragraph('1 - Principais ocorrências')
    doc.add_paragraph(f'Durante o período de {start_date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")} foram detectadas {total_chamados_abertos} ocorrências em aberto e {total_chamados_concluidos} ocorrências devidamente tratadas e aplicadas sem impactos relevantes no ambiente. Inclusive sem a necessidade de emissão de relatórios de eventos operacionais.')
    doc.add_paragraph(f'Total de chamados abertos: {total_chamados_abertos}')
    doc.add_paragraph(f'Total de chamados concluídos: {total_chamados_concluidos}')

    grafico_linhas_url = gerar_grafico_linhas(chamados_por_data, start_date, end_date)
    if grafico_linhas_url:
        img_stream = io.BytesIO(base64.b64decode(grafico_linhas_url))
        doc.add_picture(img_stream, width=Inches(6))

def gerar_grafico_linhas(chamados_por_data, start_date, end_date):
    """
    Gera um gráfico de linhas mostrando a evolução de chamados abertos e concluídos ao longo do tempo.
    """
    datas = sorted(chamados_por_data.keys())
    abertos = [chamados_por_data[data]['abertos'] for data in datas]
    concluidos = [chamados_por_data[data]['concluidos'] for data in datas]

    plt.figure(figsize=(10, 6))
    plt.plot(datas, abertos, label='Chamados Abertos', marker='o')
    plt.plot(datas, concluidos, label='Chamados Concluídos', marker='o')
    plt.xlabel('Data')
    plt.ylabel('Quantidade de Chamados')
    plt.title(f'Evolução dos Chamados Abertos e Concluídos ({start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")})')
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return grafico_url

def gerar_grafico_pizza2(chamados_por_departamento):
    """
    Gera um gráfico de pizza para representar a distribuição de chamados por departamento.
    """
    labels = chamados_por_departamento.keys()
    sizes = chamados_por_departamento.values()

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return grafico_url

def gerar_grafico_pizza(doc, data):
    """
    Gera gráfico de pizza e insere no documento.
    """
    labels = list(data.keys())
    sizes = list(data.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    doc.add_picture(img_stream, width=Inches(5))
    plt.close()

def gerar_relatorio_com_dados_prometheus(doc, prometheus_data):
    """
    Insere gráficos com os dados retornados do Prometheus.
    """
    for query, result in prometheus_data.items():
        timestamps, values = processar_dados_prometheus(result)
        if timestamps and values:
            doc.add_heading(f'Dados do Prometheus - {query}', level=2)
            gerar_grafico_prometheus(doc, timestamps, values, query)


def processar_dados_prometheus(prometheus_data):
    """
    Processa os dados retornados pelo Prometheus.
    """
    results = prometheus_data.get('data', {}).get('result', [])
    timestamps = []
    values = []

    if results:
        for value in results[0].get('values', []):
            timestamps.append(datetime.fromtimestamp(value[0]))
            values.append(float(value[1]))

    return timestamps, values


def gerar_grafico_prometheus(doc, timestamps, values, title):
    """
    Gera gráfico com dados do Prometheus e insere no relatório.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=values, mode='lines', name=title))

    img_stream = BytesIO()
    fig.write_image(img_stream, format='png')
    img_stream.seek(0)
    doc.add_picture(img_stream, width=Inches(5))


def gerar_relatorio_com_dados_grafana(doc, grafana_data):
    """
    Insere gráficos baseados nos dados retornados pelo Grafana.
    """
    panels = grafana_data.get('dashboard', {}).get('panels', [])
    for panel in panels:
        panel_id = panel.get('id')
        panel_title = panel.get('title', 'Título do Painel')
        doc.add_heading(f'Painel: {panel_title}', level=2)
        doc.add_paragraph(f'ID do Painel: {panel_id}')

def set_background_image(section, image_path):
    header = section.header
    paragraph = header.paragraphs[0]
    run = paragraph.add_run()
    run.add_picture(image_path)
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

def gerar_pagina_inicial(doc, start_date, end_date):
    section = doc.add_section(WD_SECTION_START.NEW_PAGE)

    #set_background_image(section, './app/img_inicial.png')

    # Adicionar o logo à esquerda
    p_logo = doc.add_paragraph()
    run_logo = p_logo.add_run()
    run_logo.add_picture('./app/img_itfacil.png', width=Inches(1))  # Tamanho da logo ajustado
    p_logo.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT  # Alinhado à esquerda

    # Adicionar o logo à direita
    p_logo_direita = doc.add_paragraph()
    run_logo_direita = p_logo_direita.add_run()
    run_logo_direita.add_picture('./app/img_ecom.png', width=Inches(1))
    p_logo_direita.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # Adicionar o título do relatório
    paragraph = doc.add_paragraph("Relatório Mensal")
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.runs[0]
    run.font.size = Pt(24)
    run.bold = True

    # Subtítulo
    paragraph = doc.add_paragraph(f'Run BOOK\n{start_date.strftime("%B")} de 2024')
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.runs[0]
    run.font.size = Pt(18)

    # Detalhes do documento
    paragraph = doc.add_paragraph("Relatório Gerencial Mensal\nInformativo – RunBook\nVolumetria e Nível de Serviço")
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.runs[0]
    run.font.size = Pt(12)

    # Controle do documento
    paragraph = doc.add_paragraph("Controle do documento — Versão - 001\nGerente Contrato: Alexandre Bruno")
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.runs[0]
    run.font.size = Pt(10)

    # Data de entrega e referência
    paragraph = doc.add_paragraph(f'Data de entrega – 10{start_date.strftime("/%m/%Y")}\nReferência – {start_date.strftime("%d/%m/%Y")} – de 01 até {end_date.strftime("%d/%m/%Y")}')
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = paragraph.runs[0]
    run.font.size = Pt(10)

    # Ajustar estilo da página inicial
    section.orientation = WD_PARAGRAPH_ALIGNMENT.CENTER
    section.page_height = Inches(11)
    section.page_width = Inches(8.5)


def gerar_historico_versoes(doc, autorResponsavel, numberVersion):
    """
    Gera a tabela de histórico de versões.
    """
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Criação da tabela de histórico
    table = doc.add_table(rows=2, cols=4)
    table.style = 'Table Grid'

    # Cabeçalhos
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'DATA'
    hdr_cells[1].text = 'VERSÃO'
    hdr_cells[2].text = 'DESCRIÇÃO DE ALTERAÇÃO'
    hdr_cells[3].text = 'RESPONSÁVEIS'

    # Linha com os dados
    row_cells = table.rows[1].cells
    row_cells[0].text = data_atual
    row_cells[1].text = str(numberVersion)
    row_cells[2].text = 'Criação de documento'
    row_cells[3].text = f"Autor: {autorResponsavel}\nRevisor: Leandro Gimenez\nAprovador: Alexandre Bruno"


def add_hyperlink(paragraph, url, text, color="0000FF", underline=True):
    """
    Adiciona um hyperlink ao parágrafo.

    :param paragraph: O parágrafo onde será adicionado o hyperlink
    :param url: O URL do link
    :param text: O texto que será mostrado para o link
    :param color: A cor do texto do link (padrão é azul)
    :param underline: Se o link deve ser sublinhado (padrão é True)
    """

    # Criar o namespace de relação no documento
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Criar o elemento <w:hyperlink> para o link
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    # Criar o <w:r> que contém o texto do link
    new_run = OxmlElement('w:r')

    # Criar o <w:rPr> que contém as propriedades do texto (cor, sublinhado, etc.)
    rPr = OxmlElement('w:rPr')

    # Definir a cor do link
    c = OxmlElement('w:color')
    c.set(qn('w:val'), color)
    rPr.append(c)

    # Definir o sublinhado do link
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)
    else:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'none')
        rPr.append(u)

    # Adicionar o texto ao run
    new_run.append(rPr)
    new_run.text = text

    # Anexar o run ao hyperlink
    hyperlink.append(new_run)

    # Adicionar o hyperlink ao parágrafo
    paragraph._element.append(hyperlink)