
import polars as pl
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from urllib.parse import quote



ROOT_DIR = Path(__file__).resolve().parent.parent.parent
caminho_env = ROOT_DIR / ".env"

load_dotenv(dotenv_path=caminho_env, override=True)


def testar_conexao(engine):
    """Faz um 'ping' no banco para garantir que ele existe e está acessível."""
    print("[INFO] Executando Pre-flight check: Testando conexão com o banco...")
    try:
        # Tenta abrir uma conexão e rodar uma query inofensiva
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[INFO] Conexão validada com sucesso! O banco está pronto.")
        return True
    
    except OperationalError as e:
        print("\n[CRITICAL ERROR] O pipeline foi interrompido.")
        print("[MOTIVO] Não foi possível conectar ao banco de dados. Verifique se:")
        print("  1. O servidor MySQL está rodando.")
        print("  2. O banco de dados (ex: dw_vendas) realmente existe.")
        print("  3. As credenciais no arquivo .env estão corretas.")
        print(f"\n[LOG TÉCNICO]: {e}\n")
        
        # O sys.exit(1) avisa ao sistema operacional (ou Airflow) que o script falhou com erro
        sys.exit(1)

def carregar_para_mysql():
    print("[INFO] Iniciando o processo de Load (Camada Gold)...")
    
    # 1. Encontrar o arquivo Parquet mais recente na Camada Silver
    pasta_silver = ROOT_DIR / "data" / "silver"
    arquivos_parquet = list(pasta_silver.glob("*.parquet"))
    
    if not arquivos_parquet:
        raise FileNotFoundError("[ERROR] Nenhum arquivo Parquet encontrado na camada Silver.")
        
    arquivo_mais_recente = max(arquivos_parquet, key=lambda x: x.stat().st_mtime)
    print(f"[INFO] Lendo dados da Camada Silver: {arquivo_mais_recente.name}")
    
    # Lemos o Parquet com Polars
    df_silver = pl.read_parquet(arquivo_mais_recente)
    
    # 2. Montar a string de conexão com o MySQL usando SQLAlchemy
    db_user = quote(os.getenv("DB_USER"))
    db_password = quote(os.getenv("DB_PASSWORD"))
    db_host = quote(os.getenv("DB_HOST"))
    db_port = quote(os.getenv("DB_PORT"))
    db_name = quote(os.getenv("DB_NAME"))
    
    uri_conexao = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(uri_conexao)
    testar_conexao(engine)
    
    # 3. Inserir os dados no Banco de Dados
    nome_tabela = "gold_vendas"
    print(f"[INFO] Inserindo {df_silver.height} registros na tabela '{nome_tabela}' no MySQL...")
    


    # Criando a tabela automaticamente scaso não exista
    df_silver.write_database(
        table_name=nome_tabela,
        connection=uri_conexao,
        if_table_exists="replace", 
        engine="sqlalchemy"
    )
    
    print("[SUCCESS] Carga finalizada com sucesso! Os dados estão disponíveis no MySQL.")

if __name__ == "__main__":
    carregar_para_mysql()