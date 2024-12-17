import pytest
from cd4ml.problems.rendimento.problem import Problem
from cd4ml.utils.utils import get_uuid

@pytest.fixture
def problem_instance():
    """Cria uma instância do problema 'rendimento'."""
    return Problem(
        problem_name="rendimento",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
    )

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

def test_training_and_validation_stream(problem_instance):
    """Testa os streams de treino e validação."""
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