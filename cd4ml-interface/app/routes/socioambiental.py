from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_socioambiental = Blueprint('socioambiental', __name__, template_folder='../../templates')

@bp_socioambiental.route('/socioambiental', methods=['GET', 'POST'])
def socioambiental_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("socioambiental", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Identificação de Bioma": 0.89,
        "Consulta de Unidade de Conservação": 0.86,
        "Consulta de Terra Indígena": 0.91
    }

    return render_template("playground/socioambiental.html", scores=scores, prediction=prediction_result)


@bp_socioambiental.route("/bioma")
def bioma_view():
    return render_template("playground/bioma.html")

@bp_socioambiental.route("/incendio_socio")
def incendio_socio_view():
    return render_template("playground/incendio_socio.html")

@bp_socioambiental.route("/unidade_conservacao_socio")
def unidade_conservacao_socio_view():
    return render_template("playground/unidade_conservacao_socio.html")

@bp_socioambiental.route("/indigina_socio")
def indigina_socio_view():
    return render_template("playground/indigina_socio.html")