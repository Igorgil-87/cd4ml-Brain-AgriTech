import pytest
from cd4ml.problems.rendimento.readers.stream_data import process_row, read_schema_file
from unittest.mock import patch, mock_open
import json
from pathlib import Path
from cd4ml.problems.rendimento.readers.stream_data import stream_raw, read_schema_file
from unittest.mock import patch, mock_open, MagicMock  # Importe MagicMock aqui
import json

RAW_SCHEMA_PATH = Path(__file__).parent / "../readers/raw_schema.json"

@pytest.fixture
def schema():
    mock_schema_content = """
{
  "categorical": ["safra", "cultura", "uf", "municipio", "grupo", "solo", "outros_manejos", "clima", "decenio", "data"],
  "numerical": ["valor", "Valor da Produção Total", "Área colhida (ha)"]
}
"""
    with patch('builtins.open', mock_open(read_data=mock_schema_content)):
        categorical, numerical = read_schema_file(RAW_SCHEMA_PATH)
        return categorical, numerical

def test_process_row(schema):
    """Testa a função process_row."""
    categorical_fields, numeric_fields = schema
    raw_row = {"cat1": "A", "num1": "1.23", "unknown": "X",
               "safra": "2023", "cultura": "Milho", "uf": "GO", "municipio": "Rio Verde",
               "grupo": "G1", "solo": "ST", "outros_manejos": "OM", "clima": "Tropical",
               "decenio": "1", "data": "2023-01-01", "valor": "1000",
               "Valor da Produção Total": "500000", "Área colhida (ha)": "100"}
    processed = process_row(raw_row, categorical_fields, numeric_fields)
    assert processed["safra"] == "2023"
    assert processed["valor"] == 1000.0
    assert "unknown" not in processed

from cd4ml.problems.rendimento.readers.stream_data import stream_raw, read_schema_file
from unittest.mock import patch, mock_open, MagicMock
import json

def test_stream_raw():
    """Testa a função stream_raw mockando a leitura do arquivo."""
    mock_schema = {"categorical": ["cultura"], "numerical": ["valor"], "split_value": "float64"}
    mock_file = mock_open(read_data=json.dumps(mock_schema))

    @patch('builtins.open', mock_file)
    @patch('cd4ml.problems.rendimento.readers.stream_data.pd.read_csv', return_value=iter([
        {'safra': '2023', 'cultura': 'Milho', 'valor': '10.0', 'split': '0.2'},
        {'safra': '2024', 'cultura': 'Soja', 'valor': '20.0', 'split': '0.9'},
    ]))
    def _test(mock_open_builtin, mock_read_csv):
        rows = list(stream_raw("rendimento"))
        assert len(rows) > 0
        assert isinstance(rows[0], dict)
        assert 'split_value' in rows[0]

    _test()

def test_read_schema_file():
    """Testa a função read_schema_file."""
    mock_schema_content = '{"categorical": ["cat1", "cat2"], "numerical": ["num1", "num2"]}'
    with patch('builtins.open', mock_open(read_data=mock_schema_content)):
        categorical, numerical = read_schema_file("dummy_path")
        assert categorical == ["cat1", "cat2"]
        assert numerical == ["num1", "num2"]