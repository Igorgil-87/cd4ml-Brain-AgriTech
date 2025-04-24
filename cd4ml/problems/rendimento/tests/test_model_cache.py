import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import mlflow
import pandas as pd
import requests_mock
from cd4ml.webapp.model_cache import ModelCache


class TestModelCache:
    @classmethod
    def setup_class(cls):
        os.environ["MLFLOW_TRACKING_URL"] = "http://test-tracking-uri:8080"
        mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URL"])

    def test_is_latest_deployable_model(self):
        row = {
            "ml_pipeline_params_name": 'default',
            "feature_set_name": 'default',
            "algorithm_name": 'default',
            "algorithm_params_name": 'default',
            "passed_acceptance_test": 'yes'
        }
        assert ModelCache.is_latest_deployable_model(row)

    @patch("mlflow.tracking.MlflowClient.search_runs")
    @patch("mlflow.tracking.MlflowClient.get_experiment_by_name")
    def test_list_models_for_rendimento(self, mock_get_experiment_by_name, mock_search_runs):
        cache = ModelCache()

        mock_experiment = MagicMock()
        mock_experiment.experiment_id = "1"
        mock_get_experiment_by_name.return_value = mock_experiment

        mock_search_runs.return_value = [
            MagicMock(info=MagicMock(run_id="789", start_time=datetime(2024, 3, 25, 12, 0, 0).timestamp() * 1000),
                      data=MagicMock(params={"MLPipelineParamsName": "default", "FeatureSetName": "default", "AlgorithmName": "random_forest", "AlgorithmParamsName": "default"},
                                      tags={"DidPassAcceptanceTest": "yes", "mlflow.runName": "rendimento_run"}))
        ]

        available_models = cache.list_available_models_from_ml_flow()
        assert "rendimento" in available_models
        assert len(available_models["rendimento"]) == 1
        assert available_models["rendimento"][0]['run_id'] == "789"

    def test_download_and_save_rendimento_model(self, tmp_path):
        saving_path = Path(tmp_path, "full_model.pkl")
        with requests_mock.Mocker() as mocked_req:
            mocked_req.get(f"{mlflow.get_tracking_uri()}/get-artifact?path=full_model.pkl&run_uuid=some_run_id",
                           content=b"Mocked model data")
            ModelCache.download_and_save_from_ml_flow(saving_path, "some_run_id")
            assert saving_path.read_bytes() == b"Mocked model data"