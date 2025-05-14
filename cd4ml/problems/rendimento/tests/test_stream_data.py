import pytest
from cd4ml.problems.rendimento.readers.stream_data import process_row, read_schema_file, stream_raw
from unittest.mock import patch, mock_open, MagicMock
import json
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

RAW_SCHEMA_PATH = Path(__file__).parent / "../readers/raw_schema.json"

@pytest.fixture
def schema():
    logger.info("Executando fixture schema")
    mock_schema_content = """
{
  "categorical": ["safra", "cultura", "uf", "municipio", "grupo", "solo", "outros_manejos", "clima", "decenio", "data"],
  "numerical": ["valor", "Valor da Produção Total", "Área colhida (ha)"]
}
"""
    with patch('builtins.open', mock_open(read_data=mock_schema_content)):
        categorical, numerical = read_schema_file(RAW_SCHEMA_PATH)
        logger.info(f"Fixture schema retornou: categorical={categorical}, numerical={numerical}")
        return categorical, numerical

def test_process_row(schema):
    """Testa a função process_row."""
    logger.info("Executando test_process_row")
    categorical_fields, numeric_fields = schema
    raw_row = {"cat1": "A", "num1": "1.23", "unknown": "X",
               "safra": "2023", "cultura": "Milho", "uf": "GO", "municipio": "Rio Verde",
               "grupo": "G1", "solo": "ST", "outros_manejos": "OM", "clima": "Tropical",
               "decenio": "1", "data": "2023-01-01", "valor": "1000",
               "Valor da Produção Total": "500000", "Área colhida (ha)": "100"}
    processed = process_row(raw_row, categorical_fields, numeric_fields)
    logger.info(f"test_process_row: raw_row={raw_row}, processed={processed}")
    assert processed["safra"] == "2023"
    assert processed["valor"] == 1000.0
    assert "unknown" not in processed

def test_stream_raw():
    """Testa a função stream_raw mockando a leitura do arquivo."""
    logger.info("Executando test_stream_raw")
    mock_schema = """
{
  "categorical": ["cultura"],
  "numerical": ["valor"],
  "split_value": "float64"
}
"""
    mock_file = mock_open(read_data=json.dumps(mock_schema))
    mock_read_return = MagicMock(return_value=iter([
        {'safra': '2023', 'cultura': 'Milho', 'valor': '10.0', 'split_value': '0.2'},
        {'safra': '2024', 'cultura': 'Soja', 'valor': '20.0', 'split_value': '0.9'},
    ]))

    @patch('builtins.open', mock_file)
    @patch('cd4ml.problems.rendimento.readers.stream_data.pd.read_csv', return_value=mock_read_return)
    def _test(mock_read_csv, mock_open_builtin):
        logger.info("Executando _test")
        logger.info(f"_test: mock_open_builtin={mock_open_builtin}, mock_read_csv={mock_read_csv}")
        rows = list(stream_raw("rendimento"))
        logger.info(f"_test: rows={rows}")
        assert len(rows) > 0
        assert isinstance(rows[0], dict)
        assert 'split_value' in rows[0]

    _test()

def test_read_schema_file():
    """Testa a função read_schema_file."""
    logger.info("Executando test_read_schema_file")
    mock_schema_content = '{"categorical": ["cat1", "cat2"], "numerical": ["num1", "num2"]}'
    with patch('builtins.open', mock_open(read_data=mock_schema_content)):
        categorical, numerical = read_schema_file("dummy_path")
        logger.info(f"test_read_schema_file: categorical={categorical}, numerical={numerical}")
        assert categorical == ["cat1", "cat2"]
        assert numerical == ["num1", "num2"]