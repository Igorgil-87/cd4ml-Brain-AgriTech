from cd4ml.filenames import get_problem_files
import pandas as pd
import time

# Função para log do tempo
def log_tempo(inicio, mensagem):
    print(f"{mensagem} - Tempo decorrido: {time.time() - inicio:.2f} segundos")

# Função para realizar o download e processamento
def download(use_cache=True):
    """
    Função para carregar e processar os dados necessários para o problema de rendimento.
    """
    # Obter os arquivos relacionados ao problema "rendimento"
    file_names = get_problem_files("rendimento")

    # Carregar dados de ranking de valores
    inicio = time.time()
    ranking_valores = pd.read_csv(file_names['ranking_valores'])
    ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
    ranking_valores['Valor da Produção Total'] = ranking_valores['Valor da Produção Total'] \
        .astype(str).str.replace('.', '').astype(float)
    log_tempo(inicio, "Dados do ranking carregados e processados")

    # Carregar dados do IBGE
    inicio = time.time()
    dados_ibge = {
        "Milho": {"Área colhida (ha)": 13767431, "Rendimento médio (kg/ha)": 3785, "Quantidade produzida (t)": 52112217},
        "Soja": {"Área colhida (ha)": 20565279, "Rendimento médio (kg/ha)": 2813, "Quantidade produzida (t)": 57857172},
        "Trigo": {"Área colhida (ha)": 1853224, "Rendimento médio (kg/ha)": 2219, "Quantidade produzida (t)": 4114057},
        "Arroz": {"Área colhida (ha)": 2890926, "Rendimento médio (kg/ha)": 3826, "Quantidade produzida (t)": 11060741},
    }
    dados_ibge_df = pd.DataFrame.from_dict(dados_ibge, orient='index').reset_index()
    dados_ibge_df.rename(columns={'index': 'Cultura'}, inplace=True)
    log_tempo(inicio, "Dados do IBGE carregados")

    # Combinar todos os arquivos transformados
    inicio = time.time()
    arquivos_transformados = [
        file_names['milho_transformado'],
        file_names['soja_transformado'],
        file_names['trigo_transformado'],
        file_names['arroz_transformado']
    ]
    dados_combinados = pd.concat([pd.read_csv(arquivo) for arquivo in arquivos_transformados])
    log_tempo(inicio, "Todos os arquivos transformados combinados")

    # Retornar os datasets carregados
    return ranking_valores, dados_ibge_df, dados_combinados