import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
import mlflow
import pandas as pd
import requests_mock
from cd4ml.webapp.model_cache import ModelCache


class TestModelCache:
    @classmethod
    def setup_class(cls):
        uri_ = "http://test-tracking-uri:8080"
        mlflow.set_tracking_uri(uri_)
        os.environ["MLFLOW_TRACKING_URL"] = "http://test-tracking-uri:8080"

    def test_is_latest_deployable_model(self):
        row = {
            "ml_pipeline_params_name": 'default',
            "feature_set_name": 'default',
            "algorithm_name": 'default',
            "algorithm_params_name": 'default',
            "passed_acceptance_test": 'yes'
        }
        assert ModelCache.is_latest_deployable_model(row)

    def test_list_models_for_rendimento(self):
        cache = ModelCache()

        def get_search_return_values(*args, **kwargs):
            return pd.DataFrame([{
                'run_id': "789",
                'tags.mlflow.runName': 'rendimento_run',
                'params.MLPipelineParamsName': 'default',
                'params.FeatureSetName': 'default',
                'params.AlgorithmName': 'random_forest',
                'tags.DidPassAcceptanceTest': 'yes',
                'end_time': datetime(2024, 3, 25, 12, 0, 0)
            }])

        mlflow.search_runs = MagicMock(side_effect=get_search_return_values)
        available_models = cache.list_available_models_from_ml_flow()
        assert len(available_models["rendimento"]) == 1
        assert available_models["rendimento"][0]['run_id'] == "789"

    def test_download_and_save_rendimento_model(self, tmp_path):
        saving_path = Path(tmp_path, "full_model.pkl")
        with requests_mock.Mocker() as mocked_req:
            mocked_req.get("http://test-tracking-uri:8080/get-artifact?path=full_model.pkl&run_uuid=789",
                           content=b"Mocked model data")
            ModelCache.download_and_save_from_ml_flow(saving_path, "789")
            assert saving_path.read_bytes() == b"Mocked model data"