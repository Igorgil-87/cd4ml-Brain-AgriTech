from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_producao = Blueprint('producao', __name__, template_folder='../../templates')

@bp_producao.route('/producao', methods=['GET', 'POST'])
def producao_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("producao", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Predição de Rendimento": 0.94,
        "Produtividade Histórica": 0.90,
        "Estimativa de Penalização": 0.88,
    }

    return render_template("playground/producao.html", scores=scores, prediction=prediction_result)