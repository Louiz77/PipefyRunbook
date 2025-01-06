# Relatório Runbook Automatizado (Backend Python)

Este projeto consiste em um backend desenvolvido em Python utilizando o framework Flask. Ele é responsável por automatizar a geração de relatórios gerenciais em formato Word a partir de dados extraídos do **Pipefy** e enriquecidos com gráficos, imagens e informações personalizadas. O sistema também permite a seleção personalizada da data das informações e oferece APIs para integração.

---

## **Características Principais**

- Geração automatizada de relatórios gerenciais (Word).
- Integração com **Pipefy** para extração de dados.
- Inclusão de gráficos e imagens no relatório.
- APIs REST para geração manual e consulta do status dos relatórios.
- Registro detalhado de logs do sistema.

---

## **Pré-requisitos**

- **Python** (3.8 ou superior)
- **Pip** (gerenciador de pacotes do Python)
- Ambiente virtual configurado (**venv** recomendado)
- Acesso configurado ao **Pipefy** e aos endpoints integrados

---

## **Instalação**

### **1. Clone o repositório**
```bash
git clone https://github.com/Louiz77/PipefyRunbook.git
cd PipefyRunbook
```

### **2. Crie e ative um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### **3. Instale as dependências**
```bash
pip install -r requirements.txt
```

---

## **Configuração**

### **1. Variáveis de ambiente**
Crie um arquivo `.env` na raiz do projeto e adicione as seguintes configurações:

```env
PIPEFY_API_KEY = key
GRAFANA_API_KEY = key
GRAFANA_URL = url
PROMETHEUS_URL= url
```

### **2. Configuração do diretório de upload**
Certifique-se de que o diretório `upload` está criado na raiz do projeto:
```bash
mkdir upload
```

---

## **Uso**

### **1. Executar o servidor**
Para iniciar o servidor em modo de desenvolvimento:
```bash
flask run
```

O servidor será executado por padrão em: [http://127.0.0.1:8530](http://127.0.0.1:8530).

---

### **2. Endpoints Principais**

#### **Gerar Relatório**
- **Método:** `POST`
- **URL:** `/relatorios/gerar`
- **Parâmetros:** 
  - `start_date` (YYYY-MM-DD) - Data inicial do relatório.
  - `end_date` (YYYY-MM-DD) - Data final do relatório.
  - `autorResponsavel` - Nome do responsável pelo relatório.
  - `numberVersion` - Versão do relatório.
  - Imagens (upload multipart/form-data): `pipefy_image`, `grafana_image_1` a `grafana_image_5`.

#### **Consultar Status do Relatório**
- **Método:** `GET`
- **URL:** `/relatorios/status/<report_id>`

#### **Baixar Relatório**
- **Método:** `GET`
- **URL:** `/relatorios/download/<report_id>`

---

## **Testes**

### **1. Executar testes unitários**
```bash
pytest
```

Os testes estão localizados no diretório `app/tests`.

---

## **Principais Tecnologias Utilizadas**

- **Flask**: Framework web para o backend.
- **Pandas**: Processamento de dados.
- **Matplotlib**: Geração de gráficos.
- **Python-docx**: Manipulação de documentos Word.
- **Pytest**: Testes unitarios.
- **docxcompose**: Composição de um documento Word em outro.

---

## **Contribuições**

Contribuições são bem-vindas! Para reportar problemas ou sugerir melhorias, abra uma issue ou envie um pull request.

---

## **Licença**

Este projeto está licenciado sob a [MIT License](LICENSE).
