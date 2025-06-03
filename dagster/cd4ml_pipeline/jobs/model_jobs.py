from dagster import job

from cd4ml_pipeline.ops.insumo_ops import train_insumo
from cd4ml_pipeline.ops.commodities_ops import train_commodities
from cd4ml_pipeline.ops.rendimento_ops import train_rendimento_model, preprocess_rendimento
from cd4ml_pipeline.ops.saude_lavoura_ops import train_saude_lavoura

from cd4ml_pipeline.assets.insumo_asset import insumo_data
from cd4ml_pipeline.assets.commodities_asset import commodities_data
from cd4ml_pipeline.assets.saude_lavoura_asset import saude_lavoura_data


@job
def insumo_job():
    train_insumo(insumo_data())


@job
def commodities_job():
    train_commodities(commodities_data())


@job
def rendimento_job():
    train_rendimento_model(preprocess_rendimento())


@job
def saude_lavoura_job():
    train_saude_lavoura(saude_lavoura_data())