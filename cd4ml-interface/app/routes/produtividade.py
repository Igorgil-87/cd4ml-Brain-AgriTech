from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_produtividade = Blueprint('produtividade', __name__, template_folder='../../templates')

@bp_produtividade.route('/produtividade', methods=['GET', 'POST'])
def produtividade_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("produtividade", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Composição do uso do solo": 0.90,
        "Produtividade histórica da safra": 0.88,
        "Predição de Rendimento": 0.93,
    }

    return render_template("playground/produtividade.html", scores=scores, prediction=prediction_result)


@bp_produtividade.route("/solo")
def solo_view():
    return render_template("playground/solo.html")

@bp_produtividade.route("/ndvi")
def ndvi_view():
    return render_template("playground/ndvi.html")

@bp_produtividade.route("/safrahistorica")
def safrahistorica_view():
    return render_template("playground/safrahistorica.html")

@bp_produtividade.route("/otimizacaoInsumo")
def otimizacao_insumo_view():
    return render_template("playground/otimizacaoInsumo.html")

@bp_produtividade.route("/pred_rendimento")
def pred_rendimento_view():
    return render_template("playground/pred_rendimento.html")

@bp_produtividade.route("/penalizacao")
def penalizacao_view():
    return render_template("playground/penalizacao.html")