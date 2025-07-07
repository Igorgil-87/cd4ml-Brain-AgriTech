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