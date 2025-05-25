from dagster import job
from .ops import hello_world, exibe_mensagem

@job
def hello_pipeline():
    mensagem = hello_world()
    exibe_mensagem(mensagem)