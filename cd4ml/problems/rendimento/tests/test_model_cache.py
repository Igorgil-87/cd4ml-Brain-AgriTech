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

    @patch.object(ModelCache, 'list_available_models_from_ml_flow')
    def test_list_models_for_rendimento(self, mock_list_available_models):
        cache = ModelCache()
        mock_list_available_models.return_value = {
            "rendimento": [{"run_id": "789",
                            "ml_pipeline_params_name": 'default',
                            "feature_set_name": 'default',
                            "algorithm_name": 'random_forest',
                            "tags.DidPassAcceptanceTest": 'yes'}]
        }
        available_models = cache.list_available_models_from_ml_flow()
        assert "rendimento" in available_models
        assert len(available_models["rendimento"]) == 1
        assert available_models["rendimento"][0]['run_id'] == "789"