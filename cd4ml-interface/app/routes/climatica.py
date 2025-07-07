from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_climatica = Blueprint('climatica', __name__, template_folder='../../templates')

@bp_climatica.route('/climatica', methods=['GET', 'POST'])
def climatica_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("climatica", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Análise de Clima para Lavouras": 0.91,
        "Histórico de Temperatura no Campo": 0.87,
        "Previsão do Tempo para Safra": 0.93,
    }

    return render_template("playground/climatica.html", scores=scores, prediction=prediction_result)
