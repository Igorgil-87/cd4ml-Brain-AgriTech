from flask import Blueprint, render_template, request
from app.mlflow_client import load_model, predict

bp_imagens = Blueprint('imagens', __name__, template_folder='../../templates')

@bp_imagens.route('/imagens', methods=['GET', 'POST'])
def imagens_view():
    prediction_result = None
    if request.method == 'POST':
        input_data = request.form.to_dict()
        model = load_model("imagens", stage="Production")
        prediction_result = predict(model, input_data)

    scores = {
        "Imagem de satélite Sentinel": 0.92
    }

    return render_template("playground/imagens.html", scores=scores, prediction=prediction_result)


@bp_imagens.route("/satellite")
def satellite_view():
    return render_template("playground/satellite.html")
