import pytest
from cd4ml.problems.rendimento.readers.stream_data import process_row, read_schema_file, stream_raw
from unittest.mock import patch, mock_open, MagicMock
import json
from pathlib import Path
import logging
import sys
from io import StringIO
import pandas as pd





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




from io import StringIO
import pandas as pd
import pytest
from cd4ml.problems.rendimento.readers.stream_data import stream_raw

def test_stream_raw(monkeypatch):
    # Simula o conteúdo do CSV como string
    mock_csv = StringIO("""safra,cultura,valor,split,grupo,municipio,data,Valor da Produção Total,Área colhida (ha),clima,solo,uf,decenio,outros_manejos
2023,Milho,123.4,train,Agrícola,São Paulo,2023-05-01,456.7,789.1,Seco,Arenoso,SP,1,Manejo X
""")

    # Monkeypatch para substituir pandas.read_csv sempre que chamado dentro do stream_raw
    monkeypatch.setattr("pandas.read_csv", lambda *args, **kwargs: pd.read_csv(mock_csv))

    # Executa o código testado sem depender do arquivo físico
    rows = list(stream_raw("rendimento"))
    assert len(rows) > 0

def test_read_schema_file():
    categorical, numerical = read_schema_file("dummy_path")  # força fallback
    assert "safra" in categorical
    assert "clima" in categorical
    assert "valor" in numerical