from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_saude = Blueprint('saude', __name__, template_folder='../../templates')

@bp_saude.route('/saude', methods=['GET', 'POST'])
def saude_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("saude", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Índice NDVI": 0.92,
        "Saúde do Solo": 0.88,
        "Análise Climática Integrada": 0.91,
    }

    return render_template("playground/saude.html", scores=scores, prediction=prediction_result)