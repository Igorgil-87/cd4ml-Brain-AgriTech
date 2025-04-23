import mlflow
import os

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URL", "http://mlflow:5000")
PROBLEM_NAME = os.environ.get("PROBLEM_NAME", "rendimento")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def check_for_new_production_model():
    experiment = mlflow.get_experiment_by_name(PROBLEM_NAME)
    if experiment is None:
        print(f"Experiment '{PROBLEM_NAME}' not found in MLflow.")
        return None

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.DidPassAcceptanceTest = 'yes'",
        order_by=["end_time DESC"],
        max_results=1
    )

    if runs and len(runs) > 0:
        run_id = runs.iloc[0].run_id
        print(f"Found a new production model with run_id: {run_id}")
        return run_id
    else:
        print("No new production model found in MLflow.")
        return None

if __name__ == "__main__":
    check_for_new_production_model()