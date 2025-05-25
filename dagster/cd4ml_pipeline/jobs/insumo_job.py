from dagster import job
from cd4ml_pipeline.ops.insumo_ops import train_insumo

@job
def insumo_job():
    train_insumo()