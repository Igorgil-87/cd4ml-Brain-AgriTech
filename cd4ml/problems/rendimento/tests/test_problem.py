import pytest
from cd4ml.problems.rendimento.problem import Problem
from cd4ml.utils.utils import get_uuid

import pytest
from cd4ml.problems.rendimento.problem import Problem
from cd4ml.utils.utils import get_uuid
from unittest.mock import MagicMock

@pytest.fixture
def problem_instance():
    """Cria uma instância do problema 'rendimento' com feature_set mockado."""
    problem = Problem(
        problem_name="rendimento",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
    )
    mock_feature_set = MagicMock()
    mock_feature_set.info = {"date_lookup": {}}
    problem.feature_set = mock_feature_set
    return problem

def test_problem_initialization(problem_instance):
    """Testa a inicialização da classe Problem."""
    assert problem_instance.problem_name == "rendimento", "Falha na inicialização do problema"
    assert problem_instance.model_id is not None, "model_id não foi inicializado corretamente"

def test_download_data(problem_instance, mocker):
    """Testa se o método download_data chama a função de download corretamente."""
    mock_download = mocker.patch("cd4ml.problems.rendimento.download_data.download_data.download")
    problem_instance.download_data()
    mock_download.assert_called_once_with("rendimento")

def test_prepare_feature_data(problem_instance):
    """Testa se o método prepare_feature_data executa sem erros."""
    problem_instance.prepare_feature_data()
    assert problem_instance.feature_set.info["date_lookup"] is not None, "Falha ao preparar 'date_lookup'"

def test_training_and_validation_stream(problem_instance, mocker):
    """Testa os streams de treino e validação."""
    problem_instance.ml_pipeline_params = {'splitting': {'training_random_start': 0.0, 'training_random_end': 0.7, 'validation_random_start': 0.7, 'validation_random_end': 1.0}}
    mock_stream_processed = mocker.patch.object(problem_instance, "stream_processed", return_value=iter([
        {"split_value": 0.1},  # Para treino
        {"split_value": 0.8},  # Para validação
    ]))
    training_data = list(problem_instance.training_stream())
    validation_data = list(problem_instance.validation_stream())

    assert len(training_data) > 0, "Training stream está vazio"
    assert len(validation_data) > 0, "Validation stream está vazio"

def test_run_all(problem_instance, mocker):
    """Testa a execução completa do pipeline do problema."""
    mocker.patch.object(problem_instance, "download_data")
    mocker.patch.object(problem_instance, "get_encoder")
    mocker.patch.object(problem_instance, "train")
    mocker.patch.object(problem_instance, "validate")

    problem_instance.run_all()

    problem_instance.download_data.assert_called_once()
    problem_instance.get_encoder.assert_called_once()
    problem_instance.train.assert_called_once()
    problem_instance.validate.assert_called_once()