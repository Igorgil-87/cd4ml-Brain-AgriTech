from dagster import AssetSensorDefinition, RunRequest, SensorEvaluationContext
from cd4ml_pipeline.jobs.rendimento_job import rendimento_job
from cd4ml_pipeline.jobs.commodities_job import commodities_job
from cd4ml_pipeline.jobs.insumo_job import insumo_job
from cd4ml_pipeline.jobs.saude_lavoura_job import saude_lavoura_job

def make_asset_sensor(job, asset_key, sensor_name):
    return AssetSensorDefinition(
        name=sensor_name,
        asset_key=asset_key,
        minimum_interval_seconds=3600,  # roda a cada 1 hora
        job=job,
        evaluation_fn=lambda context: [
            RunRequest(run_key=None, run_config={})
        ],
    )

rendimento_sensor = make_asset_sensor(
    rendimento_job, asset_key="rendimento_data", sensor_name="sensor_rendimento_data"
)

commodities_sensor = make_asset_sensor(
    commodities_job, asset_key="commodities_data", sensor_name="sensor_commodities_data"
)

insumo_sensor = make_asset_sensor(
    insumo_job, asset_key="insumo_data", sensor_name="sensor_insumo_data"
)

saude_lavoura_sensor = make_asset_sensor(
    saude_lavoura_job, asset_key="saude_lavoura_data", sensor_name="sensor_saude_lavoura_data"
)