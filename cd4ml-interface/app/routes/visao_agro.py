from flask import Blueprint, render_template

bp_visao_agro = Blueprint("visao_agro", __name__)

@bp_visao_agro.route("/visao_agro")
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
                ("otimizacaoInsumo.png", "Otimização de Insumos", "produtividade.otimizacaoInsumo_view"),
                ("pred_rendimento.png", "Predição de Rendimento", "produtividade.pred_rendimento_view")
            ],
            "Socioambiental": [
                ("solo.png", "Identificação de Bioma", "socioambiental.solo_view"),
                ("incendio.png", "Identificação de focos de incêndio", "socioambiental.incendio_view"),
                ("unidade_conservacao.png", "Consulta de Unidade de Conservação", "socioambiental.unidade_conservacao_view"),
                ("indigina.png", "Consulta de Terra Indígena", "socioambiental.indigina_view")
            ],
            "Logística": [
                ("lavoura.jpg", "Distância da proximidade de rios", "logistica.lavoura_view")
            ],
            "Geográfico": [
                ("car.png", "Consulta Geográfica de Municípios", "geografico.car_view"),
                ("colheita.jpg", "Geração de coordenadas Geodésicas", "geografico.colheita_view")
            ],
            "Imagens": [
                ("agriculture_satellite.jpg", "Imagem de satélite Sentinel", "imagens.sentinel_view")
            ]
    }
    return render_template("visao_agro.html", secoes=secoes)