from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/visao_agro')
def visao_agro():
    secoes = {
        "Climática": [
            ("analise_clima.png", "Análise de Clima para Lavouras"),
            ("safrahistorica.png", "Histórico de Temperatura no campo"),
            ("clima_lavoura.png", "Previsão do tempo para safra")
        ],
        "Seguros": [
            ("incra.png", "Consulta Base Fundiária do Incra"),
            ("car.png", "Consulta Car"),
            ("quilombos.png", "Consulta de Quilombola"),
            ("indigina.png", "Consulta de Terra Indígena"),
            ("unidade_conservacao.png", "Consulta de Unidade de Conservação"),
            ("divida_trabalho.png", "Consulta Dívida Trabalhista"),
            ("risco.png", "Consulta Grau de Risco (Pessoa Física)"),
            ("IBAMA.png", "Embargos Ambientais (Ibama)"),
            ("penalizacao.png", "Estimativa de Penalização de Produtividade"),
            ("geodesica.png", "Geração de coordenadas Geodésicas"),
            ("incendio.png", "Identificação de focos de incêndio"),
            ("score_gove.png", "Score de Governança"),
            ("divida_trabalho.png", "Trabalho Análogo ao Escravo")
        ],
        "Produtividade": [
            ("solo.png", "Composição do uso do solo"),
            ("penalizacao.png", "Estimativa de Penalização de Produtividade"),
            ("ndvi.png", "Indice de vegetação NDVI"),
            ("safrahistorica.png", "Produtividade histórica da safra"),
            ("otimizacaoInsumo.png", "Otimização de Insumos"),
            ("pred_rendimento.png", "Predição de Rendimento")
        ],
        "Socioambiental": [
            ("solo.png", "Identificação de Bioma"),
            ("incendio.png", "Identificação de focos de incêndio"),
            ("unidade_conservacao.png", "Consulta de Unidade de Conservação"),
            ("indigina.png", "Consulta de Terra Indígena")
        ],
        "Logística": [
            ("lavoura.jpg", "Distância da proximidade de rios")
        ],
        "Geográfico": [
            ("car.png", "Consulta Geográfica de Municípios"),
            ("colheita.jpg", "Geração de coordenadas Geodésicas")
        ],
        "Imagens": [
            ("agriculture_satellite.jpg", "Imagem de satélite Sentinel")
        ]
    }
    return render_template("visao_agro.html", secoes=secoes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)