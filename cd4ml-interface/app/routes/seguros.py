from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_seguros = Blueprint('seguros', __name__, template_folder='../../templates')

@bp_seguros.route('/seguros', methods=['GET', 'POST'])
def seguros_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("seguros", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Embargos Ambientais (Ibama)": 0.89,
        "Consulta CAR/INCRA": 0.84,
        "Score de Governança": 0.91,
        "Trabalho Análogo ao Escravo": 0.86
    }

    return render_template("playground/seguros.html", scores=scores, prediction=prediction_result)


@bp_seguros.route("/incra")
def incra_view():
    return render_template("playground/incra.html")

@bp_seguros.route("/car")
def car_view():
    return render_template("playground/car.html")

@bp_seguros.route("/quilombos")
def quilombos_view():
    return render_template("playground/quilombos.html")

@bp_seguros.route("/indigina")
def indigina_view():
    return render_template("playground/indigina.html")

@bp_seguros.route("/unidade_conservacao")
def unidade_conservacao_view():
    return render_template("playground/unidade_conservacao.html")

@bp_seguros.route("/divida_trabalho")
def divida_trabalho_view():
    return render_template("playground/divida_trabalho.html")

@bp_seguros.route("/risco")
def risco_view():
    return render_template("playground/risco.html")

@bp_seguros.route("/IBAMA")
def ibama_view():
    return render_template("playground/ibama.html")

@bp_seguros.route("/penalizacao")
def penalizacao_view():
    return render_template("playground/penalizacao.html")

@bp_seguros.route("/geodesica")
def geodesica_view():
    return render_template("playground/geodesica.html")

@bp_seguros.route("/incendio")
def incendio_view():
    return render_template("playground/incendio.html")

@bp_seguros.route("/score_gove")
def score_gove_view():
    return render_template("playground/score_gove.html")