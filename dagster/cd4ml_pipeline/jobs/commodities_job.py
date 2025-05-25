from dagster import job
from cd4ml_pipeline.ops.commodities_ops import train_commodities

@job
def commodities_job():
    train_commodities()