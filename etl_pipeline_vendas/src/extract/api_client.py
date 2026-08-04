import requests
import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Carrega as variáveis do arquivo .env para a memória do sistema
load_dotenv()

def extrair_vendas(url_base: str):
    """
    Função para extrair todas as páginas de vendas da API.
    """
    vendas_extraidas = []
    pagina_atual = 1
    tem_proxima_pagina = True

    print(f"Iniciando extração da API: {url_base}")

    while tem_proxima_pagina:
        url_paginada = f"{url_base}?page={pagina_atual}&limit=100"
        print(f"Buscando página {pagina_atual}...")

        try:
            # Faz o GET
            resposta = requests.get(url_paginada)
            
            # GATILHO DE ERRO: Força ir para o 'except' se o HTTP for 4xx ou 5xx
            resposta.raise_for_status()

            # Converte direto para Dicionário Python
            dados_dict = resposta.json()

            # Funde a lista de vendas atual com a lista total de uma vez só
            vendas_extraidas.extend(dados_dict['data'])
            
            # Atualiza a condição de parada lendo o booleano que a API já calculou
            tem_proxima_pagina = dados_dict['meta']['tem_proxima_pagina']
            
            # Prepara para a próxima rodada (só executa se tem_proxima_pagina continuar True)
            pagina_atual += 1

        except Exception as e:
            # Agora sim, se a API der Erro 500, o código cai aqui, espera 5s e tenta a MESMA página de novo!
            print(f"Erro ao buscar página {pagina_atual}: {e}")
            print("Aguardando 5 segundos antes de tentar novamente...")
            time.sleep(5)

    print(f"Extração concluída! Total de registros: {len(vendas_extraidas)}")
    return vendas_extraidas

# --- Área de Teste Local ---


# --- Área de Teste Local ---
if __name__ == "__main__":

    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Busca a URL nas variáveis de ambiente em vez de digitar o texto direto
    URL = os.getenv("API_URL_VENDAS")

    # Validação de segurança: se esquecermos de criar o .env, o script avisa e para!
    if not URL:
        raise ValueError("ERRO: A variável API_URL_VENDAS não foi encontrada no arquivo .env!")

    print(f"Iniciando pipeline conectando em: {URL}")
    dados = extrair_vendas(URL)
    
    if dados:
        # Define o caminho do diretório Bronze dinamicamente
        caminho_pasta = ROOT_DIR / "data" / "bronze"
        
        # O os.makedirs aceita objetos Path tranquilamente
        os.makedirs(caminho_pasta, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"vendas_bronze_{timestamp}.json"
        caminho_arquivo = caminho_pasta / nome_arquivo
        
        # Salva o arquivo JSON no disco
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
            
        print(f"\n[SUCESSO] {len(dados)} registros salvos na camada Bronze em: {caminho_arquivo}")