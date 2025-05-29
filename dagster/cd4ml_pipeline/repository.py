from dagster import Definitions
from cd4ml_pipeline.assets import rendimento_asset, commodities_asset, insumo_asset, saude_lavoura_asset
from cd4ml_pipeline.jobs import rendimento_job, commodities_job, insumo_job, saude_lavoura_job
from cd4ml_pipeline.sensors.asset_sensors import (
    rendimento_sensor,
    commodities_sensor,
    insumo_sensor,
    saude_lavoura_sensor
)

defs = Definitions(
    assets=[
        rendimento_asset.rendimento_data,
        commodities_asset.commodities_data,
        insumo_asset.insumo_data,
        saude_lavoura_asset.saude_lavoura_data
    ],
    jobs=[
        rendimento_job.rendimento_job,
        commodities_job.commodities_job,
        insumo_job.insumo_job,
        saude_lavoura_job.saude_lavoura_job
    ],
    sensors=[
        rendimento_sensor,
        commodities_sensor,
        insumo_sensor,
        saude_lavoura_sensor
    ]
)

# cd4ml_pipeline/repository.py

from cd4ml_pipeline.sensors.slack_sensors import notify_on_failure

@repository
def cd4ml_repository():
    return [
        rendimento_job,
        commodities_job,
        insumo_job,
        saude_lavoura_job,
        notify_on_failure,
        rendimento_data,
        commodities_data,
        insumo_data,
        saude_lavoura_data,
    ]