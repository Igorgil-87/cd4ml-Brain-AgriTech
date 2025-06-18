import logging
from loaders.load_agrotoxico import load_agrotoxico
from loaders.load_arroz_solo_transformado import load_arroz_solo_transformado
from loaders.load_arroz import load_arroz
from loaders.load_climate_data import load_climate_data
from loaders.load_fertilizantes import load_fertilizantes
from loaders.load_milho_solo_transformado import load_milho_solo_transformado
from loaders.load_milho import load_milho
from loaders.load_producao_fertilizantes import load_producao_fertilizantes
from loaders.load_producao_semente import load_producao_semente
from loaders.load_ranking_agricultura_valor import load_ranking_agricultura_valor
from loaders.load_regions import load_regions
from loaders.load_registro_agrotoxico import load_registro_agrotoxico
from loaders.load_semente import load_semente
from loaders.load_soja import load_soja
from loaders.load_stations import load_stations
from loaders.load_tabua_de_risco import load_tabua_de_risco
from loaders.load_trigo_solo_transformado import load_trigo_solo_transformado
from loaders.load_trigo import load_trigo
from loaders.load_soja_solo_transformado import load_soja_solo_transformado


import sys
import os
from sqlalchemy import create_engine
import chardet

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",
    "port": "5432"
}

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Criação da conexão SQLAlchemy
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)



# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_data():
    """
    Função principal para carregar todos os dados no banco de dados.
    Chama as funções específicas em 'loaders/' para cada conjunto de dados.
    """
    try:
        logging.info("Iniciando o processo de carregamento de dados...")
        logging.info("Iniciando o processo de registro agrotoxico...")
        load_registro_agrotoxico(engine)
        logging.info("Iniciando o processo de carregamento de dados regions...")
        load_regions(engine)
        logging.info("Iniciando o processo de carregamento de dados producao semente...")
        load_producao_semente(engine)
        logging.info("Iniciando o processo de carregamento de dados producao fertilizante...")
        load_producao_fertilizantes(engine)
        logging.info("Iniciando o processo de carregamento de dados ranking agricultura...")
        load_ranking_agricultura_valor(engine)
        logging.info("Iniciando o processo de carregamento de dados semente...")
        load_semente(engine)
        logging.info("Iniciando o processo de carregamento de dados agrotoxico...")
        load_agrotoxico(engine)
        logging.info("Iniciando o processo de carregamento de dados fertilizante...")
        load_fertilizantes(engine)
        # Chamadas de cada loader
        logging.info("Iniciando o processo de carregamento de dados de estacao...")
        load_stations(engine)   #ok
        logging.info("Iniciando o processo de carregamento de dados climatico...")
        load_climate_data(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de risco...")
        load_tabua_de_risco(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de arroz...")        
        load_arroz(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de milho...")        
        load_milho(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de soja...")        
        load_soja(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de trigo...")        
        load_trigo(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de solo arroz...")
        load_arroz_solo_transformado(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de solo milho...")        
        load_milho_solo_transformado(engine)
        logging.info("Iniciando o processo de carregamento de dados tabua de solo soja...")        
        load_soja_solo_transformado(engine)        
        logging.info("Iniciando o processo de carregamento de dados tabua de solo trigo...")        
        load_trigo_solo_transformado(engine)
        logging.info("Carregamento de dados concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro no processo de carregamento de dados: {e}")

if __name__ == "__main__":
    load_data()