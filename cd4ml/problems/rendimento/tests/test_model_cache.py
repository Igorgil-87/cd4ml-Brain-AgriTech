import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
import mlflow
import pandas as pd
import requests_mock
from cd4ml.webapp.model_cache import ModelCache
from mlflow.tracking.mock import mock_tracking_server


class TestModelCache:
    @classmethod
    def setup_class(cls):
        cls.mock_server = mock_tracking_server()
        os.environ["MLFLOW_TRACKING_URL"] = cls.mock_server.uri
        mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URL"])

    @classmethod
    def teardown_class(cls):
        cls.mock_server.stop()

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
        with mlflow.start_run(run_name="rendimento_run"):
            mlflow.log_param("MLPipelineParamsName", "default")
            mlflow.log_param("FeatureSetName", "default")
            mlflow.log_param("AlgorithmName", "random_forest")
            mlflow.set_tag("DidPassAcceptanceTest", "yes")
            mlflow.set_tag("BuildNumber", "123")
            end_time = datetime(2024, 3, 25, 12, 0, 0).timestamp()
            mlflow.end_run()
            run_id = mlflow.active_run().info.run_uuid

        available_models = cache.list_available_models_from_ml_flow()
        assert "rendimento" in available_models
        assert len(available_models["rendimento"]) >= 1
        found = False
        for model in available_models["rendimento"]:
            if model['run_id'] == run_id:
                assert model['ml_pipeline_params_name'] == 'default'
                assert model['feature_set_name'] == 'default'
                assert model['algorithm_name'] == 'random_forest'
                assert model['passed_acceptance_test'] == 'yes'
                found = True
                break
        assert found

    def test_download_and_save_rendimento_model(self, tmp_path):
        # Este teste pode precisar de uma adaptação se você realmente precisa simular o download.
        # Por enquanto, vamos mantê-lo como estava, assumindo que a conexão MLflow está funcionando.
        saving_path = Path(tmp_path, "full_model.pkl")
        with requests_mock.Mocker() as mocked_req:
            mocked_req.get(f"{mlflow.get_tracking_uri()}/get-artifact?path=full_model.pkl&run_uuid=some_run_id",
                           content=b"Mocked model data")
            ModelCache.download_and_save_from_ml_flow(saving_path, "some_run_id")
            assert saving_path.read_bytes() == b"Mocked model data"