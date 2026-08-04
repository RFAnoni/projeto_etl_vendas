import polars as pl
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

def processar_camada_bronze(caminho_json: Path):
    if not caminho_json.exists():
        raise FileNotFoundError(f"Erro: O arquivo {caminho_json} não foi encontrado na Camada Bronze.")
        
    print(f"\n[1] Lendo dados da camada Bronze: {caminho_json.name}")
    df_raw = pl.read_json(caminho_json)
    
    # --- VERIFICAÇÃO ANTES DO EXPLODE ---
    linhas_originais = df_raw.height
    print(f"-> Quantidade de Vendas originais (linhas): {linhas_originais}")
    
    colunas_struct = [
        coluna for coluna, tipo in df_raw.schema.items() 
        if isinstance(tipo, pl.Struct)
    ]
    
    # 2. Desempacota as colunas do tipo Struct
    df_tratado = df_raw.unnest(colunas_struct)
    
   # 3. Explode a lista de parcelas e desempacota
    df_final = (
        df_tratado
        .explode("parcelas_cronograma", empty_as_null=True)
        .unnest("parcelas_cronograma")
    )
    # --- VERIFICAÇÃO APÓS O EXPLODE ---
    linhas_finais = df_final.height
    print(f"-> Quantidade após explode (linhas de parcelas): {linhas_finais}")
    
    if linhas_originais > 0:
        aumento = linhas_finais / linhas_originais
        print(f"-> O volume de linhas multiplicou em {aumento:.2f}x!")
    
    return df_final

if __name__ == "__main__":
    pasta_bronze = ROOT_DIR / "data" / "bronze"
    arquivos_json = list(pasta_bronze.glob("*.json"))
    
    if not arquivos_json:
        print("Nenhum arquivo JSON encontrado na camada Bronze!")
    else:
        # Pega o arquivo modificado mais recentemente
        arquivo_mais_recente = max(arquivos_json, key=lambda x: x.stat().st_mtime)
        
        # Executa a transformação
        df_silver = processar_camada_bronze(arquivo_mais_recente)
        
        # --- FASE DE CARGA NA CAMADA SILVER ---
        print("\n[2] Salvando dados na Camada Silver...")
        pasta_silver = ROOT_DIR / "data" / "silver"
        
        # Cria a pasta silver se não existir
        pasta_silver.mkdir(exist_ok=True) 
        
        # Gera o nome do arquivo com timestamp atual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_silver = pasta_silver / f"vendas_silver_{timestamp}.parquet"
        
        # Escreve o DataFrame no disco em formato Parquet
        df_silver.write_parquet(caminho_silver)
        
        print(f"[SUCESSO] Tabela final (OBT) salva com sucesso em:")
        print(f"{caminho_silver}")