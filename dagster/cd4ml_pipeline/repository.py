# cd4ml_pipeline/repository.py

from dagster import Definitions, load_assets_from_modules

# Módulos de assets
from cd4ml_pipeline.assets import (
    rendimento_asset,
    commodities_asset,
    insumo_asset,
    saude_lavoura_asset
)

# Módulos de jobs
from cd4ml_pipeline.jobs.model_jobs import (
    rendimento_job,
    commodities_job,
    insumo_job,
    saude_lavoura_job
)

# Sensores
from cd4ml_pipeline.sensors.asset_sensors import (
    rendimento_sensor,
    commodities_sensor,
    insumo_sensor,
    saude_lavoura_sensor
)
from cd4ml_pipeline.sensors.slack_sensors import notify_on_failure

# Carregando assets automaticamente dos módulos
all_assets = load_assets_from_modules([
    rendimento_asset,
    commodities_asset,
    insumo_asset,
    saude_lavoura_asset,
])

# Registro final
defs = Definitions(
    assets=all_assets,
    jobs=[
        rendimento_job,
        commodities_job,
        insumo_job,
        saude_lavoura_job
    ],
    sensors=[
        rendimento_sensor,
        commodities_sensor,
        insumo_sensor,
        saude_lavoura_sensor,
        notify_on_failure
    ]
)