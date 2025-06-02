# cd4ml_pipeline/sensors/asset_sensors.py

from dagster import asset_sensor, AssetKey, RunRequest, SensorEvaluationContext, AssetExecutionContext

from cd4ml_pipeline.jobs.rendimento_job import rendimento_job
from cd4ml_pipeline.jobs.commodities_job import commodities_job
from cd4ml_pipeline.jobs.insumo_job import insumo_job
from cd4ml_pipeline.jobs.saude_lavoura_job import saude_lavoura_job

@asset_sensor(asset_key=AssetKey("rendimento_data"), name="sensor_rendimento_data", job=rendimento_job)
def rendimento_sensor(context: SensorEvaluationContext, asset_event: AssetExecutionContext):
    return RunRequest(run_key=None, run_config={})

@asset_sensor(asset_key=AssetKey("commodities_data"), name="sensor_commodities_data", job=commodities_job)
def commodities_sensor(context: SensorEvaluationContext, asset_event: AssetExecutionContext):
    return RunRequest(run_key=None, run_config={})

@asset_sensor(asset_key=AssetKey("insumo_data"), name="sensor_insumo_data", job=insumo_job)
def insumo_sensor(context: SensorEvaluationContext, asset_event: AssetExecutionContext):
    return RunRequest(run_key=None, run_config={})

@asset_sensor(asset_key=AssetKey("saude_lavoura_data"), name="sensor_saude_lavoura_data", job=saude_lavoura_job)
def saude_lavoura_sensor(context: SensorEvaluationContext, asset_event: AssetExecutionContext):
    return RunRequest(run_key=None, run_config={})