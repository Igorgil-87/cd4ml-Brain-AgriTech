from dagster import op

@op
def hello_world():
    print("🚀 Rodando op: hello_world")
    return "Hello from Dagster!"

@op
def exibe_mensagem(mensagem: str):
    print(f"📣 Mensagem recebida: {mensagem}")