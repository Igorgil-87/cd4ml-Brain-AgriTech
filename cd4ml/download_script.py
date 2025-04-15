def download(problem_name):
    def generator():
        yield {
            "Cultura": "soja",
            "Área colhida (ha)": 1000,
            "Valor da Produção Total": 500000,
            "Rendimento médio (kg/ha)": 500
        }
    return generator