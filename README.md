<div align="center">

# 🚀 Projeto ETL Vendas: Do Excel Manual a um Pipeline Orquestrado

![Visualizações](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FRFAnoni%2Fprojeto_etl_vendas&count_bg=%23007EC6&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=visualiza%C3%A7%C3%B5es&edge_flat=false)

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/Polars-CD792C?style=for-the-badge&logo=polars&logoColor=white" alt="Polars" />
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
<img src="https://img.shields.io/badge/Status-Em_Desenvolvimento-success?style=for-the-badge" alt="Status" />

</div>
<br>

Quem nunca precisou extrair um relatório, jogar no Excel e fazer malabarismos com dezenas de fórmulas para gerar um dashboard? 

Para sair dessa rotina manual e aprofundar meus estudos na construção de fluxos de dados, decidi criar o **projeto_etl_vendas**. Meu grande objetivo aqui não é apenas ter um código que funcione, mas sim entender a fundo a lógica, a arquitetura e o funcionamento das ferramentas envolvidas em um pipeline End-to-End.

---

## 🗺️ Roadmap do Projeto (O que vem por aí?)
Este é um projeto vivo, focado no uso de ferramentas modernas e open-source. 

- [x] **Fase 1 (Extract & Transform):** 
  - 🧩 **Mock API:** Para não depender de planilhas estáticas, criei uma API própria (FastAPI) simulando um sistema real, estruturando um ambiente controlado para focar 100% na lógica de extração.
  - ⚡ **Alta Performance:** Construção da extração modular e utilização do **Polars** (substituindo o Pandas) para otimizar o uso de memória e velocidade no achatamento de JSONs aninhados (`unnest` e `explode`).
- [ ] **Fase 2 (Load):** Modelar o destino e carregar os dados transformados em um banco de dados relacional (MySQL).
- [ ] **Fase 3 (Orquestração):** Fazer o deploy da API e estudar a implementação do **Apache Airflow** para agendar e monitorar todo o fluxo.
- [ ] **Fase 4 (Data Viz):** Plugar a camada final em uma ferramenta de visualização para criar um Dashboard estratégico.

---

## 🏗️ Arquitetura do Projeto (Fase 1 Concluída)

O repositório utiliza o conceito de **Monorepo**, dividido em dois ecossistemas independentes:

1. 🌐 **`mock_api_vendas/`**: Uma API RESTful construída com FastAPI e Faker que gera transações de vendas com dados complexos e aninhados.
2. ⚙️ **`etl_pipeline_vendas/`**: O pipeline de dados estruturado utilizando o conceito de **Arquitetura Medalhão** (Medallion Architecture).

### 🥉 Camada Bronze (Raw)
- O script consome a API e salva a resposta bruta em JSON.
- **Governança:** Particionamento por execução (Time Travel) garantindo a imutabilidade do dado original.

### 🥈 Camada Silver (Trusted / OBT)
- Processamento ultrarrápido com **Polars**.
- Desempacotamento de dicionários e explosão de listas (normalização de parcelas).
- Salvamento em formato **Parquet**, garantindo alta compressão e leitura colunar.

---

## 💻 Como Executar o Projeto Localmente

### Pré-requisitos
* 🐍 Python 3.10+
* 🐙 Git
* 🖥️ Terminal (PowerShell, Bash, etc.)

---

### Passo 1: Subindo o Sistema de Origem (API)
Abra um terminal, acesse a pasta da API, crie um ambiente virtual isolado e inicie o servidor:

```powershell
# 1. Acesse a pasta da API
cd mock_api_vendas

# 2. Crie e ative o ambiente virtual (Comandos para Windows)
python -m venv venv
.\venv\Scripts\activate

# 3. Instale as dependências da API
pip install -r requirements.txt

# 4. Inicie o servidor
uvicorn app.main:app --reload
```
A API estará disponível no seu navegador em: `http://127.0.0.1:8000`. Deixe este terminal aberto rodando.

---

### Passo 2: Configurando o Pipeline de Dados
Abra **um NOVO terminal** (para não fechar a API), vá para a pasta do pipeline e configure o ambiente:

```powershell
# 1. Acesse a pasta do pipeline
cd etl_pipeline_vendas

# 2. Crie e ative o ambiente virtual do pipeline (Comandos para Windows)
python -m venv venv
.\venv\Scripts\activate

# 3. Instale as dependências do ETL (Polars, Requests, etc)
pip install -r requirements.txt
```

### Passo 3: Configurando as Variáveis de Ambiente (.env)
Dentro da pasta `etl_pipeline_vendas/`, crie um arquivo chamado exatamente **`.env`** (com o ponto na frente) e cole o seguinte conteúdo dentro dele para que o pipeline saiba onde buscar os dados:

```text
API_URL_VENDAS=[http://127.0.0.1:8000/api/v1/vendas](http://127.0.0.1:8000/api/v1/vendas)
```

### Passo 4: Rodando o Pipeline (A Mágica Acontece)
Com o ambiente ativado e o `.env` configurado, execute os scripts das camadas na ordem:

**📥 Fase de Extração (Ingestão para a Camada Bronze):**
```powershell
python src/extract/api_client.py
```
*(Confira a pasta `data/bronze/` para ver o arquivo JSON bruto particionado com a data e hora da extração).*

**🔄 Fase de Transformação (Bronze para Silver):**
```powershell
python src/transform/transform_polars.py
```
*(Confira a pasta `data/silver/` para ver a One Big Table achatada e compactada no formato Parquet).*

---

## 🤝 Contribuições e Feedback
Como este é um projeto de estudo contínuo focando no ecossistema de Data Analytics e Engenharia de Dados, adoraria receber dicas, críticas construtivas e trocar ideias sobre código e arquitetura. Fique à vontade para abrir uma *Issue* ou me chamar nas redes!

**#DataAnalytics #EngenhariaDeDados #Estudos #Python #Polars #ApacheAirflow #ETL #BuildInPublic**