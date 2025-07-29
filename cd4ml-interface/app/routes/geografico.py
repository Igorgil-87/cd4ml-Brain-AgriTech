from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_geografico = Blueprint('geografico', __name__, template_folder='../../templates')

@bp_geografico.route('/geografico', methods=['GET', 'POST'])
def geografico_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("geografico", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Consulta Geográfica de Municípios": 0.89,
        "Geração de coordenadas Geodésicas": 0.86
    }

    return render_template("playground/geografico.html", scores=scores, prediction=prediction_result)

@bp_geografico.route("/car_geo")
def car_geo_view():
    return render_template("playground/car_geo.html")

@bp_geografico.route("/colheita")
def colheita_view():
    return render_template("playground/colheita.html")
