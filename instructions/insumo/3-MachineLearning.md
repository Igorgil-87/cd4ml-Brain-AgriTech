# Instruções para Executar o Pipeline de Machine Learning (ML)

## Executar o Pipeline com Diferentes Parâmetros de Modelo

### Objetivos

- Executar o pipeline em Python localmente.
- Fazer alterações nos parâmetros do modelo e observar os efeitos.

---

## Executar os Testes Localmente

Se quiser rodar o pipeline localmente, siga este guia. Caso prefira usar o Jenkins, pode pular esta etapa. O uso do Jenkins requer o commit e push das alterações no código.

1. Execute os testes:
   ```bash
   ./run_tests.sh


## 32 passed, 2 skipped in 5.73 seconds


2.	O flake8 verifica aderência às diretrizes de estilo PEP8. IDEs como PyCharm ajudam a identificar esses erros enquanto você digita. Caso prefira, você pode desativar o flake8 no script run_tests.sh.
3.	Ative o ambiente virtual:

source .venv/bin/activate

4.	Execute o pipeline:
python3 run_python_script.py pipeline
{'r2_score': 0.678401327984714}


5.	Para habilitar o profiler e identificar gargalos de desempenho, use:
python3 run_python_script.py pipeline -p
	•	Analise o arquivo gerado com o snakeviz:
snakeviz pipeline.prof



Alterar Parâmetros do Modelo

	1.	Abra o arquivo cd4ml/ml_model_params.py:
	•	Altere o valor de n_estimators de 10 para um número maior, como 100.
	•	Este parâmetro define o número de árvores na floresta. Valores maiores geralmente melhoram as métricas até certo ponto, mas aumentam o tempo de execução e uso de memória.
	2.	Após a alteração:
	•	Execute localmente o pipeline novamente:

python3 run_python_script.py pipeline



	•	Ou faça o commit e push para executar pelo Jenkins:
git commit . -m "Change to 100 trees"
git pull -r
git push

## Configurar o ML Flow

	1.	Acesse o MLflow no navegador:
http://localhost:12000/#/
	2.	No menu à esquerda, clique em Experiments e selecione “jenkins” para visualizar os jobs executados pelo servidor Jenkins.
	3.	Cada execução exibe métricas, como o r2_score, associadas ao commit do Git. Isso facilita o rollback para versões anteriores do modelo.


## Estrutura do Código

## Estratégia de Configuração

	•	Existem dois arquivos principais para configuração: pipeline_params.py e ml_model_params.py.
	•	O objeto de configuração é criado uma única vez no início do pipeline (em scripts/pipeline.py) e passado para outras funções. Isso garante controle programático completo e evita inconsistências.Design de Streaming

	•	Os caminhos e nomes dos arquivos são centralizados no arquivo cd4ml/filenames.py para facilitar a manutenção.
	•	O leitor de stream, implementado em cd4ml/read_data.py, atualmente lê arquivos CSV, mas futuramente suportará bancos como PostgreSQL.


    Codificação One-Hot

Foi implementada uma codificação One-Hot personalizada devido às limitações da versão do scikit-learn. As vantagens incluem:
	•	Processamento em streaming.
	•	Persistência fácil, essencial para reprodutibilidade.
	•	Controle sobre o número máximo de níveis codificados para otimizar memória.
	•	Configuração centralizada, permitindo ajustes de hiperparâmetros.


    Melhorias Futuras

	•	O objetivo é continuar aprimorando a base de código, tornando-a útil tanto para aprendizado quanto para projetos reais.
	•	Será dada prioridade à modularidade, permitindo que os componentes sejam rearranjados para diferentes ecossistemas.


    Conclusão

Com essas instruções, você pode configurar, executar e modificar o pipeline de ML localmente ou via Jenkins, explorando as possibilidades oferecidas pelos parâmetros do modelo.


