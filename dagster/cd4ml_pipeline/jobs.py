from dagster import job
from cd4ml_pipeline.ops import hello_world  # ✅ Importação absoluta

@job
def hello_pipeline():
    hello_world()