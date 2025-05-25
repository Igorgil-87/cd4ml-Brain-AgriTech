from dagster import job
from cd4ml_pipeline.ops.saude_lavoura_ops import train_saude_lavoura

@job
def saude_lavoura_job():
    train_saude_lavoura()