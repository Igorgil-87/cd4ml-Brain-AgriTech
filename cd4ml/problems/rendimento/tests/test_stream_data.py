import pytest
import os
from cd4ml.problems.rendimento.readers.stream_data import stream_data, process_row, stream_raw
from pathlib import Path
import json
from cd4ml.problems.rendimento.readers.stream_data import stream_raw
from unittest.mock import patch


# Caminho para o schema raw
RAW_SCHEMA_PATH = Path(Path(__file__).parent, "../readers/raw_schema.json")

@pytest.fixture
def schema():
    with open(RAW_SCHEMA_PATH, "r") as file:
        return json.load(file)



def test_stream_raw():
    """Testa a função stream_raw mockando a leitura do arquivo."""
    @patch('cd4ml.problems.rendimento.readers.stream_data.pd.read_csv')
    @patch('cd4ml.problems.rendimento.readers.stream_data.os.path.exists', return_value=True)
    @patch('cd4ml.problems.rendimento.readers.stream_data.open', create=True)
    def _test(mock_open, mock_exists, mock_read_csv):
        mock_read_csv.return_value = iter([
            {'safra': '2023', 'cultura': 'Milho', 'valor': 10.0, 'split': 0.2},
            {'safra': '2024', 'cultura': 'Soja', 'valor': 20.0, 'split': 0.9},
        ])
        rows = list(stream_raw("rendimento"))
        assert len(rows) > 0
        assert isinstance(rows[0], dict)

    _test()

def test_process_row(schema):
    """Testa se a função process_row processa os dados corretamente."""
    raw_row = {
        "Cultura": "Milho",
        "lot_size_sf": "1000",
        "price": "60000"
    }
    processed_row = process_row(raw_row, schema["categorical"], schema["numerical"])
    assert processed_row["Cultura"] == "Milho", "Falha ao processar coluna categórica"
    assert processed_row["lot_size_sf"] == 1000.0, "Falha ao converter coluna numérica"
    assert processed_row["price"] == 60000, "Falha no tratamento do campo 'price'"

def test_stream_data(schema):
    """Testa se o stream_data aplica o schema corretamente."""
    processed_rows = list(stream_data("rendimento"))
    assert len(processed_rows) > 0, "O stream_data não retornou nenhuma linha processada"
    for row in processed_rows:
        assert "Cultura" in row, "Campo 'Cultura' não encontrado"
        assert isinstance(row["lot_size_sf"], float), "Coluna numérica não foi convertida corretamente"