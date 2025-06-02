# cd4ml_pipeline/repository.py

from dagster import repository
from cd4ml_pipeline.assets.rendimento_asset import rendimento_data
from cd4ml_pipeline.assets.commodities_asset import commodities_data
from cd4ml_pipeline.assets.insumo_asset import insumo_data
from cd4ml_pipeline.assets.saude_lavoura_asset import saude_lavoura_data

from cd4ml_pipeline.jobs.rendimento_job import rendimento_job
from cd4ml_pipeline.jobs.commodities_job import commodities_job
from cd4ml_pipeline.jobs.insumo_job import insumo_job
from cd4ml_pipeline.jobs.saude_lavoura_job import saude_lavoura_job

from cd4ml_pipeline.sensors.asset_sensors import (
    rendimento_sensor,
    commodities_sensor,
    insumo_sensor,
    saude_lavoura_sensor
)

from cd4ml_pipeline.sensors.slack_sensors import notify_on_failure

@repository
def cd4ml_repository():
    return [
        rendimento_job,
        commodities_job,
        insumo_job,
        saude_lavoura_job,
        rendimento_data,
        commodities_data,
        insumo_data,
        saude_lavoura_data,
        rendimento_sensor,
        commodities_sensor,
        insumo_sensor,
        saude_lavoura_sensor,
        notify_on_failure,
    ]