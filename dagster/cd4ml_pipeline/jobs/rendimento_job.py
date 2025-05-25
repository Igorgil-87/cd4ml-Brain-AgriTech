from dagster import job
from cd4ml_pipeline.ops.rendimento_ops import train_rendimento_model

@job
def rendimento_job():
    train_rendimento_model()