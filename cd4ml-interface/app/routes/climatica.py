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

    return render_template("playground/climatica.html", prediction=prediction_result, api_key="abc123xyz456")

@bp_climatica.route("/analise_clima")
def analise_clima_view():
    return render_template("playground/analise_clima.html")

@bp_climatica.route("/safrahistorica")
def safrahistorica_view():
    return render_template("playground/safrahistorica.html")

@bp_climatica.route("/clima_lavoura")
def clima_lavoura_view():
    return render_template("playground/clima_lavoura.html")