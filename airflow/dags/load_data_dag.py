from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Adiciona o diretório dos scripts ao path
sys.path.append('/opt/airflow/scripts')
sys.path.append('/opt/airflow/scripts/loaders')

from sqlalchemy import create_engine

# Conexão com PostgreSQL
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",
    "port": "5432"
}
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Importa os loaders individualmente
from load_agrotoxico import load_agrotoxico
from load_soja import load_soja
from load_milho import load_milho
from load_trigo import load_trigo
from load_arroz import load_arroz
from load_climate_data import load_climate_data
from load_stations import load_stations
from load_ranking_agricultura_valor import load_ranking_agricultura_valor
# ... importe os demais loaders que você tiver

default_args = {
    'owner': 'agro_user',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='pipeline_carregamento_agro_por_tabela',
    default_args=default_args,
    description='Pipeline Airflow com carregamentos separados por dataset',
    schedule_interval='@daily',  # ou altere conforme desejar
    catchup=False,
    max_active_runs=1,
    tags=['agro', 'pipeline'],
) as dag:

    def wrapper(func):
        return lambda: func(engine)

    task_agrotoxico = PythonOperator(
        task_id='carregar_agrotoxico',
        python_callable=wrapper(load_agrotoxico)
    )

    task_soja = PythonOperator(
        task_id='carregar_soja',
        python_callable=wrapper(load_soja)
    )

    task_milho = PythonOperator(
        task_id='carregar_milho',
        python_callable=wrapper(load_milho)
    )

    task_trigo = PythonOperator(
        task_id='carregar_trigo',
        python_callable=wrapper(load_trigo)
    )

    task_arroz = PythonOperator(
        task_id='carregar_arroz',
        python_callable=wrapper(load_arroz)
    )

    task_clima = PythonOperator(
        task_id='carregar_clima',
        python_callable=wrapper(load_climate_data)
    )

    task_estacoes = PythonOperator(
        task_id='carregar_estacoes',
        python_callable=wrapper(load_stations)
    )

    task_ranking = PythonOperator(
        task_id='carregar_ranking_agricultura',
        python_callable=wrapper(load_ranking_agricultura_valor)
    )

    # Exemplo de orquestração: clima e estações em paralelo, depois ranking
    [task_clima, task_estacoes] >> task_ranking

    # Grãos em paralelo com ranking
    [task_soja, task_milho, task_trigo, task_arroz, task_agrotoxico] >> task_ranking