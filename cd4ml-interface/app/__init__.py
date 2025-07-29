from flask import Flask, render_template

# Importa blueprints
from app.routes.climatica import bp_climatica
from app.routes.seguros import bp_seguros
from app.routes.produtividade import bp_produtividade
from app.routes.socioambiental import bp_socioambiental
from app.routes.logistica import bp_logistica
from app.routes.geografico import bp_geografico
from app.routes.imagens import bp_imagens

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Registro de rotas (blueprints)
    app.register_blueprint(bp_climatica)
    app.register_blueprint(bp_seguros)
    app.register_blueprint(bp_produtividade)
    app.register_blueprint(bp_socioambiental)
    app.register_blueprint(bp_logistica)
    app.register_blueprint(bp_geografico)
    app.register_blueprint(bp_imagens)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/visao_agro")
    def visao_agro():
        secoes = {
            "Climática": [
                ("analise_clima.png", "Análise de Clima para Lavouras", "climatica.analise_clima_view"),
                ("safrahistorica.png", "Histórico de Temperatura no campo", "climatica.safrahistorica_view"),
                ("clima_lavoura.png", "Previsão do tempo para safra", "climatica.clima_lavoura_view")
            ],
            "Seguros": [
                ("incra.png", "Consulta Base Fundiária do Incra", "seguros.incra_view"),
                ("car.png", "Consulta Car", "seguros.car_view"),
                ("quilombos.png", "Consulta de Quilombola", "seguros.quilombos_view"),
                ("indigina.png", "Consulta de Terra Indígena", "seguros.indigina_view"),
                ("unidade_conservacao.png", "Consulta de Unidade de Conservação", "seguros.unidade_conservacao_view"),
                ("divida_trabalho.png", "Consulta Dívida Trabalhista", "seguros.divida_trabalho_view"),
                ("risco.png", "Consulta Grau de Risco (Pessoa Física)", "seguros.risco_view"),
                ("IBAMA.png", "Embargos Ambientais (Ibama)", "seguros.ibama_view"),
                ("penalizacao.png", "Estimativa de Penalização de Produtividade", "seguros.penalizacao_view"),
                ("geodesica.png", "Geração de coordenadas Geodésicas", "seguros.geodesica_view"),
                ("incendio.png", "Identificação de focos de incêndio", "seguros.incendio_view"),
                ("score_gove.png", "Score de Governança", "seguros.score_gove_view")
            ],
            "Produtividade": [
                ("solo.png", "Composição do uso do solo", "produtividade.solo_view"),
                ("penalizacao.png", "Estimativa de Penalização de Produtividade", "produtividade.penalizacao_view"),
                ("ndvi.png", "Indice de vegetação NDVI", "produtividade.ndvi_view"),
                ("safrahistorica.png", "Produtividade histórica da safra", "produtividade.safrahistorica_view"),
                ("otimizacaoInsumo.png", "Otimização de Insumos", "produtividade.otimizacao_insumo_view"),
                ("pred_rendimento.png", "Predição de Rendimento", "produtividade.pred_rendimento_view")
            ],
            "Socioambiental": [
                ("solo.png", "Identificação de Bioma", "socioambiental.bioma_view"),
                ("incendio.png", "Identificação de focos de incêndio", "socioambiental.incendio_socio_view"),
                ("unidade_conservacao.png", "Consulta de Unidade de Conservação", "socioambiental.unidade_conservacao_socio_view"),
                ("indigina.png", "Consulta de Terra Indígena", "socioambiental.indigina_socio_view")
            ],
            "Logística": [
                ("lavoura.jpg", "Distância da proximidade de rios", "logistica.lavoura_view")
            ],
            "Geográfico": [
                ("car.png", "Consulta Geográfica de Municípios", "geografico.car_geo_view"),
                ("colheita.jpg", "Geração de coordenadas Geodésicas", "geografico.colheita_view")
            ],
            "Imagens": [
                ("agriculture_satellite.jpg", "Imagem de satélite Sentinel", "imagens.satellite_view")
            ]
        }
        return render_template("visao_agro.html", secoes=secoes)

    print("\n==== Rotas Registradas ====")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:35s} => {rule.rule}")
    print("==== Fim das Rotas ====\n")


    return app