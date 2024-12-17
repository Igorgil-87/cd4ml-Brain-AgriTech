import pytest
import os
from cd4ml.problems.rendimento.readers.stream_data import stream_data, process_row, stream_raw
from pathlib import Path
import json

# Caminho para o schema raw
RAW_SCHEMA_PATH = Path(Path(__file__).parent, "../readers/raw_schema.json")

@pytest.fixture
def schema():
    with open(RAW_SCHEMA_PATH, "r") as file:
        return json.load(file)

def test_stream_raw():
    """Testa se o stream_raw retorna linhas corretamente."""
    rows = list(stream_raw("rendimento"))
    assert len(rows) > 0, "O stream_raw não retornou nenhuma linha"
    assert "Cultura" in rows[0], "Coluna 'Cultura' não encontrada nos dados brutos"

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