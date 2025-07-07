from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_insumos = Blueprint('insumos', __name__, template_folder='../../templates')

@bp_insumos.route('/insumos', methods=['GET', 'POST'])
def insumos_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("insumos", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Otimização de Insumos": 0.89,
        "Custo Efetivo por Região": 0.86,
        "Eficiência Agronômica": 0.91,
    }

    return render_template("playground/insumos.html", scores=scores, prediction=prediction_result)