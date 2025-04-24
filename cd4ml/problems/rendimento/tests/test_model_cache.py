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
            MagicMock(info=MagicMock(run_id="789"))
        ]

        available_models = cache.list_available_models_from_ml_flow()
        assert "rendimento" in available_models
        assert len(available_models["rendimento"]) == 1
        assert available_models["rendimento"][0]['run_id'] == "789"