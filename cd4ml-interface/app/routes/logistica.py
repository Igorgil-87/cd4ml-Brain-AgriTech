from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_logistica = Blueprint('logistica', __name__, template_folder='../../templates')

@bp_logistica.route('/logistica', methods=['GET', 'POST'])
def logistica_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("logistica", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Distância da Proximidade de Rios": 0.88
    }

    return render_template("playground/logistica.html", scores=scores, prediction=prediction_result)

@bp_logistica.route("/lavoura")
def lavoura_view():
    return render_template("playground/lavoura.html")