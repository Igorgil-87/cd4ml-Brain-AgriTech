from dagster import define_asset_job
from cd4ml_pipeline.assets.rendimento_asset import rendimento_data
from cd4ml_pipeline.ops.rendimento_ops import preprocess_rendimento, train_rendimento_model

rendimento_job = define_asset_job(
    name="rendimento_job",
    selection=["rendimento_data"]
)